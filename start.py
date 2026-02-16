#!/usr/bin/env python3
"""
Fill Application - Direct Startup Script

Starts the Fill application without Docker container.
Useful for development or when Docker is not available.

Usage:
    python start.py              # Start with auto-reload (development)
    python start.py --production # Start without reload (production)
    python start.py --host 0.0.0.0 --port 8080  # Custom host/port
"""

import argparse
import os
import sys
from pathlib import Path


def setup_environment():
    """Setup environment for local execution."""
    # Ensure data directory exists
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Set default database URL if not set
    if not os.getenv("DATABASE_URL"):
        db_path = data_dir / "fill.db"
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
        print(f"Using database: {db_path}")
    
    # Add src to Python path
    src_dir = Path(__file__).parent / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    # Set environment variables
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    os.environ.setdefault("WATCH_MODE", "true")
    os.environ.setdefault("DEBUG", "true")


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import sqlalchemy
        import uvicorn
        print("Dependencies check: OK")
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Start Fill Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Development mode with auto-reload
  %(prog)s --production       # Production mode
  %(prog)s --port 8080        # Use port 8080
  %(prog)s --host 0.0.0.0     # Allow external connections
        """
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Production mode (no auto-reload)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Import after environment setup
    import uvicorn
    
    # Configure reload
    reload_mode = not args.production
    
    print(f"\n{'='*60}")
    print("Fill Application Starting...")
    print(f"{'='*60}")
    print(f"Host:    {args.host}")
    print(f"Port:    {args.port}")
    print(f"Mode:    {'Production' if args.production else 'Development'}")
    print(f"Reload:  {'Enabled' if reload_mode else 'Disabled'}")
    print(f"{'='*60}\n")
    
    # Start server
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=reload_mode,
        workers=args.workers if args.production else 1,
        app_dir=str(Path(__file__).parent / "src"),
    )


if __name__ == "__main__":
    main()
