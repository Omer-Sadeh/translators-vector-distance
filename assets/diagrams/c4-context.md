# C4 Context Diagram

## System Context: Translation Chain Vector Distance Analysis

```mermaid
graph TB
    User[Research User]
    CLI[CLI Interface]
    System[Translation Chain<br/>Analysis System]
    Agents[Translation Agents<br/>Cursor/Gemini/Claude/Ollama]
    DB[(SQLite Database)]
    
    User -->|Runs experiments| CLI
    CLI -->|Commands| System
    System -->|Invokes| Agents
    System -->|Stores results| DB
    System -->|Generates reports| User
    Agents -->|Translation results| System
    
    style System fill:#4A90E2,color:#fff
    style User fill:#95E1D3,color:#000
    style Agents fill:#F38181,color:#fff
    style DB fill:#AA96DA,color:#fff
```

## Actors

- **Research User**: Investigator studying translation quality degradation
- **Translation Agents**: External CLI tools (cursor-agent, gemini, claude, ollama)
- **SQLite Database**: Persistent storage for experimental results

## System Boundary

The system orchestrates multi-stage translations, injects controlled errors, computes vector embeddings, calculates semantic distances, and provides statistical analysis capabilities.

