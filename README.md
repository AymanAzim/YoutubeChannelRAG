# YouTube Channel RAG

A Retrieval-Augmented Generation app that lets you ask questions about any YouTube channel's content. It fetches video transcripts, indexes them using vector embeddings, and answers your questions using only the channel's actual content — with source links.

Built with Streamlit, OpenAI, ChromaDB, and yt-dlp.

## Screenshots

<!-- Add your screenshots here -->
![Home](screenshots/screenshot1.png) 
![Indexing](screenshots/screenshot2.png)
![indexed](screenshots/screenshot3.png)
![Query Result](screenshots/screenshot4.png) 

## How It Works

1. **Fetch** — Retrieves all video IDs from a YouTube channel using `yt-dlp`
2. **Transcribe** — Downloads transcripts for each video via `youtube-transcript-api`
3. **Chunk & Embed** — Splits transcripts into overlapping chunks and generates embeddings with OpenAI's `text-embedding-3-small`
4. **Store** — Stores embeddings in a ChromaDB vector database
5. **Query** — Finds the most relevant chunks for your question and generates an answer with GPT-4o, citing the source videos

## Setup

### Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)

### Installation

```bash
git clone https://github.com/AymanAzim/YoutubeChannelRAG.git
cd YoutubeChannelRAG
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file or export your key:

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### Run

```bash
streamlit run app.py
```

## Usage

1. Paste a YouTube channel URL (e.g. `https://www.youtube.com/@ChannelName/videos`)
2. Click **Index Channel** and wait for it to finish
3. Ask any question about the channel's content
4. Get an answer with links to the source videos

## Tech Stack

| Component | Tool |
|-----------|------|
| Frontend | Streamlit |
| LLM | OpenAI GPT-4o |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | ChromaDB |
| Transcripts | youtube-transcript-api |
| Video Fetching | yt-dlp |

## License

MIT
