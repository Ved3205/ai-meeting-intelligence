## 1. System Overview

The AI Meeting Intelligence Platform converts meeting recordings into
searchable knowledge and uses Retrieval-Augmented Generation (RAG) to
answer questions using the meeting's actual content.

```mermaid
flowchart LR
    User[User]

    Video[Meeting Video / Audio]

    Ingestion[Ingestion Pipeline]

    Audio[Audio]
    Transcript[Transcript]
    Chunks[Semantic Chunks]
    Embeddings[Embeddings]
    Qdrant[(Qdrant)]

    Query[User Question]
    Retrieval[Semantic Retrieval]
    Context[Retrieved Context]
    LLM[LLM]
    Response[Grounded Response]

    User --> Video
    Video --> Ingestion

    Ingestion --> Audio
    Audio --> Transcript
    Transcript --> Chunks
    Chunks --> Embeddings
    Embeddings --> Qdrant

    User --> Query
    Query --> Retrieval
    Retrieval --> Qdrant
    Qdrant --> Context
    Context --> LLM
    Query --> LLM
    LLM --> Response
````

The core architecture is:

**Meeting → Knowledge → Vector Search → Retrieval → LLM → Answer**

---

# 2. Architectural Layers

```mermaid
flowchart TB

    Client[Client / User]

    API[API Layer<br/>FastAPI]

    Pipelines[Pipelines<br/>Workflow Orchestration]

    Services[Services<br/>Domain Operations]

    Models[Models<br/>Data Contracts]

    VectorStore[Vector Store<br/>Qdrant]

    Prompts[Prompt System]

    LLM[LLM Runtime<br/>Ollama]

    Storage[Local / Future File Storage]

    Database[PostgreSQL<br/>Future]

    Client --> API
    API --> Pipelines

    Pipelines --> Services
    Pipelines --> Models

    Services --> Models
    Services --> VectorStore
    Services --> Prompts
    Services --> LLM
    Services --> Storage
    Services --> Database
```

### Architectural Rule

```text
Pipeline
    ↓
"What should happen?"

Service
    ↓
"How is the operation performed?"

Model
    ↓
"What data is being passed?"

Vector Store
    ↓
"Where is semantic knowledge stored?"

Prompt System
    ↓
"How should the LLM be instructed?"

LLM
    ↓
"How should the retrieved knowledge be transformed into an answer?"
```

---

# 3. Meeting Ingestion Sequence

The ingestion workflow starts when a meeting recording enters the system.

```mermaid
sequenceDiagram

    actor User
    participant Upload as Upload / API
    participant VP as VideoPipeline
    participant FFmpeg as FFmpeg Utils
    participant TS as TranscriptionService
    participant Whisper as Whisper
    participant MS as MetadataService
    participant CS as ChunkingService
    participant IP as IndexingPipeline
    participant ES as EmbeddingService
    participant Ollama as Ollama
    participant Qdrant as Qdrant

    User->>Upload: Upload meeting.mp4

    Upload->>VP: Meeting + file path

    VP->>FFmpeg: Extract audio
    FFmpeg-->>VP: Audio

    VP->>TS: transcribe(meeting_id, audio)
    TS->>Whisper: Transcribe audio
    Whisper-->>TS: Timestamped segments
    TS-->>VP: Transcript

    VP->>MS: generate(meeting, audio, transcript)
    MS-->>VP: Metadata

    VP->>CS: chunk(transcript)
    CS-->>VP: Chunks

    VP->>IP: Index chunks

    loop For each chunk

        IP->>ES: embed(chunk)
        ES->>Ollama: Generate embedding
        Ollama-->>ES: Vector
        ES-->>IP: Embedding

        IP->>Qdrant: Store vector + payload
        Qdrant-->>IP: Stored

    end

    IP-->>VP: Indexing complete
    VP-->>Upload: PipelineResult
    Upload-->>User: Meeting processed
```

---

# 4. File Lifecycle

The meeting recording moves through several representations.

```mermaid
flowchart LR

    Video["meeting.mp4<br/>data/uploads/"]

    Audio["meeting.wav<br/>data/audio/"]

    Transcript["meeting.json<br/>data/transcripts/"]

    Chunks["meeting.json<br/>data/chunks/"]

    Embedding["Embedding vectors"]

    Qdrant["Qdrant"]

    Video -->|FFmpeg| Audio
    Audio -->|Whisper| Transcript
    Transcript -->|ChunkingService| Chunks
    Chunks -->|EmbeddingService| Embedding
    Embedding -->|VectorStoreService| Qdrant
