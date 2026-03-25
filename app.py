import os
from typing import List
from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL
from openai import OpenAI
import chromadb

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
chroma_client = chromadb.Client()
try:
    chroma_client.delete_collection(name="youtube_channel")
except Exception:
    pass
collection = chroma_client.create_collection(name="youtube_channel")

def get_channel_video_ids(channel_url: str) -> List[str]:
    # Fetch all video IDs from the YouTube channel
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlistend': 500,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        return [entry['id'] for entry in info['entries']]


ytt_api = YouTubeTranscriptApi()

def get_transcript(video_id: str) -> str:
    # Fetch the transcript for a given video ID
    try:
        transcript = ytt_api.fetch(video_id)
        return " ".join([snippet.text for snippet in transcript.snippets])
    except Exception as e:
        print(f" Failed to get transcript for {video_id}: {e}")
        return None

def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    # Split the transcript into overlapping chunks
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - 50):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def get_embedding(text: str) -> list:
    # Get the embedding for a given text chunk
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def index_channel(channel_url: str):
    # Fetch, transcribe, embed, and store all channel videos
    print(f" Fetching video IDs from channel...")
    video_ids = get_channel_video_ids(channel_url)
    print(f" Found {len(video_ids)} videos")

    indexed = 0
    for video_id in video_ids:
        transcript = get_transcript(video_id)
        if not transcript:
            continue
        chunks = chunk_text(transcript)
        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[f"{video_id}_chunk_{i}"],
                metadatas=[{"video_id": video_id, "url": f"https://www.youtube.com/watch?v={video_id}"}]
            )
        indexed += 1
        print(f" Indexed video {indexed}/{len(video_ids)}: {video_id}")

    print(f"Indexing complete. Total videos indexed: {indexed}")


def query_channel(question: str) -> dict:
    # Search across all indexed videos and generate an answer
    q_embedding = get_embedding(question)
    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=5
    )
    context = "\n\n".join(results['documents'][0])
    sources = [m["url"] for m in results['metadatas'][0]]

    prompt = f"""Answer the question using ONLY the Youtube video transcripts below.
    Include which video(s) the information came from.

    Context:
    {context}
    Question: {question}
    Answer:"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}]
    )
    return {
        "answer": response.choices[0].message.content,
        "sources": list(set(sources))
    }


import streamlit as st

st.title("YouTube Channel RAG")
st.caption("Ask anything across the entire channel")

channel_url = st.text_input("YouTube Channel URL", placeholder="https://www.youtube.com/@channelname/videos")

if st.button("Index Channel") and channel_url:
    with st.spinner("Indexing channel... This may take few minutes."):
        index_channel(channel_url)
    st.success("Channel indexed successfully! Start asking questions.")

question = st.text_input("Ask a question about the channel content")
if st.button("Ask Question") and question:
    with st.spinner("Generating answer..."):
        result = query_channel(question)
    st.write("**Answer:**", result["answer"])
    st.subheader("**Sources:**")
    for url in result["sources"]:
        st.markdown(f"- [{url}]({url})")
