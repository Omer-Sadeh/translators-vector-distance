#!/usr/bin/env python3
"""
Quick Start Script for Translation Chain Vector Distance Analysis

Usage:
    python run.py
    
This script provides an interactive menu for common tasks.
"""

import sys
from pathlib import Path

def print_menu():
    """Print main menu."""
    print("\n" + "="*60)
    print("  Translation Chain Vector Distance Analysis")
    print("="*60)
    print("\n1. Run Experiments")
    print("2. Launch Dashboard")
    print("3. Generate Visualizations")
    print("4. Run Tests")
    print("5. View Database Statistics")
    print("6. Exit")
    print("\n" + "-"*60)

def run_experiments():
    """Run experiment suite."""
    print("\n📊 Running Experiments...")
    print("-" * 60)
    
    # Check for available agents
    print("\nAvailable agents:")
    print("  1. cursor   - Cursor Agent (cursor-agent)")
    print("  2. gemini   - Google Gemini CLI")
    print("  3. claude   - Anthropic Claude CLI")
    print("  4. ollama   - Ollama (local)")
    
    agent_choice = input("\nSelect agent (1-4) [default: 1]: ").strip() or "1"
    agent_map = {"1": "cursor", "2": "gemini", "3": "claude", "4": "ollama"}
    agent_type = agent_map.get(agent_choice, "cursor")
    
    num_sentences = input("Number of sentences to test [default: 5]: ").strip() or "5"
    
    print(f"\n🚀 Starting experiments with {agent_type} agent...")
    print(f"   Testing {num_sentences} sentences across 5 error rates")
    print(f"   This may take several minutes...\n")
    
    try:
        from src.data.experiment_runner import ExperimentRunner
        
        runner = ExperimentRunner(agent_type)
        results = runner.run_full_experiment_suite(
            num_sentences=int(num_sentences)
        )
        
        print("\n✅ Experiments Complete!")
        print(f"   Total: {results['total_experiments']}")
        print(f"   Successful: {results['successful_experiments']}")
        print(f"   Success Rate: {results['success_rate']:.1%}")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {agent_type} CLI tool not found!")
        print(f"   Please install {agent_type} first.")
        print(f"   See README.md for installation instructions.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def launch_dashboard():
    """Launch interactive dashboard."""
    print("\n📈 Launching Dashboard...")
    print("-" * 60)
    print("\n🌐 Dashboard will open at: http://localhost:8050")
    print("   Press Ctrl+C to stop the server\n")
    
    try:
        from src.visualization.dashboard import create_dashboard
        
        dashboard = create_dashboard()
        dashboard.run(debug=False)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def generate_visualizations():
    """Generate static visualizations."""
    print("\n📊 Generating Visualizations...")
    print("-" * 60)
    
    try:
        from src.visualization.plots import StaticPlots
        from src.data.storage import ExperimentStorage
        import pandas as pd
        
        db_path = Path('data/experiments.db')
        if not db_path.exists():
            print("\n⚠️  No experiments found!")
            print("   Please run experiments first (Option 1)")
            return
        
        storage = ExperimentStorage(db_path)
        data = pd.DataFrame(storage.get_all_results())
        
        if len(data) == 0:
            print("\n⚠️  No experiment data found!")
            print("   Please run experiments first (Option 1)")
            return
        
        print(f"\n📊 Found {len(data)} experiments")
        print("   Generating plots...")
        
        output_dir = Path('results/figures')
        plotter = StaticPlots(output_dir, dpi=300)
        plots = plotter.generate_all_plots(data)
        
        print(f"\n✅ Generated {len(plots)} plots:")
        for name, path in plots.items():
            print(f"   • {name}: {path}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def run_tests():
    """Run test suite."""
    print("\n🧪 Running Tests...")
    print("-" * 60)
    print()
    
    import subprocess
    try:
        result = subprocess.run(
            ["pytest", "--cov=src", "--cov-report=term-missing", "-v"],
            check=False
        )
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print("\n⚠️  Some tests failed. See output above.")
            
    except FileNotFoundError:
        print("❌ pytest not found. Please run: pip install pytest pytest-cov")

def view_statistics():
    """View database statistics."""
    print("\n📊 Database Statistics")
    print("-" * 60)
    
    try:
        from src.data.storage import ExperimentStorage
        
        db_path = Path('data/experiments.db')
        if not db_path.exists():
            print("\n⚠️  No database found!")
            print("   Please run experiments first (Option 1)")
            return
        
        storage = ExperimentStorage(db_path)
        stats = storage.get_statistics()
        
        print(f"\n📈 Experiment Summary:")
        print(f"   Total Sentences: {stats['total_sentences']}")
        print(f"   Total Experiments: {stats['total_experiments']}")
        print(f"   Successful: {stats['successful_experiments']}")
        print(f"   Success Rate: {stats['success_rate']:.1%}")
        print(f"\n🤖 Agents Tested: {', '.join(stats['agents']) if stats['agents'] else 'None'}")
        print(f"📉 Error Rates: {', '.join(f'{r*100:.0f}%' for r in stats['error_rates']) if stats['error_rates'] else 'None'}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def main():
    """Main menu loop."""
    while True:
        print_menu()
        choice = input("Select option (1-6): ").strip()
        
        if choice == "1":
            run_experiments()
        elif choice == "2":
            launch_dashboard()
        elif choice == "3":
            generate_visualizations()
        elif choice == "4":
            run_tests()
        elif choice == "5":
            view_statistics()
        elif choice == "6":
            print("\n👋 Goodbye!\n")
            sys.exit(0)
        else:
            print("\n❌ Invalid choice. Please select 1-6.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!\n")
        sys.exit(0)