```

---

# 5. Video Pipeline

### Module

```text
app/pipelines/video_pipeline.py
```

The video pipeline is the main ingestion orchestrator.

```mermaid
flowchart TD

    Input[Meeting Input]

    Validate[Validate Input]

    Audio[Extract Audio]

    Transcript[Transcribe Audio]

    Metadata[Generate Metadata]

    Chunks[Create Chunks]

    Index[Index Chunks]

    Result[PipelineResult]

    Input --> Validate
    Validate --> Audio
    Audio --> Transcript
    Transcript --> Metadata
    Metadata --> Chunks
    Chunks --> Index
    Index --> Result
```

The pipeline coordinates services; it should not duplicate their internal logic.

---

# 6. Audio Extraction

```mermaid
sequenceDiagram

    participant VP as VideoPipeline
    participant FFmpeg as ffmpeg_utils
    participant FS as File System

    VP->>FFmpeg: extract_audio(video_path)

    FFmpeg->>FS: Read video

    FFmpeg->>FS: Write WAV

    FS-->>FFmpeg: audio_path

    FFmpeg-->>VP: Audio
```

Input:

```text
data/uploads/meeting.mp4
```

Output:

```text
data/audio/meeting.wav
```

---

# 7. Transcription Flow

The transcription service converts audio into the internal `Transcript`
model using Whisper/Faster-Whisper. The service validates the audio,
runs transcription, converts Whisper segments, and returns `Transcript`. 

```mermaid
sequenceDiagram

    participant VP as VideoPipeline
    participant TS as TranscriptionService
    participant MM as ModelManager
    participant Whisper as Whisper
    participant Timer

    VP->>TS: transcribe(meeting_id, audio)

    TS->>TS: Validate audio

    TS->>MM: Get Whisper model

    MM-->>TS: Whisper model

    TS->>Timer: Start timer

    TS->>Whisper: transcribe(audio)

    Whisper-->>TS: Segments

    TS->>TS: Convert segments

    TS->>Timer: Stop timer

    TS-->>VP: Transcript
```

---

# 8. Transcript → Chunk Flow

```mermaid
flowchart TD

    Transcript[Transcript]

    Segments[Transcript Segments]

    Chunker[ChunkingService]

    Chunk1[Chunk 1]
    Chunk2[Chunk 2]
    Chunk3[Chunk 3]
    More[More Chunks...]

    Transcript --> Segments

    Segments --> Chunker

    Chunker --> Chunk1
    Chunker --> Chunk2
    Chunker --> Chunk3
    Chunker --> More
```

Chunks preserve the information required for retrieval, including
transcript text and timestamp information.

Output:

```text
data/chunks/
```

---

# 9. Chunk → Embedding Flow

```mermaid
sequenceDiagram

    participant Pipeline as IndexingPipeline
    participant ES as EmbeddingService
    participant Ollama
    participant Model as bge-m3

    Pipeline->>ES: embed(chunk)

    ES->>Ollama: Embedding request

    Ollama->>Model: Encode chunk text

    Model-->>Ollama: Vector

    Ollama-->>ES: Embedding

    ES-->>Pipeline: list[float]
```

The `EmbeddingService` accepts a `Chunk` and produces an embedding vector. 

---

# 10. Indexing Pipeline

```mermaid
sequenceDiagram

    participant IP as IndexingPipeline
    participant FileSystem
    participant ES as EmbeddingService
    participant VS as VectorStoreService
    participant Qdrant

    IP->>FileSystem: Read chunk JSON

    FileSystem-->>IP: Meeting + Chunks

    loop Each chunk

        IP->>ES: embed(chunk)

        ES-->>IP: Embedding

        IP->>VS: upload_chunk(chunk)

        VS->>Qdrant: Upsert vector + payload

        Qdrant-->>VS: Success

        VS-->>IP: Success

    end

    IP-->>FileSystem: Indexing complete
```

---

# 11. Qdrant Data Model

Each indexed chunk conceptually becomes:

```mermaid
flowchart TB

    Point[Qdrant Point]

    ID[Vector ID]

    Vector[Embedding Vector]

    Payload[Payload]

    Text[Chunk Text]

    MeetingID[Meeting ID]

    Timestamp[Start / End Timestamp]

    Metadata[Meeting Metadata]

    Point --> ID
    Point --> Vector
    Point --> Payload

    Payload --> Text
    Payload --> MeetingID
    Payload --> Timestamp
    Payload --> Metadata
