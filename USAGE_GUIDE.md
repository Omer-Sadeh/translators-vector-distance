# Usage Guide
## Translation Chain Vector Distance Analysis

**Quick Reference for Getting Started**

---

## 🎯 Three Ways to Use This System

### 1. 🎮 Interactive Menu (Easiest!)

**Best for:** First-time users, exploratory work

```bash
python run.py
```

**What you get:**
- Numbered menu with clear options
- Interactive prompts for configuration
- User-friendly error messages
- No need to remember commands

**Perfect when:**
- You're just starting out
- You want to explore features
- You prefer guided experience

---

### 2. ⚡ Command-Line Interface (Powerful!)

**Best for:** Automation, scripting, advanced users

```bash
# Quick examples
python cli.py experiment --agent cursor --sentences 10
python cli.py dashboard
python cli.py visualize
python cli.py test --coverage
python cli.py stats
```

**What you get:**
- Full control with flags and options
- Scriptable and automatable
- Faster for repeated tasks
- Detailed help with `--help`

**Perfect when:**
- You know what you want to do
- You're scripting workflows
- You want maximum control

---

### 3. 🐍 Python API (Most Flexible!)

**Best for:** Integration, custom workflows, research scripts

```python
from src.data.experiment_runner import ExperimentRunner

runner = ExperimentRunner('cursor')
results = runner.run_full_experiment_suite(num_sentences=5)
```

**What you get:**
- Full programmatic control
- Integration with your code
- Direct access to all features
- Maximum flexibility

**Perfect when:**
- Integrating with other Python code
- Building custom analysis pipelines
- Need fine-grained control

---

## 🚀 Quick Start Workflows

### Workflow 1: First Time Setup

```bash
# 1. Install (one time)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Run interactive menu
python run.py

# 3. Select Option 1: Run Experiments
# 4. Select Option 2: Launch Dashboard
# 5. View results at http://localhost:8050
```

### Workflow 2: Running Experiments

**Interactive:**
```bash
python run.py
# Choose: 1. Run Experiments
# Select agent: cursor / gemini / claude / ollama
# Enter number of sentences: 10
```

**CLI:**
```bash
python cli.py experiment --agent cursor --sentences 10
```

**Python:**
```python
from src.data.experiment_runner import ExperimentRunner

runner = ExperimentRunner('cursor')
results = runner.run_full_experiment_suite(num_sentences=10)
print(f"Success rate: {results['success_rate']:.1%}")
```

### Workflow 3: Visualizing Results

**Interactive:**
```bash
python run.py
# Choose: 3. Generate Visualizations
```

**CLI:**
```bash
python cli.py visualize --output results/figures --dpi 300
```

**Python:**
```python
from src.visualization.plots import StaticPlots
from src.data.storage import ExperimentStorage
from pathlib import Path
import pandas as pd

storage = ExperimentStorage(Path('data/experiments.db'))
data = pd.DataFrame(storage.get_all_results())
plotter = StaticPlots(Path('results/figures'), dpi=300)
plots = plotter.generate_all_plots(data)
```

### Workflow 4: Viewing Results

**Interactive:**
```bash
python run.py
# Choose: 2. Launch Dashboard
# Open browser to http://localhost:8050
```

**CLI:**
```bash
python cli.py dashboard --port 8050
```

### Workflow 5: Running Tests

**Interactive:**
```bash
python run.py
# Choose: 4. Run Tests
```

**CLI:**
```bash
python cli.py test --coverage
```

**Direct:**
```bash
pytest --cov=src --cov-report=html
```

---

## 📋 CLI Command Reference

### Experiment Command

```bash
python cli.py experiment [OPTIONS]

Options:
  --agent, -a       Agent type: cursor, gemini, claude, ollama
  --sentences, -s   Number of sentences to test
  --error-rates, -e Comma-separated rates: "0,10,25,50"
  --config, -c      Path to config file

Examples:
  # Basic usage
  python cli.py experiment --agent cursor
  
  # Custom configuration
  python cli.py experiment --agent ollama --sentences 20 --error-rates "0,25,50"
  
  # Use custom config
  python cli.py experiment --agent cursor --config my_config.yaml
```

### Dashboard Command

```bash
python cli.py dashboard [OPTIONS]

Options:
  --host            Host to bind (default: 127.0.0.1)
  --port, -p        Port to bind (default: 8050)
  --debug           Enable debug mode
  --config, -c      Path to config file

Examples:
  # Basic usage
  python cli.py dashboard
  
  # Custom port
  python cli.py dashboard --port 8888
  
  # Debug mode
  python cli.py dashboard --debug
```

