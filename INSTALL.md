# Installation Guide
## Translation Chain Vector Distance Analysis

**Quick Fix for Installation Issues**

---

## Issue: "externally-managed-environment" Error

If you see this error when running `pip install -r requirements.txt`, it means your Python is managed by Homebrew and you need to use a virtual environment.

---

## ✅ Solution: Create Virtual Environment

### Step 1: Create Virtual Environment

```bash
cd /Users/osadeh/Documents/Github/translators-vector-distance
python -m venv venv
```

### Step 2: Activate Virtual Environment

```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This should now work without errors!

---

## Verification

```bash
# Check installation
python -c "import sentence_transformers; print('✓ Dependencies installed successfully!')"
```

---

## Complete Installation Commands

```bash
# All in one go:
cd /Users/osadeh/Documents/Github/translators-vector-distance
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Troubleshooting

### Issue: "No module named 'sentence_transformers'"

**Solution:** Make sure virtual environment is activated:
```bash
source venv/bin/activate  # You should see (venv) in prompt
```

### Issue: Still getting externally-managed error

**Solution:** Make sure you're using the venv Python:
```bash
which python  # Should show: .../venv/bin/python
```

### Issue: Slow installation

**Solution:** This is normal. sentence-transformers downloads ~400MB of models on first use.

---

## Next Steps After Installation

### 1. Quick Start - Interactive Menu

The easiest way to get started:

```bash
python run.py
```

This launches an interactive menu that guides you through:
- Running experiments
- Launching dashboard
- Generating visualizations
- Running tests
- Viewing statistics

### 2. Command-Line Interface

For more control:

```bash
# See all available commands
python cli.py --help

# Run experiments
python cli.py experiment --agent cursor --sentences 5

# Launch dashboard
python cli.py dashboard

# Run tests
python cli.py test --coverage
```

### 3. Verify Installation

```bash
# Quick verification
python -c "
from src.data.generator import SentenceGenerator
gen = SentenceGenerator()
print(f'✓ Loaded {len(gen.sentences)} test sentences')
print('✓ Installation successful!')
"
```

---

## Python Version Compatibility

**Tested with:**
- Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.14

**Minimum Required:** Python 3.8+

---

## Alternative: Using pipx (Advanced)

If you prefer system-wide installation:

```bash
brew install pipx
pipx install sentence-transformers
# ... install other packages
```

But **virtual environment is recommended** for this project!

---

## Deactivating Virtual Environment

When done working:

```bash
deactivate
```

---

## Keeping Virtual Environment Clean

```bash
# To reinstall dependencies:
pip install -r requirements.txt --force-reinstall

# To upgrade dependencies:
pip install -r requirements.txt --upgrade
```

---

**Installation Help:** If issues persist, check Python version with `python --version` (should be 3.8+)