```

Qdrant is responsible for storing and retrieving vector embeddings and
their associated payloads. 

---

# 12. Query / RAG Sequence

After indexing, the meeting becomes searchable.

```mermaid
sequenceDiagram

    actor User

    participant API
    participant QP as QueryPipeline
    participant ES as EmbeddingService
    participant RS as RetrievalService
    participant Qdrant
    participant PF as PromptFactory
    participant LLM as LLMService
    participant Ollama

    User->>API: Ask question

    API->>QP: Query

    QP->>RS: retrieve(query)

    RS->>ES: Embed query

    ES->>Ollama: Generate query embedding

    Ollama-->>ES: Query vector

    ES-->>RS: Query vector

    RS->>Qdrant: Semantic search

    Qdrant-->>RS: Top-K payloads

    RS-->>QP: RetrievalResult[]

    QP->>PF: Build prompt

    PF-->>QP: PromptRequest

    QP->>LLM: generate_answer(request)

    LLM->>PF: Get QA prompt

    PF-->>LLM: Prompt

    LLM->>Ollama: Generate answer

    Ollama-->>LLM: LLM response

    LLM-->>QP: LLMResponse

    QP-->>API: Response

    API-->>User: Answer + sources + timestamps
```

The retrieval service first generates the query embedding, searches
Qdrant, converts returned payloads into `RetrievedChunk` objects, and
returns ranked retrieval results. 

---

# 13. RAG Data Flow

```mermaid
flowchart LR

    Question[User Question]

    Query[Query Model]

    Embedding[Query Embedding]

    Search[Qdrant Semantic Search]

    Retrieved[RetrievedChunk]

    Results[RetrievalResult]

    Prompt[PromptRequest]

    LLMRequest[LLMRequest]

    LLMResponse[LLMResponse]

    Response[Final Response]

    Question --> Query
    Query --> Embedding
    Embedding --> Search
    Search --> Retrieved
    Retrieved --> Results
    Results --> Prompt
    Prompt --> LLMRequest
    LLMRequest --> LLMResponse
    LLMResponse --> Response
```

This directly follows the model contract defined for the project. 

---

# 14. Retrieval Service

```mermaid
flowchart TD

    Query[Query]

    ES[EmbeddingService]

    Vector[Query Vector]

    Qdrant[(Qdrant)]

    Payloads[Top-K Payloads]

    RetrievedChunk[RetrievedChunk]

    Results[RetrievalResult]

    Query --> ES
    ES --> Vector
    Vector --> Qdrant
    Qdrant --> Payloads
    Payloads --> RetrievedChunk
    RetrievedChunk --> Results
```

### Responsibility

```text
Query
  ↓
Generate query embedding
  ↓
Search Qdrant
  ↓
Convert payloads
  ↓
Rank results
  ↓
Return RetrievalResult
```

---

# 15. Prompt Construction

```mermaid
flowchart TD

    Query[User Query]

    Retrieved[Retrieved Chunks]

    Metadata[Meeting Metadata]

    PromptRequest[PromptRequest]

    Factory[PromptFactory]

    Builder[QA Prompt Builder]

    Prompt[Final Prompt]

    Query --> PromptRequest
    Retrieved --> PromptRequest
    Metadata --> PromptRequest

    PromptRequest --> Factory
    Factory --> Builder
    Builder --> Prompt
```

The prompt system separates prompt selection/building from the LLM
service. `LLMService.generate_answer()` obtains the QA prompt builder,
builds the prompt, sends it to Ollama, and returns `LLMResponse`. 

---

# 16. LLM Generation

```mermaid
sequenceDiagram

    participant QP as QueryPipeline
    participant LLM as LLMService
    participant PF as PromptFactory
    participant Builder as QA Prompt Builder
    participant Ollama

    QP->>LLM: LLMRequest

    LLM->>PF: Get QA builder

    PF-->>LLM: QA builder

    LLM->>Builder: Build prompt

    Builder-->>LLM: Prompt

    LLM->>Ollama: Generate

    Ollama-->>LLM: Answer

    LLM-->>QP: LLMResponse
```

---

# 17. Final Answer Construction

```mermaid
flowchart LR

    Retrieval[Retrieved Sources]

    LLM[LLMResponse]

    Builder[Response Builder]

    Answer[Final Response]

    Sources[Source Chunks]

    Timestamps[Timestamps]

    Retrieval --> Builder
    LLM --> Builder

    Builder --> Answer
    Builder --> Sources
    Builder --> Timestamps
```

The goal is not simply to return an LLM-generated sentence.

The response should retain the relationship between:

```text
Answer
  ↓
Retrieved evidence
  ↓
Meeting
  ↓
