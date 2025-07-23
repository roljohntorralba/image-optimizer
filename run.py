#!/usr/bin/env python3
"""
Simple launcher for the Image Optimizer application
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Launch the image optimizer application"""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Path to the main application
    app_path = script_dir / "image_optimizer.py"
    
    # Path to the virtual environment Python
    venv_python = script_dir / ".venv" / "bin" / "python"
    
    try:
        if venv_python.exists():
            # Use virtual environment Python
            subprocess.run([str(venv_python), str(app_path)])
        else:
            # Fall back to system Python
            subprocess.run([sys.executable, str(app_path)])
    except KeyboardInterrupt:
        print("\nApplication closed by user")
    except Exception as e:
        print(f"Error launching application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
