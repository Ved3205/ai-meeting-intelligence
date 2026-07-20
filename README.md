# 🎙️ AI Meeting Intelligence Platform

<p align="center">
  <img src="docs/AI-Meeting%20Platform.png" alt="AI Meeting Intelligence Platform Architecture" width="100%">
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?style=for-the-badge&logo=fastapi)
![Qdrant](https://img.shields.io/badge/Qdrant-VectorDB-red?style=for-the-badge)
![Whisper](https://img.shields.io/badge/OpenAI-Whisper-black?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-bge--m3-blueviolet?style=for-the-badge)
![RAG](https://img.shields.io/badge/RAG-Retrieval%20Augmented%20Generation-orange?style=for-the-badge)

</p>

---

# 📌 Overview

**AI Meeting Intelligence Platform** is an AI-powered SaaS application that converts meeting recordings into a searchable organizational knowledge base.

Instead of manually searching through long meeting recordings or transcripts, users can upload meetings and ask natural language questions such as:

- What decisions were made?
- What are my action items?
- Who is responsible for deployment?
- Summarize yesterday's meeting.
- What was discussed about authentication?

The platform combines **Speech-to-Text**, **Semantic Search**, **Vector Databases**, **RAG (Retrieval Augmented Generation)** and **Large Language Models** to provide grounded, timestamp-aware answers.

---

# 🚀 Vision

Transform meetings into an intelligent organizational memory where every discussion can be searched, summarized, and understood using AI.

---

# 🎯 Problem Statement

Organizations spend hundreds of hours in meetings.

After meetings end,

- Important decisions are forgotten
- Action items are lost
- Team members miss discussions
- Searching recordings is time-consuming
- Knowledge remains trapped inside videos

This platform solves these problems by automatically converting meetings into searchable AI knowledge.

---

# ✨ Features

## Current

- Meeting indexing pipeline
- Embedding generation using Ollama (bge-m3)
- Vector storage using Qdrant
- Chunk-based semantic indexing

---

## Planned

- Video Upload
- Audio Extraction
- Whisper Speech-to-Text
- Intelligent Transcript Chunking
- Meeting Summaries
- Action Item Detection
- Decision Extraction
- Topic Detection
- Sentiment Analysis
- AI Chat with Meetings
- Workspace Support
- User Authentication
- Multi-language Support
- PDF/DOCX Export
- FastAPI Backend
- Next.js Frontend

---

# 🏗 Project Architecture

The complete architecture is under developement and will be updated shortly.


---

# 🧠 System Workflow

```
User Uploads Meeting

        │

        ▼

Video Pipeline

        │

        ▼

FFmpeg
Extract Audio

        │

        ▼

Whisper

Speech → Text

        │

        ▼

Chunking Service

Split Transcript

        │

        ▼

Embedding Service

Generate Embeddings

        │

        ▼

Qdrant

Store Vectors

        │

        ▼

User asks Question

        │

        ▼

Query Embedding

        │

        ▼

Vector Search

        │

        ▼

Top Relevant Chunks

        │

        ▼

LLM

Generate Final Answer

        │

        ▼

Answer + Sources + Timestamps
```

---

# 🧩 Tech Stack

## Backend

- Python
- FastAPI *(Planned)*

---

## AI

- Whisper
- Ollama
- bge-m3 Embeddings
- Retrieval Augmented Generation (RAG)

---

## Vector Database

- Qdrant

---

## Database

- PostgreSQL *(Planned)*

---

## Frontend

- Next.js *(Planned)*

---

## File Storage

- Local Storage *(Current)*
- Cloud Storage *(Future)*

---

## Future Scaling

- Kafka
- Redis
- Docker
- Docker Compose

---

# 📂 Project Structure

```
ai-meeting-intelligence/

│
├── app/
│
├── pipelines/
│
├── services/
│
├── vectorstore/
│
├── config/
│
├── models/
│
├── prompts/
│
├── utils/
│
├── database/
│
├── api/
│
├── data/
│
├── tests/
│
├── docs/
│
├── notebooks/
│
├── scripts/
│
└── docker/
```

---

# 🔄 Processing Pipeline

## 1. Upload

User uploads

```
meeting.mp4
```

↓

Stored inside

```
data/uploads/
```

---

## 2. Audio Extraction

FFmpeg converts

```
MP4

↓

WAV
```

Stored in

```
data/audio/
```

---

## 3. Transcription

Whisper converts

```
Audio

↓

Transcript
```

Stored in

```
data/transcripts/
```

---

## 4. Chunking

Transcript

↓

Semantic Chunks

Stored inside

```
data/chunks/
```

---

## 5. Embeddings

Each chunk

↓

Embedding Vector

Generated using

```
bge-m3
```

through

```
Ollama
```

---

## 6. Vector Database

Embeddings

↓

Stored in

```
Qdrant
```

with metadata:

- Meeting ID
- Chunk ID
- Timestamps
- Meeting Title
- Transcript Text

---

## 7. Retrieval

User Question

↓

Embedding

↓

Qdrant Search

↓

Top-K Relevant Chunks

---

## 8. LLM

Retrieved Context

+

User Question

↓

LLM

↓

Grounded Response

---

# 📌 Current Development Status

## ✅ Completed

- Project architecture
- Embedding service
- Qdrant integration
- Meeting indexing pipeline
- Initial testing

---

## 🚧 In Progress

- Video pipeline
- Whisper transcription
- Chunking service

---

## 📅 Upcoming

- Retrieval pipeline
- RAG pipeline
- Summary pipeline
- FastAPI backend
- Next.js frontend
- PostgreSQL integration
- Docker support

---

# 🧪 Current Modules

## Embedding Service

Responsible for:

- Sending transcript chunks to Ollama
- Generating embeddings
- Returning embedding vectors

---

## Qdrant Client

Responsible for:

- Creating collections
- Uploading vectors
- Managing vector database

---

## Indexing Pipeline

Responsible for:

- Reading chunk JSON files
- Calling Embedding Service
- Creating vector collection
- Uploading vectors into Qdrant

---

# 🎯 Future AI Capabilities

- Meeting Summaries
- Decision Detection
- Action Item Extraction
- Topic Detection
- Semantic Search
- Cross Meeting Search
- Knowledge Base Chat
- Team Memory
- Workspace Search

---

# 📊 Future Scalability

Future enterprise architecture includes

- Kafka Event Streaming
- Worker-based Processing
- Redis Cache
- PostgreSQL
- Docker Deployment
- Cloud Storage
- Background Workers

allowing the platform to process thousands of meetings simultaneously.

---

# 📖 Learning Objectives

This project is designed to gain hands-on experience with:

- Python Backend Development
- AI Engineering
- Retrieval Augmented Generation
- Vector Databases
- Whisper
- Ollama
- Embedding Models
- FastAPI
- Docker
- Kafka
- PostgreSQL
- Software Architecture
- Production-grade Project Structure

---

# 👨‍💻 Author

**Vednarayan Hiralkar**

B.Tech Computer Science & Engineering (2023–2027)

---

# ⭐ Project Status

🚧 Active Development

This repository is currently under active development. New features and improvements are being added incrementally following a production-oriented architecture.