# API Documentation
## Translation Chain Vector Distance Analysis

**Version:** 1.0  
**Date:** November 18, 2025

---

## Table of Contents

1. [Agent API](#agent-api)
2. [Translation API](#translation-api)
3. [Analysis API](#analysis-api)
4. [Data API](#data-api)
5. [Visualization API](#visualization-api)
6. [Configuration API](#configuration-api)

---

## 1. Agent API

### AgentFactory

Factory class for creating translation agent instances.

#### `AgentFactory.create(agent_type, config=None)`

Create an agent instance.

**Parameters:**
- `agent_type` (str): Agent type ('cursor', 'gemini', 'claude', 'ollama')
- `config` (dict, optional): Configuration dictionary

**Returns:**
- `BaseAgent`: Agent instance

**Example:**
```python
from src.agents.factory import AgentFactory

agent = AgentFactory.create('cursor', {'timeout': 60})
```

#### `AgentFactory.get_supported_agents()`

Get list of supported agent types.

**Returns:**
- `list`: List of agent type strings

#### `AgentFactory.register_agent(agent_type, agent_class)`

Register a new agent type.

**Parameters:**
- `agent_type` (str): Unique identifier
- `agent_class` (type): Agent class inheriting from BaseAgent

### BaseAgent

Abstract base class for translation agents.

#### `agent.translate(text, source_lang, target_lang)`

Translate text between languages.

**Parameters:**
- `text` (str): Text to translate
- `source_lang` (str): Source language code ('en', 'fr', 'he')
- `target_lang` (str): Target language code

**Returns:**
- `TranslationResult`: Result object with translated text and metadata

**Raises:**
- `ValueError`: If inputs are invalid
- `RuntimeError`: If translation fails

**Example:**
```python
result = agent.translate("Hello world", "en", "fr")
print(result.translated_text)  # "Bonjour le monde"
print(result.duration_seconds)  # 2.5
```

---

## 2. Translation API

### TranslationChain

Orchestrates multi-stage translation chain.

#### `TranslationChain(agent, error_injector=None)`

Initialize translation chain.

**Parameters:**
- `agent` (BaseAgent): Translation agent to use
- `error_injector` (ErrorInjector, optional): Custom error injector

#### `chain.execute_chain(text, error_rate=0.0)`

Execute complete EN→FR→HE→EN translation chain.

**Parameters:**
- `text` (str): Original English text
- `error_rate` (float): Error rate (0.0 to 1.0)

**Returns:**
- `ChainResult`: Complete chain execution results

**Example:**
```python
from src.translation.chain import TranslationChain

chain = TranslationChain(agent)
result = chain.execute_chain("Hello world", error_rate=0.25)

print(f"Success: {result.success}")
print(f"Original: {result.original_text}")
print(f"Corrupted: {result.corrupted_text}")
print(f"Final: {result.translation_en}")
print(f"Duration: {result.total_duration_seconds}s")
```

### ErrorInjector

Injects controlled spelling errors into text.

#### `ErrorInjector(seed=None)`

Initialize error injector.

**Parameters:**
- `seed` (int, optional): Random seed for reproducibility

#### `injector.inject_errors(text, error_rate, maintain_punctuation=True, maintain_capitalization=True)`

Inject spelling errors.

**Parameters:**
- `text` (str): Input text
- `error_rate` (float): Target error rate (0.0 to 1.0)
- `maintain_punctuation` (bool): Preserve punctuation
- `maintain_capitalization` (bool): Preserve capitalization

**Returns:**
- `str`: Corrupted text

**Example:**
```python
from src.translation.error_injector import ErrorInjector

injector = ErrorInjector(seed=42)
corrupted = injector.inject_errors("Hello world", 0.5)
print(corrupted)  # "Helo wrold" (example)
```

---

## 3. Analysis API

### EmbeddingEngine

Generates vector embeddings using sentence-transformers.

#### `EmbeddingEngine(model_name='all-MiniLM-L6-v2', device='cpu', batch_size=32)`

Initialize embedding engine.

**Parameters:**
- `model_name` (str): Sentence-transformers model name
- `device` (str): 'cpu' or 'cuda'
- `batch_size` (int): Batch size for encoding

#### `engine.encode(texts, use_cache=True, show_progress=False)`

Generate embeddings for text(s).

**Parameters:**
- `texts` (str or list): Single text or list of texts
- `use_cache` (bool): Use cached embeddings
- `show_progress` (bool): Show progress bar

**Returns:**
- `np.ndarray`: Embeddings array

**Example:**
```python
from src.analysis.embeddings import EmbeddingEngine

engine = EmbeddingEngine()
embedding = engine.encode("Hello world")
print(embedding.shape)  # (384,)

# Batch encoding
embeddings = engine.encode(["Hello", "World"])
print(embeddings.shape)  # (2, 384)
```

### DistanceMetrics

Computes distance metrics between embeddings.

#### `DistanceMetrics.cosine(embedding1, embedding2)`

Calculate cosine distance.

**Parameters:**
- `embedding1` (np.ndarray): First embedding
- `embedding2` (np.ndarray): Second embedding

**Returns:**
- `float`: Cosine distance (0 to 2)

#### `DistanceMetrics.euclidean(embedding1, embedding2)`

Calculate Euclidean distance.

#### `DistanceMetrics.manhattan(embedding1, embedding2)`

Calculate Manhattan distance.

#### `DistanceMetrics.all_metrics(embedding1, embedding2)`

Calculate all distance metrics.

**Returns:**
- `dict`: Dictionary with 'cosine', 'euclidean', 'manhattan' keys

**Example:**
```python
from src.analysis.distance import DistanceMetrics

distances = DistanceMetrics.all_metrics(emb1, emb2)
print(f"Cosine: {distances['cosine']:.4f}")
print(f"Euclidean: {distances['euclidean']:.4f}")
```

### StatisticalAnalysis

Performs statistical analysis on results.

#### `StatisticalAnalysis.correlation(x, y, method='pearson')`

Calculate correlation.

**Parameters:**
- `x` (np.ndarray): First variable
- `y` (np.ndarray): Second variable
- `method` (str): 'pearson' or 'spearman'

**Returns:**
- `tuple`: (correlation_coefficient, p_value)

#### `StatisticalAnalysis.linear_regression(x, y)`

Perform linear regression.

**Returns:**
- `dict`: Regression results with slope, intercept, r_squared, p_value

**Example:**
```python
from src.analysis.statistics import StatisticalAnalysis

corr, pval = StatisticalAnalysis.correlation(error_rates, distances)
print(f"Correlation: {corr:.4f}, p-value: {pval:.6f}")
```

---

## 4. Data API

### ExperimentStorage

SQLite database interface for experiment results.

#### `ExperimentStorage(db_path)`

Initialize storage.

**Parameters:**
- `db_path` (Path): Path to SQLite database file

#### `storage.store_experiment(sentence_id, chain_result, embeddings, distances)`

Store complete experiment results.

**Parameters:**
- `sentence_id` (int): Sentence ID
- `chain_result` (ChainResult): Translation chain results
- `embeddings` (dict): Dict with 'original' and 'final' embeddings
- `distances` (dict): Dict with distance metrics

**Returns:**
- `int`: Experiment ID

#### `storage.get_all_results()`

Get all experiment results.

**Returns:**
- `list`: List of result dictionaries

#### `storage.get_results_by_agent(agent_type)`

Filter results by agent.

#### `storage.get_statistics()`

Get database statistics.

**Example:**
```python
from src.data.storage import ExperimentStorage
from pathlib import Path

storage = ExperimentStorage(Path('data/experiments.db'))
results = storage.get_all_results()
stats = storage.get_statistics()
print(f"Total experiments: {stats['total_experiments']}")
```

### ExperimentRunner

High-level experiment orchestration.

#### `ExperimentRunner(agent_type, config_path=None)`

Initialize experiment runner.

**Parameters:**
- `agent_type` (str): Agent type to use
- `config_path` (str, optional): Path to config file

#### `runner.run_single_experiment(sentence, error_rate)`

Run single experiment.

**Returns:**
- `int`: Experiment ID or None if failed

#### `runner.run_full_experiment_suite(num_sentences=None, error_rates=None)`

Run complete experiment suite.

**Returns:**
- `dict`: Results summary

**Example:**
```python
from src.data.experiment_runner import ExperimentRunner

runner = ExperimentRunner('cursor')
results = runner.run_full_experiment_suite(
    num_sentences=10,
    error_rates=[0.0, 0.25, 0.5]
)
print(f"Success rate: {results['success_rate']:.1%}")
```

---

## 5. Visualization API

### StaticPlots

Generate publication-quality static graphs.

#### `StaticPlots(output_dir, dpi=300)`

Initialize plot generator.

**Parameters:**
- `output_dir` (Path): Directory to save figures
- `dpi` (int): Resolution in dots per inch

#### `plotter.plot_error_rate_vs_distance(data, metric='cosine_distance', save_name='error_vs_distance')`

Generate error rate vs distance plot.

**Parameters:**
- `data` (pd.DataFrame): Experiment data
- `metric` (str): Distance metric column name
- `save_name` (str): Filename without extension

**Returns:**
- `Path`: Path to saved figure

#### `plotter.generate_all_plots(data)`

Generate all standard plots.

**Returns:**
- `dict`: Dictionary mapping plot names to file paths

**Example:**
```python
from src.visualization.plots import StaticPlots
from pathlib import Path
import pandas as pd

plotter = StaticPlots(Path('results/figures'), dpi=300)
plots = plotter.generate_all_plots(data)
print(f"Generated {len(plots)} plots")
```

### TranslationDashboard

Interactive Plotly Dash dashboard.

#### `create_dashboard(config_path=None)`

Create dashboard instance.

**Returns:**
- `TranslationDashboard`: Dashboard instance

#### `dashboard.run(debug=False)`

Run dashboard server.

**Example:**
```python
from src.visualization.dashboard import create_dashboard

dashboard = create_dashboard()
dashboard.run(debug=False)
# Visit http://localhost:8050
```

---

## 6. Configuration API

### Settings

Configuration management.

#### `get_settings(config_path=None)`

Get singleton settings instance.

**Parameters:**
- `config_path` (str, optional): Path to config file

**Returns:**
- `Settings`: Settings instance

#### `settings.get(key, default=None)`

Get configuration value.

**Parameters:**
- `key` (str): Configuration key (supports dot notation)
- `default`: Default value if not found

#### `settings.get_agent_config(agent_type)`

Get agent-specific configuration.

**Example:**
```python
from src.config import get_settings

settings = get_settings()
timeout = settings.get('agents.cursor.timeout', 30)
error_rates = settings.get_error_rates()
db_path = settings.get_database_path()
```

---

## Complete Example

```python
# 1. Setup
from src.agents.factory import AgentFactory
from src.translation.chain import TranslationChain
from src.analysis.embeddings import EmbeddingEngine
from src.analysis.distance import DistanceMetrics
from src.data.storage import ExperimentStorage
from pathlib import Path

# 2. Create components
agent = AgentFactory.create('cursor')
chain = TranslationChain(agent)
engine = EmbeddingEngine()
storage = ExperimentStorage(Path('data/experiments.db'))

# 3. Run experiment
sentence = "The quick brown fox jumps over the lazy dog"
chain_result = chain.execute_chain(sentence, error_rate=0.25)

# 4. Analyze
original_emb = engine.encode(sentence)
final_emb = engine.encode(chain_result.translation_en)
distances = DistanceMetrics.all_metrics(original_emb, final_emb)

# 5. Store results
sentence_id = storage.get_or_create_sentence(sentence)
exp_id = storage.store_experiment(
    sentence_id,
    chain_result,
    {'original': original_emb, 'final': final_emb},
    distances
)

print(f"Experiment {exp_id} completed!")
print(f"Cosine distance: {distances['cosine']:.4f}")
```

---

## Error Handling

All API functions raise appropriate exceptions:

- `ValueError`: Invalid input parameters
- `RuntimeError`: Operation failed
- `FileNotFoundError`: Required file missing
- `TypeError`: Incorrect type

Always wrap API calls in try-except blocks for production use.

---

**API Version:** 1.0  
**Last Updated:** November 18, 2025

