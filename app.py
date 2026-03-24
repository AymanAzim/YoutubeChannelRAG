from openai import OpenAI
import chromadb

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
chroma_client = chromadb.Client()
collection = chroma_client.crate_collection(name="youtube_channel")

def get_channel_video_ids(channel_url: str) -> list[str]:
    # Fetch all video IDs from the YouTube channel 
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlistend': 100,  # Limit to the first 100 videos - increase if needed
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        video_ids = [entry['id'] for entry in info['entries']]
    
def get_transcript(video_id: str) -> str:
    # Fetch the transcript for a given video ID
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([chunk['text'] for chunk in transcript])
    except Exception:
        return "None" # skip videos without transcripts
    
def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    # Split the transcript into overlapping chunks
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - 50):  # 50 words overlap
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
        transcript= get_transcript(video_id)
        if not transcript: 
            continue
        chunks = chunk_text(transcript)
        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[f"{video_id}_chunk_{i}"]
                metadata=[{"video_id": video_id, "url": f"https://www.youtube.com/watch?v={video_id}"}]
            )
        indexed += 1
        print(f" Indexed video  {indexed}/{len(video_ids)}: {video_id}")

    print(f"Indexing complete. Total videos indexed: {indexed}")

index_channel("https://www.youtube.com/@AndrejKarpathy/videos")

