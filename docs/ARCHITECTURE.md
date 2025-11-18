# System Architecture Documentation
## Translation Chain Vector Distance Analysis

**Version:** 1.0  
**Date:** November 18, 2025

---

## Table of Contents
1. [System Overview](#system-overview)
2. [C4 Model Diagrams](#c4-model-diagrams)
3. [UML Diagrams](#uml-diagrams)
4. [Architectural Decision Records (ADRs)](#architectural-decision-records)
5. [Data Flow](#data-flow)
6. [Component Specifications](#component-specifications)
7. [API and Interfaces](#api-and-interfaces)

---

## 1. System Overview

The Translation Chain Vector Distance Analysis system is a research tool designed to measure semantic drift through multi-stage machine translation. It employs a plugin-based architecture supporting multiple LLM backends, uses local embedding models for vector analysis, and provides both static and interactive visualization capabilities.

### Key Architectural Principles
- **Modularity:** Each component has a single, well-defined responsibility
- **Extensibility:** Plugin architecture allows easy addition of new agents
- **Testability:** Clear interfaces enable comprehensive unit testing
- **Configurability:** YAML-based configuration with no hardcoded values
- **Portability:** SQLite and local models ensure cross-platform compatibility

---

## 2. C4 Model Diagrams

### 2.1 Level 1: System Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                       External Systems                          │
│                                                                 │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│   │ cursor-agent │  │   gemini CLI │  │  claude CLI  │        │
│   └──────────────┘  └──────────────┘  └──────────────┘        │
│         │                   │                  │                │
│         └───────────────────┼──────────────────┘                │
└─────────────────────────────┼──────────────────────────────────┘
                              │
                              ▼
                  ┌─────────────────────────┐
                  │                         │
                  │  Translation Vector     │
                  │  Distance System        │
                  │                         │
                  └─────────────────────────┘
                              │
                              ▼
                  ┌─────────────────────────┐
                  │       Researcher        │
                  │    (Primary User)       │
                  └─────────────────────────┘
                              │
                              ▼
                  ┌─────────────────────────┐
                  │  Sentence Transformers  │
                  │   (Local ML Model)      │
                  └─────────────────────────┘

Purpose: Researcher analyzes semantic drift through translation chains
         by testing sentences with controlled spelling errors across
         multiple LLM backends, measuring vector distances.
```

### 2.2 Level 2: Container Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                     Translation Vector Distance System              │
│                                                                      │
│  ┌─────────────────────┐         ┌──────────────────────┐          │
│  │   Web Dashboard     │◄────────│  Visualization Layer │          │
│  │   (Plotly Dash)     │         │   - plots.py         │          │
│  │   Port 8050         │         │   - dashboard.py     │          │
│  └─────────────────────┘         └──────────────────────┘          │
│           │                                  │                      │
│           │                                  ▼                      │
│  ┌────────▼──────────────────────────────────────────┐             │
│  │         Core Translation Engine                    │             │
│  │  ┌──────────────┐  ┌────────────────────┐        │             │
│  │  │ Translation  │  │   Agent Factory    │        │             │
│  │  │   Chain      │──│  - cursor_agent    │        │             │
│  │  │ Orchestrator │  │  - gemini_agent    │        │             │
│  │  │              │  │  - claude_agent    │        │             │
│  │  │              │  │  - ollama_agent    │        │             │
│  │  └──────────────┘  └────────────────────┘        │             │
│  │         │                                          │             │
│  │         ▼                                          │             │
│  │  ┌──────────────┐  ┌────────────────────┐        │             │
│  │  │ Error        │  │  Vector Analysis   │        │             │
│  │  │ Injector     │  │  - embeddings.py   │        │             │
│  │  │              │  │  - distance.py     │        │             │
│  │  │              │  │  - statistics.py   │        │             │
│  │  └──────────────┘  └────────────────────┘        │             │
│  └─────────────────────────────────────────┼─────────┘             │
│                                             │                       │
│                    ┌────────────────────────▼────────┐              │
│                    │   Data Management Layer         │              │
│                    │  - storage.py                   │              │
│                    │  - generator.py                 │              │
│                    └────────────────────────┬────────┘              │
│                                             │                       │
│                    ┌────────────────────────▼────────┐              │
│                    │   SQLite Database               │              │
│                    │   (experiments.db)              │              │
│                    └─────────────────────────────────┘              │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │            Configuration System                           │      │
│  │  settings.py ◄── experiment_config.yaml                  │      │
│  └──────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────┘

Technologies:
- Application: Python 3.8+
- Web: Dash (Flask-based)
- Database: SQLite3
- ML: sentence-transformers, scikit-learn
- Visualization: Plotly, Matplotlib, Seaborn
```

### 2.3 Level 3: Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Subsystem                            │
│                                                                 │
│         ┌────────────────────────────────┐                      │
│         │       BaseAgent (ABC)          │                      │
│         │                                │                      │
│         │  + translate()                 │                      │
│         │  + validate_input()            │                      │
│         │  # before_translate()          │                      │
│         │  # after_translate()           │                      │
│         │  # on_error()                  │                      │
│         └───────────┬────────────────────┘                      │
│                     │                                           │
│        ┌────────────┼────────────┬──────────────┐              │
│        │            │            │              │              │
│  ┌─────▼─────┐ ┌───▼────┐ ┌────▼─────┐ ┌──────▼──────┐       │
│  │  Cursor   │ │ Gemini │ │  Claude  │ │   Ollama    │       │
│  │  Agent    │ │ Agent  │ │  Agent   │ │   Agent     │       │
│  └───────────┘ └────────┘ └──────────┘ └─────────────┘       │
│        │            │            │              │              │
│        └────────────┼────────────┴──────────────┘              │
│                     │                                           │
│              ┌──────▼────────┐                                 │
│              │ AgentFactory  │                                 │
│              │               │                                 │
│              │ + create()    │                                 │
│              └───────────────┘                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   Translation Subsystem                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐           │
│  │          TranslationChain                        │           │
│  │                                                  │           │
│  │  - agent: BaseAgent                              │           │
│  │  + execute_chain(text, error_rate)               │           │
│  │  + get_intermediate_translations()               │           │
│  │  - _translate_step()                             │           │
│  └──────────────────┬───────────────────────────────┘           │
│                     │                                           │
│                     │ uses                                      │
│                     ▼                                           │
│  ┌──────────────────────────────────────────────────┐           │
│  │          ErrorInjector                           │           │
│  │                                                  │           │
│  │  + inject_errors(text, error_rate)               │           │
│  │  - _character_swap()                             │           │
│  │  - _character_deletion()                         │           │
│  │  - _character_insertion()                        │           │
│  │  - _character_substitution()                     │           │
│  │  + calculate_actual_error_rate()                 │           │
│  └──────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Analysis Subsystem                          │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │ EmbeddingEngine  │  │  DistanceMetrics │                    │
│  │                  │  │                  │                    │
│  │ - model          │  │ + cosine()       │                    │
│  │ + encode()       │  │ + euclidean()    │                    │
│  │ + batch_encode() │  │ + manhattan()    │                    │
│  └──────────────────┘  └──────────────────┘                    │
│           │                      │                              │
│           └──────────┬───────────┘                              │
│                      │                                          │
│                      ▼                                          │
│           ┌────────────────────┐                                │
│           │ StatisticalAnalysis│                                │
│           │                    │                                │
│           │ + descriptive()    │                                │
│           │ + correlation()    │                                │
│           │ + hypothesis_test()│                                │
│           │ + confidence_int() │                                │
│           └────────────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

### 2.4 Level 4: Code Diagram (Key Classes)

```python
# BaseAgent hierarchy
class BaseAgent(ABC):
    config: Dict[str, Any]
    
    @abstractmethod
    def translate(text: str, source: str, target: str) -> TranslationResult
    
    def validate_input(text, source, target) -> None
    def before_translate(...) -> None  # Hook
    def after_translate(...) -> None   # Hook
    def on_error(error) -> None        # Hook

class CursorAgent(BaseAgent):
    def translate(...) -> TranslationResult:
        # subprocess.run(['cursor-agent', '-p', prompt])
        
class TranslationChain:
    agent: BaseAgent
    error_injector: ErrorInjector
    
    def execute_chain(text: str, error_rate: float) -> ChainResult:
        # 1. Inject errors
        # 2. EN -> FR
        # 3. FR -> HE  
        # 4. HE -> EN
        
class EmbeddingEngine:
    model: SentenceTransformer
    
    def encode(texts: List[str]) -> np.ndarray:
        # return embeddings
```

---

## 3. UML Diagrams

### 3.1 Class Diagram: Core Components

```
┌─────────────────────────────┐
│      <<abstract>>           │
│       BaseAgent             │
├─────────────────────────────┤
│ # config: Dict              │
├─────────────────────────────┤
│ + __init__(config)          │
│ + translate(...)            │
│ + validate_input(...)       │
│ # before_translate(...)     │
│ # after_translate(...)      │
│ # on_error(...)             │
│ + get_agent_type()          │
└──────────┬──────────────────┘
           │
           │ ◄────implements────
           │
     ┌─────┴─────┬─────────┬─────────┐
     │           │         │         │
┌────▼───┐  ┌───▼────┐ ┌──▼─────┐ ┌─▼──────┐
│ Cursor │  │ Gemini │ │ Claude │ │ Ollama │
│ Agent  │  │ Agent  │ │ Agent  │ │ Agent  │
└────────┘  └────────┘ └────────┘ └────────┘

┌──────────────────────┐
│  AgentFactory        │
├──────────────────────┤
│ + create(type, cfg)  │
└──────────────────────┘

┌──────────────────────┐      ┌──────────────────────┐
│ TranslationChain     │◆────▶│    BaseAgent         │
├──────────────────────┤      └──────────────────────┘
│ - agent              │
│ - error_injector     │◆─┐
├──────────────────────┤  │
│ + execute_chain(...) │  │   ┌──────────────────────┐
│ - _translate_step()  │  └──▶│   ErrorInjector      │
└──────────────────────┘      ├──────────────────────┤
                              │ + inject_errors(...) │
                              │ - _char_swap()       │
                              │ - _char_delete()     │
                              └──────────────────────┘

┌──────────────────────┐      ┌──────────────────────┐
│  EmbeddingEngine     │      │   DistanceMetrics    │
├──────────────────────┤      ├──────────────────────┤
│ - model              │      │ + cosine(v1, v2)     │
│ - device             │      │ + euclidean(v1, v2)  │
├──────────────────────┤      │ + manhattan(v1, v2)  │
│ + encode(texts)      │      └──────────────────────┘
│ + batch_encode(...)  │
└──────────────────────┘
```

### 3.2 Sequence Diagram: Translation Chain Execution

```
Researcher  TranslationChain  ErrorInjector  CursorAgent  EmbeddingEngine  Database
    │               │               │              │              │            │
    ├──execute()───▶│               │              │              │            │
    │               │               │              │              │            │
    │               ├─inject_errors─▶              │              │            │
    │               │◄───corrupted──┤              │              │            │
    │               │                text           │              │            │
    │               │                               │              │            │
    │               ├──translate(EN→FR)────────────▶              │            │
    │               │◄──────French text─────────────┤              │            │
    │               │                               │              │            │
    │               ├──translate(FR→HE)────────────▶              │            │
    │               │◄──────Hebrew text─────────────┤              │            │
    │               │                               │              │            │
    │               ├──translate(HE→EN)────────────▶              │            │
    │               │◄──────English text────────────┤              │            │
    │               │                               │              │            │
    │               ├──encode(original)────────────────────────────▶           │
    │               │◄──────embedding_1─────────────────────────────┤           │
    │               │                               │              │            │
    │               ├──encode(final)────────────────────────────────▶           │
    │               │◄──────embedding_2─────────────────────────────┤           │
    │               │                               │              │            │
    │               ├──calculate_distance()──────────────────────────────────▶  │
    │               │◄──────distance_value─────────────────────────────────────┤ │
    │               │                               │              │            │
    │               ├──store_result()───────────────────────────────────────────▶│
    │               │◄──────success─────────────────────────────────────────────┤
    │               │                               │              │            │
    │◄─ChainResult──┤               │              │              │            │
    │               │               │              │              │            │
```

### 3.3 Activity Diagram: Experiment Execution Flow

```
                 [Start Experiment]
                         │
                         ▼
              ┌──────────────────────┐
              │ Load Configuration   │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Load Test Sentences  │
              └──────────┬───────────┘
                         │
                         ▼
              ╔══════════════════════╗
              ║ For each error rate  ║◄─────┐
              ╚══════════╤═══════════╝      │
                         │                   │
                         ▼                   │
              ╔══════════════════════╗      │
              ║ For each sentence    ║◄──┐  │
              ╚══════════╤═══════════╝   │  │
                         │                │  │
                         ▼                │  │
              ┌──────────────────────┐   │  │
              │ Inject Spelling      │   │  │
              │ Errors               │   │  │
              └──────────┬───────────┘   │  │
                         │                │  │
                         ▼                │  │
              ┌──────────────────────┐   │  │
              │ Execute Translation  │   │  │
              │ Chain (EN→FR→HE→EN)  │   │  │
              └──────────┬───────────┘   │  │
                         │                │  │
                         ▼                │  │
                    ◊───────────◊         │  │
                   /   Success?  \        │  │
                  ◊───────────────◊       │  │
                 /                 \      │  │
              Yes                  No     │  │
               │                    │     │  │
               ▼                    ▼     │  │
    ┌─────────────────┐  ┌──────────────┐│  │
    │ Calculate       │  │ Log Error    ││  │
    │ Embeddings      │  │ & Continue   ││  │
    └────────┬────────┘  └──────┬───────┘│  │
             │                   │        │  │
             ▼                   │        │  │
    ┌─────────────────┐         │        │  │
    │ Compute Vector  │         │        │  │
    │ Distance        │         │        │  │
    └────────┬────────┘         │        │  │
             │                   │        │  │
             ▼                   │        │  │
    ┌─────────────────┐         │        │  │
    │ Store Results   │         │        │  │
    │ in Database     │         │        │  │
    └────────┬────────┘         │        │  │
             │                   │        │  │
             └───────────────────┘        │  │
                         │                │  │
                         ├────────────────┘  │
                         │                   │
                         ├───────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Generate Statistics  │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Create Visualizations│
              └──────────┬───────────┘
                         │
                         ▼
                  [End Experiment]
```

---

## 4. Architectural Decision Records (ADRs)

### ADR-001: CLI Agents vs Direct API Calls

**Status:** Accepted  
**Date:** 2025-11-18  
**Context:**  
The system needs to interface with multiple LLMs for translation. Options include:
1. Direct API calls to OpenAI, Anthropic, Google APIs
2. CLI-based agents (cursor-agent, gemini CLI, claude CLI)

**Decision:**  
Use CLI-based agents exclusively.

**Rationale:**
- **No API Keys Required:** Eliminates security concerns around key storage
- **Cost:** Free usage with installed CLI tools
- **Flexibility:** Supports both cloud and local LLMs (Ollama)
- **Simplicity:** Subprocess interface is straightforward
- **User Control:** Users choose their preferred LLM backend

**Consequences:**
- ✅ Positive: No API costs, no key management, local execution possible
- ✅ Positive: Easy to add new agents (just implement BaseAgent)
- ❌ Negative: Requires CLI tools to be pre-installed
- ❌ Negative: Less control over API parameters (temperature, etc.)
- ⚠️ Mitigation: Provide clear installation guide, support 4 different CLIs

**Alternatives Considered:**
1. Direct API integration: Rejected due to cost and key management
2. Mixed approach: Rejected for consistency and complexity

---

### ADR-002: Embedding Model Selection

**Status:** Accepted  
**Date:** 2025-11-18  
**Context:**  
Need to generate vector embeddings for semantic similarity measurement. Options:
1. OpenAI embeddings API (ada-002, text-embedding-3-small)
2. Sentence-transformers with open-source models
3. Universal Sentence Encoder (TensorFlow)

**Decision:**  
Use sentence-transformers library with `all-MiniLM-L6-v2` model.

**Rationale:**
- **Free:** No API costs, no usage limits
- **Local:** Works offline after initial download
- **Quality:** Sufficient performance for research (benchmark: 63.3% on semantic similarity tasks)
- **Speed:** Fast inference on CPU (~20ms per sentence)
- **Lightweight:** Model size only 80MB
- **Ecosystem:** Well-maintained library with extensive documentation

**Consequences:**
- ✅ Positive: Zero ongoing costs
- ✅ Positive: Reproducible results (frozen model weights)
- ✅ Positive: No internet dependency after setup
- ✅ Positive: Privacy-preserving (no data sent externally)
- ❌ Negative: Lower quality than OpenAI embeddings
- ⚠️ Mitigation: Sufficient for detecting translation drift

**Alternatives Considered:**
1. OpenAI embeddings: Rejected due to cost ($0.02 per 1M tokens)
2. all-mpnet-base-v2: Rejected as larger (420MB) with marginal quality gain
3. USE: Rejected due to TensorFlow dependency complexity

---

### ADR-003: Database Technology

**Status:** Accepted  
**Date:** 2025-11-18  
**Context:**  
Need persistent storage for experiment data. Options:
1. SQLite (file-based)
2. PostgreSQL (client-server)
3. JSON files
4. CSV files

**Decision:**  
Use SQLite with Write-Ahead Logging (WAL) mode.

**Rationale:**
- **Zero Configuration:** No server setup required
- **Portability:** Single file, easy to share and backup
- **Sufficient Scale:** Handles millions of rows (project needs <1000)
- **SQL Interface:** Standard query language, complex joins supported
- **ACID Compliance:** Data integrity guarantees
- **Python Built-in:** sqlite3 module in standard library

**Consequences:**
- ✅ Positive: Simple deployment, no dependencies
- ✅ Positive: Easy backup (copy single file)
- ✅ Positive: Cross-platform compatibility
- ❌ Negative: No concurrent writes (but not needed)
- ❌ Negative: Limited for production scale (but this is research)

**Alternatives Considered:**
1. PostgreSQL: Rejected as overkill for research project
2. JSON files: Rejected due to lack of query capabilities
3. CSV: Rejected due to poor relational data modeling

---

### ADR-004: Primary Distance Metric

**Status:** Accepted  
**Date:** 2025-11-18  
**Context:**  
Multiple distance/similarity metrics exist for vector comparison:
1. Cosine similarity/distance
2. Euclidean distance (L2)
3. Manhattan distance (L1)
4. Dot product

**Decision:**  
Use **cosine distance** as primary metric, with Euclidean and Manhattan as secondary.

**Rationale:**
- **Magnitude Independence:** Cosine measures angle, not magnitude
- **Standard Practice:** Most common in semantic similarity literature
- **Interpretability:** 0 = identical, 2 = opposite
- **Normalization:** Sentence-transformers embeddings are unit-normalized
- **Comparison:** Academic papers use cosine for semantic similarity

**Consequences:**
- ✅ Positive: Alignment with research literature
- ✅ Positive: Intuitive interpretation
- ✅ Positive: Magnitude-invariant (focuses on direction)
- ❌ Negative: Less sensitive to magnitude changes (but not needed here)
- ⚠️ Include Euclidean and Manhattan for completeness

**Alternatives Considered:**
1. Euclidean only: Rejected as magnitude-dependent
2. Multiple primary metrics: Rejected for clarity in results

---

### ADR-005: Plugin Architecture with Lifecycle Hooks

**Status:** Accepted  
**Date:** 2025-11-18  
**Context:**  
Need extensible design for adding new agents and behaviors.

**Decision:**  
Implement abstract `BaseAgent` with lifecycle hooks: `before_translate()`, `after_translate()`, `on_error()`.

**Rationale:**
- **Extensibility:** Easy to add logging, monitoring, caching
- **Open/Closed Principle:** Open for extension, closed for modification
- **Testability:** Hooks can be mocked in tests
- **Separation of Concerns:** Cross-cutting concerns separated from core logic

**Consequences:**
- ✅ Positive: Future-proof architecture
- ✅ Positive: Easy to add new agents
- ✅ Positive: Enables advanced features (caching, rate limiting)
- ❌ Negative: Slightly more complex than simple interface

---

### ADR-006: Configuration Management

**Status:** Accepted  
**Date:** 2025-11-18  
**Context:**  
System has many configurable parameters (error rates, timeouts, paths).

**Decision:**  
Use YAML configuration files with singleton Settings class.

**Rationale:**
- **Readability:** YAML is human-readable and writable
- **Hierarchy:** Supports nested configuration
- **Comments:** Allows inline documentation
- **Type Safety:** PyYAML parses to native Python types
- **No Code Changes:** Users configure without touching source

**Consequences:**
- ✅ Positive: Easy user customization
- ✅ Positive: No hardcoded values in source
- ✅ Positive: Different configs for different experiments
- ❌ Negative: Need to validate configuration

---

## 5. Data Flow

### 5.1 End-to-End Data Flow

```
Input Sentence (Clean English)
        │
        ▼
┌───────────────────┐
│  Error Injection  │ ← error_rate parameter
└─────────┬─────────┘
          │
          ▼
Corrupted Sentence
          │
          ├──────────────────────────────┐
          │                              │
          ▼                              ▼
┌──────────────────┐            ┌──────────────────┐
│ Store Original   │            │ Translation      │
│ Embedding        │            │ Chain: EN→FR     │
└──────────────────┘            └─────────┬────────┘
          │                              │
          │                              ▼
          │                     French Translation
          │                              │
          │                              ▼
          │                     ┌──────────────────┐
          │                     │ Translation      │
          │                     │ Chain: FR→HE     │
          │                     └─────────┬────────┘
          │                              │
          │                              ▼
          │                     Hebrew Translation
          │                              │
          │                              ▼
          │                     ┌──────────────────┐
          │                     │ Translation      │
          │                     │ Chain: HE→EN     │
          │                     └─────────┬────────┘
          │                              │
          │                              ▼
          │                     Final English Output
          │                              │
          │                              ▼
          │                     ┌──────────────────┐
          │                     │ Store Final      │
          │                     │ Embedding        │
          │                     └─────────┬────────┘
          │                              │
          └──────────────┬───────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Calculate        │
                │ Vector Distance  │
                └────────┬─────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Store Results   │
                │ in Database     │
                └────────┬─────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Statistical     │
                │ Analysis        │
                └────────┬─────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Visualization   │
                └─────────────────┘
```

### 5.2 Database Schema

```sql
-- Sentences table
CREATE TABLE sentences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    word_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Experiments table
CREATE TABLE experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sentence_id INTEGER NOT NULL,
    agent_type TEXT NOT NULL,
    error_rate REAL NOT NULL,
    corrupted_text TEXT NOT NULL,
    actual_error_rate REAL NOT NULL,
    translation_fr TEXT,
    translation_he TEXT,
    translation_en TEXT,
    duration_seconds REAL,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sentence_id) REFERENCES sentences(id)
);

-- Embeddings table
CREATE TABLE embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id INTEGER NOT NULL,
    original_embedding BLOB NOT NULL,
    final_embedding BLOB NOT NULL,
    cosine_distance REAL NOT NULL,
    euclidean_distance REAL NOT NULL,
    manhattan_distance REAL NOT NULL,
    FOREIGN KEY (experiment_id) REFERENCES experiments(id)
);

-- Indexes for query performance
CREATE INDEX idx_experiments_agent ON experiments(agent_type);
CREATE INDEX idx_experiments_error_rate ON experiments(error_rate);
CREATE INDEX idx_experiments_sentence ON experiments(sentence_id);
```

---

## 6. Component Specifications

### 6.1 Agent Layer

**Responsibility:** Interface with LLM CLI tools for translation

**Key Classes:**
- `BaseAgent`: Abstract base with lifecycle hooks
- `CursorAgent`, `GeminiAgent`, `ClaudeAgent`, `OllamaAgent`: Concrete implementations
- `AgentFactory`: Creates agent instances

**Interfaces:**
```python
translate(text: str, source_lang: str, target_lang: str) -> TranslationResult
validate_input(text: str, source_lang: str, target_lang: str) -> None
```

**Error Handling:**
- Retry logic (3 attempts with exponential backoff)
- Timeout handling (30s default)
- Graceful degradation

### 6.2 Translation Layer

**Responsibility:** Orchestrate translation chains and error injection

**Key Classes:**
- `TranslationChain`: Manages EN→FR→HE→EN flow
- `ErrorInjector`: Introduces controlled spelling errors

**Algorithms:**
- Error injection uses random selection with seeding for reproducibility
- Maintains word boundaries and punctuation
- Four error types: swap, deletion, insertion, substitution

### 6.3 Analysis Layer

**Responsibility:** Calculate embeddings and distances

**Key Classes:**
- `EmbeddingEngine`: Generates vector embeddings
- `DistanceMetrics`: Computes distance measures
- `StatisticalAnalysis`: Performs statistical tests

**Performance:**
- Batch processing for embeddings (32 sentences/batch)
- Caching to avoid re-computation
- NumPy vectorization for distance calculations

### 6.4 Data Layer

**Responsibility:** Persist and retrieve experiment data

**Key Classes:**
- `ExperimentStorage`: Database interface
- `SentenceGenerator`: Create/load test sentences

**Features:**
- ACID transactions
- Query builders for complex analysis
- Efficient blob storage for embeddings

### 6.5 Visualization Layer

**Responsibility:** Present results graphically

**Key Classes:**
- `StaticPlots`: Publication-quality figures (300 DPI)
- `Dashboard`: Interactive Dash application

**Visualizations:**
- Error rate vs distance (line plot with confidence intervals)
- Distribution box plots
- Agent comparison heatmaps
- Vector space projections (t-SNE, UMAP)

---

## 7. API and Interfaces

### 7.1 Public API

#### Agent Creation
```python
from src.agents.factory import AgentFactory

agent = AgentFactory.create('cursor', config={'timeout': 30})
result = agent.translate("Hello world", "en", "fr")
```

#### Translation Chain
```python
from src.translation.chain import TranslationChain

chain = TranslationChain(agent=agent)
result = chain.execute_chain(
    text="The quick brown fox jumps",
    error_rate=0.25
)
```

#### Vector Analysis
```python
from src.analysis.embeddings import EmbeddingEngine
from src.analysis.distance import DistanceMetrics

engine = EmbeddingEngine()
emb1 = engine.encode("Original text")
emb2 = engine.encode("Translated text")

distance = DistanceMetrics.cosine(emb1, emb2)
```

#### Experiment Execution
```python
from src.data.storage import ExperimentStorage
from src.config import get_settings

settings = get_settings()
storage = ExperimentStorage(settings.get_database_path())

# Run experiments
for error_rate in [0, 0.1, 0.25, 0.35, 0.5]:
    result = chain.execute_chain(text, error_rate)
    storage.store_result(result)
```

### 7.2 Configuration API

```python
from src.config import get_settings

settings = get_settings()

# Get agent config
cursor_config = settings.get_agent_config('cursor')

# Get experiment parameters
error_rates = settings.get_error_rates()  # [0, 10, 25, 35, 50]

# Get paths
db_path = settings.get_database_path()
results_dir = settings.get_results_dir()
```

### 7.3 CLI Interface (Planned)

```bash
# Run experiments
python -m src.main experiment --agent cursor --sentences data/input_sentences.json

# Generate visualizations
python -m src.main visualize --db data/experiments.db --output results/figures/

# Launch dashboard
python -m src.main dashboard --port 8050
```

---

## 8. Deployment Architecture

### 8.1 Local Development

```
Developer Machine
├── Python 3.8+ (venv)
├── sentence-transformers models (~80MB cached)
├── SQLite database (data/experiments.db)
├── CLI tools (cursor-agent, etc.)
└── Results directory (generated figures)
```

### 8.2 Research Environment

```
Research Workstation
├── All components local
├── Jupyter Lab for analysis
├── Dashboard on localhost:8050
└── No external network dependencies (after setup)
```

---

## 9. Performance Considerations

### 9.1 Bottlenecks
1. **LLM translation:** 5-15s per translation (3 translations per chain)
2. **Embedding generation:** ~20ms per sentence (negligible)
3. **Distance calculation:** <1ms (NumPy optimized)

### 9.2 Optimizations
- Batch embedding generation (32 sentences/batch)
- Database indexing on frequently queried columns
- WAL mode for SQLite (better concurrency)
- Caching of embeddings (avoid recomputation)

### 9.3 Scalability
- Current design: 10-20 sentences, single machine
- Potential: Parallel agent calls, distributed experiments
- Limit: CLI agent availability and rate limits

---

## 10. Security Considerations

1. **No Secrets:** CLI tools handle authentication externally
2. **Input Validation:** All user inputs validated
3. **Subprocess Safety:** No shell=True, argument escaping
4. **File Permissions:** Database and results directories properly secured
5. **Dependencies:** Regular updates for security patches

---

## 11. Future Extensibility

### Planned Extensions
1. **New Agents:** Easy to add via BaseAgent interface
2. **New Metrics:** Pluggable distance metric system
3. **New Languages:** Configurable language pairs
4. **Parallel Execution:** Thread pool for concurrent translations
5. **Export Formats:** CSV, JSON, LaTeX tables

### Extension Points
- Agent lifecycle hooks for custom behavior
- Distance metric registration system
- Visualization plugin architecture
- Custom error injection strategies

---

## Document Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-18 | Initial architecture documentation | System |

---

## References

1. C4 Model for Visualizing Software Architecture - Simon Brown
2. Documenting Software Architectures: Views and Beyond - Clements et al.
3. ISO/IEC 25010:2011 Software Quality Model
4. Clean Architecture - Robert C. Martin
5. Design Patterns: Elements of Reusable Object-Oriented Software - Gang of Four

