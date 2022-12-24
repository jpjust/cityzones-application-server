import sys, os

# Get current and venv directories
cwd = os.getcwd()
INTERP = os.path.expanduser(f"{cwd}/venv/bin/python3")

# Replace python3 process
if sys.executable != INTERP:
  os.execl(INTERP, INTERP, *sys.argv)

# Include venv bin into PATH
sys.path.insert(0, f"{cwd}/venv/bin")

# Import the application
import riskzonesapp as application