Timestamp
```

---

# 18. Summary Pipeline

The summary pipeline is separate from interactive Q&A.

```mermaid
flowchart TD

    Meeting[Meeting]

    Transcript[Transcript]

    Context[Meeting Context]

    Summary[Executive Summary]

    Topics[Topics]

    Actions[Action Items]

    Decisions[Decisions]

    Keywords[Keywords]

    Meeting --> Transcript
    Transcript --> Context

    Context --> Summary
    Context --> Topics
    Context --> Actions
    Context --> Decisions
    Context --> Keywords
```

---

# 19. Model Flow

The project's model layer forms the backbone of communication between
components.

```mermaid
flowchart TD

    Meeting[Meeting]

    Audio[Audio]

    Transcript[Transcript]

    Segment[TranscriptSegment]

    Chunk[Chunk]

    Embedding[Embedding]

    RetrievedChunk[RetrievedChunk]

    RetrievalResult[RetrievalResult]

    PromptRequest[PromptRequest]

    LLMRequest[LLMRequest]

    LLMResponse[LLMResponse]

    Response[Response]

    Meeting --> Audio
    Audio --> Transcript
    Transcript --> Segment
    Segment --> Chunk

    Chunk --> Embedding
    Chunk --> RetrievedChunk

    RetrievedChunk --> RetrievalResult
    RetrievalResult --> PromptRequest
    PromptRequest --> LLMRequest
    LLMRequest --> LLMResponse
    LLMResponse --> Response
```

---

# 20. Component Responsibilities

```mermaid
flowchart TB

    Pipeline["Pipelines<br/>Orchestrate workflows"]

    Services["Services<br/>Perform domain operations"]

    Models["Models<br/>Define data contracts"]

    VectorStore["Vector Store<br/>Persist / retrieve vectors"]

    Prompts["Prompts<br/>Build LLM instructions"]

    Utils["Utils<br/>Reusable technical helpers"]

    Config["Config<br/>Runtime configuration"]

    Pipeline --> Services
    Pipeline --> Models

    Services --> Models
    Services --> VectorStore
    Services --> Prompts

    Services --> Utils
    Services --> Config
```

---

# 21. Service Dependency Flow

```mermaid
flowchart LR

    VideoPipeline[VideoPipeline]

    MetadataService[MetadataService]

    TranscriptionService[TranscriptionService]

    ChunkingService[ChunkingService]

    IndexingPipeline[IndexingPipeline]

    EmbeddingService[EmbeddingService]

    VectorStoreService[VectorStoreService]

    RetrievalService[RetrievalService]

    LLMService[LLMService]

    PromptFactory[PromptFactory]

    VideoPipeline --> TranscriptionService
    VideoPipeline --> MetadataService
    VideoPipeline --> ChunkingService
    VideoPipeline --> IndexingPipeline

    IndexingPipeline --> EmbeddingService
    IndexingPipeline --> VectorStoreService

    RetrievalService --> EmbeddingService
    RetrievalService --> VectorStoreService

    LLMService --> PromptFactory
```

---

# 22. Data Ownership

```mermaid
flowchart TB

    FileSystem["Local File System"]

    FileSystem --> Uploads["data/uploads"]
    FileSystem --> Audio["data/audio"]
    FileSystem --> Transcripts["data/transcripts"]
    FileSystem --> Chunks["data/chunks"]
    FileSystem --> Embeddings["data/embeddings"]
    FileSystem --> Exports["data/exports"]

    Qdrant["Qdrant"]

    Qdrant --> Vectors["Embeddings"]
    Qdrant --> Payload["Chunk Metadata"]
    Qdrant --> Search["Semantic Search"]
```

The current development architecture intentionally keeps the processing
local while the scalable architecture remains future work. 

---

# 23. Testing Architecture

```mermaid
flowchart TD

    Unit[Unit Tests]

    Integration[Integration Tests]

    Pipeline[Pipeline Tests]

    RAG[RAG Tests]

    Unit --> Services
    Integration --> ServiceInteractions
    Pipeline --> EndToEnd
    RAG --> QueryFlow

    Services["Individual Services"]

    ServiceInteractions["Embedding → Qdrant"]

    EndToEnd["Video → Audio → Transcript → Chunks → Embeddings → Qdrant"]

    QueryFlow["Question → Retrieval → Prompt → LLM → Response"]
```

The testing strategy covers unit, integration, pipeline, and RAG-level
testing. 

---

# 24. Current Development State

```mermaid
flowchart LR

    Current["CURRENT"]

    Embedding["EmbeddingService"]
    Qdrant["Qdrant"]
    Indexing["IndexingPipeline"]

    Current --> Embedding
    Current --> Qdrant
    Current --> Indexing
