# 🚀 Easy Start Guide
## Get Running in 30 Seconds!

---

## ⚡ Quickest Way to Start

```bash
# 1. Activate your virtual environment
source venv/bin/activate

# 2. Run the interactive menu
python run.py
```

That's it! The menu guides you through everything. 🎉

---

## 📋 What You Can Do

### Option 1: Run Experiments
- Translates sentences through language chains
- Tests different error rates
- Saves results to database

### Option 2: Launch Dashboard  
- Interactive web visualization
- View results in real-time
- Compare agents and error rates
- Opens at http://localhost:8050

### Option 3: Generate Visualizations
- Creates publication-quality graphs (300 DPI)
- Error rate vs distance plots
- Box plots, heatmaps, scatter plots
- Saved to `results/figures/`

### Option 4: Run Tests
- Executes full test suite
- Shows coverage report
- Verifies everything works

### Option 5: View Statistics
- Shows database summary
- Number of experiments
- Success rates
- Agents and error rates tested

---

## 💡 First Time? Try This:

```bash
python run.py
```

Then:
1. Select **Option 5** (View Statistics) - See current state
2. Select **Option 4** (Run Tests) - Verify installation
3. When ready to experiment:
   - Select **Option 1** (Run Experiments)
   - Choose an agent (cursor/ollama recommended)
   - Start with 2-3 sentences
4. Select **Option 2** (Launch Dashboard) - View results!

---

## 🎮 Interactive Menu Example

```
============================================================
  Translation Chain Vector Distance Analysis
============================================================

1. Run Experiments
2. Launch Dashboard
3. Generate Visualizations
4. Run Tests
5. View Database Statistics
6. Exit

------------------------------------------------------------
Select option (1-6): 1

📊 Running Experiments...
------------------------------------------------------------

Available agents:
  1. cursor   - Cursor Agent (cursor-agent)
  2. gemini   - Google Gemini CLI
  3. claude   - Anthropic Claude CLI
  4. ollama   - Ollama (local)

Select agent (1-4) [default: 1]: 4

Number of sentences to test [default: 5]: 3

🚀 Starting experiments with ollama agent...
   Testing 3 sentences across 5 error rates
   This may take several minutes...

✅ Experiments Complete!
   Total: 15
   Successful: 15
   Success Rate: 100.0%
```

---

## ⚡ Command-Line Alternative

If you prefer commands:

```bash
# See all commands
python cli.py --help

# Run experiments
python cli.py experiment --agent cursor --sentences 5

# Launch dashboard
python cli.py dashboard

# View stats
python cli.py stats
```

---

## 🆘 Troubleshooting

### "Agent not found" Error
**Solution:** Install the agent first:
- **Ollama** (easiest, local, free): https://ollama.ai/
- **Others**: See README.md installation section

### NumPy Warning
```
A module that was compiled using NumPy 1.x cannot be run in NumPy 2.3.5...
```
**This is OK!** It's just a warning. Everything still works.

To silence it (optional):
```bash
pip install "numpy<2"
```

### Database Empty
If you see "0 experiments", you need to run experiments first:
```bash
python run.py
# Select Option 1: Run Experiments
```

---

## 📚 More Information

- **Full Documentation:** `README.md`
- **Installation Help:** `INSTALL.md`
- **Usage Examples:** `USAGE_GUIDE.md`
- **CLI Reference:** `python cli.py --help`

---

**🎉 You're ready to go! Run `python run.py` to start!**

