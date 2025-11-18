#!/usr/bin/env python3
"""
Command-Line Interface for Translation Chain Vector Distance Analysis

Usage:
    python cli.py <command> [options]
    
Commands:
    experiment    Run translation experiments
    dashboard     Launch interactive dashboard
    visualize     Generate static visualizations
    analyze       Run analysis notebook
    test          Run test suite
    stats         Show database statistics
    
Examples:
    python cli.py experiment --agent cursor --sentences 10
    python cli.py dashboard --port 8050
    python cli.py visualize --output results/figures
    python cli.py test --coverage
"""

import argparse
import sys
from pathlib import Path


def cmd_experiment(args):
    """Run experiments command."""
    print(f"🚀 Running experiments with {args.agent} agent...")
    print(f"   Sentences: {args.sentences}")
    print(f"   Error rates: {args.error_rates or 'default [0, 10, 25, 35, 50]'}")
    
    try:
        from src.data.experiment_runner import ExperimentRunner
        
        runner = ExperimentRunner(args.agent, args.config)
        
        error_rates = None
        if args.error_rates:
            error_rates = [float(r)/100 for r in args.error_rates.split(',')]
        
        results = runner.run_full_experiment_suite(
            num_sentences=args.sentences,
            error_rates=error_rates
        )
        
        print(f"\n✅ Experiments Complete!")
        print(f"   Total: {results['total_experiments']}")
        print(f"   Successful: {results['successful_experiments']}")
        print(f"   Failed: {results['failed_experiments']}")
        print(f"   Success Rate: {results['success_rate']:.1%}")
        
        if results['successful_experiments'] > 0:
            print(f"\n📊 Results saved to database")
            print(f"   Run 'python cli.py dashboard' to visualize")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def cmd_dashboard(args):
    """Launch dashboard command."""
    print(f"🌐 Launching dashboard on {args.host}:{args.port}")
    print(f"   Press Ctrl+C to stop")
    
    try:
        from src.visualization.dashboard import create_dashboard
        
        dashboard = create_dashboard(args.config)
        dashboard.run(debug=args.debug)
        
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def cmd_visualize(args):
    """Generate visualizations command."""
    print(f"📊 Generating visualizations...")
    
    try:
        from src.visualization.plots import StaticPlots
        from src.data.storage import ExperimentStorage
        from src.config import get_settings
        import pandas as pd
        
        settings = get_settings(args.config)
        db_path = settings.get_database_path()
        
        if not db_path.exists():
            print("❌ No experiments found. Run experiments first:")
            print("   python cli.py experiment --agent cursor")
            sys.exit(1)
        
        storage = ExperimentStorage(db_path)
        data = pd.DataFrame(storage.get_all_results())
        
        if len(data) == 0:
            print("❌ No experiment data. Run experiments first.")
            sys.exit(1)
        
        output_dir = Path(args.output) if args.output else Path('results/figures')
        plotter = StaticPlots(output_dir, dpi=args.dpi)
        
        print(f"   Found {len(data)} experiments")
        print(f"   Output: {output_dir}")
        
        plots = plotter.generate_all_plots(data)
        
        print(f"\n✅ Generated {len(plots)} plots:")
        for name, path in plots.items():
            print(f"   • {name}: {path}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def cmd_analyze(args):
    """Open analysis notebook."""
    print("📓 Opening analysis notebook...")
    
    import subprocess
    try:
        notebook_path = Path('notebooks/analysis.ipynb')
        if not notebook_path.exists():
            print(f"❌ Notebook not found: {notebook_path}")
            sys.exit(1)
        
        subprocess.run(['jupyter', 'lab', str(notebook_path)])
        
    except FileNotFoundError:
        print("❌ Jupyter not found. Install with: pip install jupyterlab")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def cmd_test(args):
    """Run tests command."""
    print("🧪 Running tests...")
    
    import subprocess
    
    cmd = ['pytest']
    
    if args.coverage:
        cmd.extend(['--cov=src', '--cov-report=html', '--cov-report=term-missing'])
    
    if args.verbose:
        cmd.append('-v')
    
    if args.file:
        cmd.append(args.file)
    
    try:
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
            if args.coverage:
                print("   Coverage report: htmlcov/index.html")
        else:
            sys.exit(1)
            
    except FileNotFoundError:
        print("❌ pytest not found. Install with: pip install pytest pytest-cov")
        sys.exit(1)


def cmd_stats(args):
    """Show statistics command."""
    print("📊 Database Statistics\n")
    
    try:
        from src.data.storage import ExperimentStorage
        from src.config import get_settings
        
        settings = get_settings(args.config)
        db_path = settings.get_database_path()
        
        if not db_path.exists():
            print("❌ No database found. Run experiments first.")
            sys.exit(1)
        
        storage = ExperimentStorage(db_path)
        stats = storage.get_statistics()
        
        print(f"Experiment Summary:")
        print(f"  Total Sentences: {stats['total_sentences']}")
        print(f"  Total Experiments: {stats['total_experiments']}")
        print(f"  Successful: {stats['successful_experiments']}")
        print(f"  Success Rate: {stats['success_rate']:.1%}")
        
        if stats['agents']:
            print(f"\nAgents Tested:")
            for agent in stats['agents']:
                print(f"  • {agent}")
        
        if stats['error_rates']:
            print(f"\nError Rates:")
            for rate in stats['error_rates']:
                print(f"  • {rate*100:.0f}%")
        
        if args.detailed:
            results = storage.get_all_results()
            print(f"\nDetailed Results:")
            print(f"  Database file: {db_path}")
            print(f"  Database size: {db_path.stat().st_size / 1024:.1f} KB")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Translation Chain Vector Distance Analysis CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run experiments with cursor agent
  python cli.py experiment --agent cursor --sentences 10
  
  # Launch dashboard
  python cli.py dashboard
  
  # Generate visualizations
  python cli.py visualize --dpi 300
  
  # Run tests with coverage
  python cli.py test --coverage
  
  # Show statistics
  python cli.py stats --detailed
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Experiment command
    exp_parser = subparsers.add_parser('experiment', help='Run translation experiments')
    exp_parser.add_argument('--agent', '-a', default='cursor',
                           choices=['cursor', 'gemini', 'claude', 'ollama'],
                           help='Agent type to use (default: cursor)')
    exp_parser.add_argument('--sentences', '-s', type=int, default=10,
                           help='Number of sentences to test (default: 10)')
    exp_parser.add_argument('--error-rates', '-e',
                           help='Comma-separated error rates, e.g., "0,10,25,50"')
    exp_parser.add_argument('--config', '-c',
                           help='Path to config file')
    
    # Dashboard command
    dash_parser = subparsers.add_parser('dashboard', help='Launch interactive dashboard')
    dash_parser.add_argument('--host', default='127.0.0.1',
                            help='Host to bind to (default: 127.0.0.1)')
    dash_parser.add_argument('--port', '-p', type=int, default=8050,
                            help='Port to bind to (default: 8050)')
    dash_parser.add_argument('--debug', action='store_true',
                            help='Enable debug mode')
    dash_parser.add_argument('--config', '-c',
                            help='Path to config file')
    
    # Visualize command
    viz_parser = subparsers.add_parser('visualize', help='Generate static visualizations')
    viz_parser.add_argument('--output', '-o',
                           help='Output directory (default: results/figures)')
    viz_parser.add_argument('--dpi', type=int, default=300,
                           help='Image resolution (default: 300)')
    viz_parser.add_argument('--config', '-c',
                           help='Path to config file')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Open analysis notebook')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run test suite')
    test_parser.add_argument('--coverage', action='store_true',
                            help='Generate coverage report')
    test_parser.add_argument('--verbose', '-v', action='store_true',
                            help='Verbose output')
    test_parser.add_argument('--file', '-f',
                            help='Specific test file to run')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    stats_parser.add_argument('--detailed', '-d', action='store_true',
                             help='Show detailed statistics')
    stats_parser.add_argument('--config', '-c',
                             help='Path to config file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route to command handler
    commands = {
        'experiment': cmd_experiment,
        'dashboard': cmd_dashboard,
        'visualize': cmd_visualize,
        'analyze': cmd_analyze,
        'test': cmd_test,
        'stats': cmd_stats
    }
    
    commands[args.command](args)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted")
        sys.exit(130)