```

Currently implemented core capabilities include:

* Meeting indexing pipeline
* Embedding generation using Ollama / `bge-m3`
* Qdrant vector storage
* Chunk-based semantic indexing

These are the components currently represented as implemented in the
project documentation. 

---

# 25. Target Architecture

```mermaid
flowchart TB

    Frontend["Next.js Frontend"]

    API["FastAPI Backend"]

    Pipelines["AI Processing Pipelines"]

    Whisper["Whisper"]

    Embedding["Embedding Service"]

    Qdrant["Qdrant"]

    PostgreSQL["PostgreSQL"]

    LLM["LLM"]

    Frontend --> API
    API --> Pipelines

    Pipelines --> Whisper
    Pipelines --> Embedding
    Pipelines --> Qdrant
    Pipelines --> LLM

    API --> PostgreSQL
```

Future functionality includes FastAPI, Next.js, authentication,
workspace support, summaries, action-item extraction, decision
extraction, topic detection, sentiment analysis, and export. 

---

# 26. Future Scalable Architecture

```mermaid
flowchart LR

    Upload["Meeting Upload"]

    API["API Gateway"]

    Kafka["Kafka<br/>Event Bus"]

    Transcription["Transcription Worker"]

    Embedding["Embedding Worker"]

    Summary["Summary Worker"]

    Actions["Action Item Worker"]

    Decisions["Decision Worker"]

    Notification["Notification Worker"]

    PostgreSQL[(PostgreSQL)]

    Qdrant[(Qdrant)]

    Storage["File Storage"]

    Redis["Redis"]

    Upload --> API
    API --> Kafka

    Kafka --> Transcription
    Kafka --> Embedding
    Kafka --> Summary
    Kafka --> Actions
    Kafka --> Decisions
    Kafka --> Notification

    Transcription --> PostgreSQL
    Embedding --> Qdrant
    Summary --> PostgreSQL
    Actions --> PostgreSQL
    Decisions --> PostgreSQL
    Notification --> Redis

    Transcription --> Storage
```

This architecture is a future scaling direction rather than the current
local implementation.

---

# 27. Core Architectural Principle

```mermaid
flowchart TD

    Pipeline["Pipeline"]

    Service["Service"]

    Model["Model"]

    Storage["Storage"]

    LLM["LLM"]

    Pipeline -->|"orchestrates"| Service
    Service -->|"uses"| Model
    Service -->|"persists / retrieves"| Storage
    Service -->|"generates intelligence"| LLM
```

Remember:

```text
PIPELINES
Move the workflow.

SERVICES
Perform the operations.

MODELS
Define the data.

VECTOR STORE
Stores and retrieves semantic knowledge.

PROMPTS
Define how the LLM should reason over retrieved context.

LLM
Generates the final intelligence.
```

---

# 28. Complete Platform Flow

```mermaid
flowchart TD

    User["User"]

    Upload["Meeting Upload"]

    VideoPipeline["video_pipeline.py"]

    FFmpeg["FFmpeg"]

    Whisper["Whisper"]

    Transcript["Transcript"]

    Chunking["ChunkingService"]

    Chunks["Chunks"]

    Embedding["EmbeddingService"]

    Vectors["Embeddings"]

    Qdrant[("Qdrant")]

    Question["User Question"]

    Retrieval["RetrievalService"]

    Context["Top-K Retrieved Chunks"]

    Prompt["PromptFactory"]

    LLM["LLMService"]

    Answer["Answer + Sources + Timestamps"]

    User --> Upload
    Upload --> VideoPipeline

    VideoPipeline --> FFmpeg
    FFmpeg --> Whisper
    Whisper --> Transcript
    Transcript --> Chunking
    Chunking --> Chunks
    Chunks --> Embedding
    Embedding --> Vectors
    Vectors --> Qdrant

    User --> Question
    Question --> Retrieval
    Retrieval --> Qdrant
    Qdrant --> Context
    Context --> Prompt
    Question --> Prompt
    Prompt --> LLM
    LLM --> Answer
    Answer --> User
```

---

# 29. One-Line Mental Model

```text
Meeting
  ↓
Audio
  ↓
Transcript
  ↓
Chunks
  ↓
Embeddings
  ↓
Qdrant
  ↓
Retrieve
  ↓
Prompt
  ↓
LLM
  ↓
Grounded Answer
```

The platform therefore turns:

**Meeting Audio → Knowledge → Searchable Memory → Grounded Intelligence**

```
