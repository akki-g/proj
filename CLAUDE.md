# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an NBA RAG (Retrieval-Augmented Generation) pipeline project with a PostgreSQL database, Ollama LLM backend, and Angular frontend. The system ingests NBA game data, creates embeddings, and provides a chat interface for answering NBA statistics questions.

## Core Architecture

### Backend RAG Pipeline
- **Ingestion** (`backend/ingest.py`): Loads NBA CSV data into PostgreSQL tables (game_details, player_box_scores, players, teams)
- **Embedding** (`backend/embed.py`): Generates text embeddings using Ollama's `nomic-embed-text` model and stores them in pgvector
- **Retrieval** (`backend/rag.py`): Performs semantic search and generates answers using `llama3.2:3b`
- **API Server** (`backend/server.py`): FastAPI server with `/api/chat` endpoint for real-time queries

### Data Flow
1. CSV files → PostgreSQL tables (with pgvector extension)
2. Game data → Text serialization → Embeddings → Vector storage
3. User query → Embedding → Cosine similarity search → Context retrieval → LLM response

### Frontend
- Angular 15 application with chat interface
- Connects to backend API at `http://localhost:8000`
- Located in `frontend/` directory

## Development Commands

### Docker Services
```bash
# Start database and Ollama services
docker compose up -d db ollama

# Pull required models
docker exec ollama ollama pull nomic-embed-text
docker exec ollama ollama pull llama3.2:3b

# Build application container
docker compose build app
```

### Backend Pipeline
```bash
# Run data ingestion
docker compose run --rm app python -m backend.ingest

# Generate embeddings (takes time)
docker compose run --rm app python -m backend.embed

# Run RAG pipeline and generate Part 1 answers
docker compose run --rm app python -m backend.rag

# Start API server
docker compose run --rm --service-ports app uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Development
```bash
cd frontend
npm install --force
npm start  # Runs on http://localhost:4200
```

### Testing
```bash
# Frontend tests
cd frontend
npm test
```

## Configuration

### Environment Variables
- `DB_DSN`: PostgreSQL connection string
- `OLLAMA_HOST`: Ollama API endpoint
- `EMBED_MODEL`: Embedding model name (default: nomic-embed-text)
- `LLM_MODEL`: LLM model name (default: llama3.2:3b)

### Database Schema
- Uses pgvector extension for vector operations
- Main tables: game_details (with embedding column), player_box_scores, players, teams
- HNSW index on embeddings for efficient similarity search

## Key Implementation Details

### Text Serialization Strategy
Game data is serialized as: `"game | season:{season} | date:{date} | home_team_id:{id} | away_team_id:{id} | home_points:{points} | away_points:{points}"`

### Retrieval Method
- Uses cosine similarity (`<->` operator) for vector search
- Returns top-k most similar games with metadata
- Evidence tracking includes table name and record IDs

### Project Structure
- `part1/`: Contains questions.json and generated answers.json
- `part2/`: Frontend demo video location
- `part3/`: Written responses to assignment questions
- `part4/`: Optional embedding fine-tuning work
- `prompts/`: AI tool usage tracking

## Important Notes

- This is a technical assessment project with proprietary NBA data
- Part 1 requires running the RAG pipeline to generate `part1/answers.json`
- Part 2 requires building a chat interface and demo video
- The embedding process can be time-intensive depending on hardware
- All evidence must track source table and record IDs for transparency