### Visualize Command

```bash
python cli.py visualize [OPTIONS]

Options:
  --output, -o      Output directory
  --dpi             Image resolution (default: 300)
  --config, -c      Path to config file

Examples:
  # Basic usage
  python cli.py visualize
  
  # High resolution
  python cli.py visualize --dpi 600 --output results/publication
```

### Test Command

```bash
python cli.py test [OPTIONS]

Options:
  --coverage        Generate coverage report
  --verbose, -v     Verbose output
  --file, -f        Specific test file

Examples:
  # Run all tests
  python cli.py test
  
  # With coverage
  python cli.py test --coverage
  
  # Specific file
  python cli.py test --file tests/test_agents.py
```

### Stats Command

```bash
python cli.py stats [OPTIONS]

Options:
  --detailed, -d    Show detailed statistics
  --config, -c      Path to config file

Examples:
  # Basic stats
  python cli.py stats
  
  # Detailed stats
  python cli.py stats --detailed
```

### Analyze Command

```bash
python cli.py analyze

# Opens Jupyter Lab with analysis notebook
```

---

## 🎓 Example Scenarios

### Scenario 1: Research Paper

```bash
# 1. Run comprehensive experiments
python cli.py experiment --agent cursor --sentences 15 --error-rates "0,10,25,35,50"

# 2. Generate publication-quality figures
python cli.py visualize --dpi 300

# 3. Open analysis notebook for statistical analysis
python cli.py analyze

# 4. View results interactively
python cli.py dashboard
```

### Scenario 2: Quick Test

```bash
# Run quick test with 5 sentences
python cli.py experiment --agent ollama --sentences 5 --error-rates "0,25"

# Check results
python cli.py stats
```

### Scenario 3: Agent Comparison

```bash
# Test all agents
for agent in cursor gemini claude ollama; do
    python cli.py experiment --agent $agent --sentences 10
done

# View comparison in dashboard
python cli.py dashboard
```

### Scenario 4: Automated Pipeline

Create a script `run_pipeline.sh`:

```bash
#!/bin/bash

# Run experiments
python cli.py experiment --agent cursor --sentences 15

# Generate visualizations
python cli.py visualize --output results/latest

# Run tests
python cli.py test --coverage

# Show final stats
python cli.py stats --detailed

echo "Pipeline complete! View dashboard: python cli.py dashboard"
```

---

## 🔧 Configuration Tips

### Using Custom Config

```yaml
# my_config.yaml
experiments:
  error_rates: [0, 15, 30, 45]
  num_sentences: 20

agents:
  cursor:
    timeout: 60
```

```bash
python cli.py experiment --config my_config.yaml
```

### Setting Defaults

Edit `config/experiment_config.yaml` to set project-wide defaults.

---

## 📝 Tips & Tricks

### Tip 1: Start Small
```bash
# Test with 2-3 sentences first
python cli.py experiment --agent cursor --sentences 3 --error-rates "0,25"
```

### Tip 2: Check Before Big Runs
```bash
# Verify agent works
python cli.py stats
```

### Tip 3: Use Screen/Tmux for Long Runs
```bash
# Long experiments in background
tmux new -s experiments
python cli.py experiment --agent cursor --sentences 20
# Ctrl+B, D to detach
```

### Tip 4: Export Results
```python
# In Python
from src.data.storage import ExperimentStorage
import pandas as pd

storage = ExperimentStorage(Path('data/experiments.db'))
data = pd.DataFrame(storage.get_all_results())
data.to_csv('results/experiments.csv', index=False)
```

---

## ❓ Common Questions

**Q: Which way should I use?**
A: Start with `python run.py` (interactive menu) to learn, then graduate to CLI for regular use.

**Q: Can I use multiple agents?**
A: Yes! Run experiments separately for each agent, then view all results in the dashboard.

**Q: How do I stop the dashboard?**
A: Press `Ctrl+C` in the terminal.

**Q: Where are results stored?**
A: Database: `data/experiments.db`, Figures: `results/figures/`

**Q: Can I run experiments without a CLI agent?**
A: No, you need at least one installed. Ollama is the easiest (free, local, no API key).

---

## 🆘 Getting Help

```bash
# General help
python cli.py --help

# Command-specific help
python cli.py experiment --help
python cli.py dashboard --help
python cli.py visualize --help

# Or check documentation
cat README.md
cat INSTALL.md
```

---

**Happy Experimenting! 🚀**

