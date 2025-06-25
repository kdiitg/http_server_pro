# --- File: dep_check.py ---

import os
import sys
import subprocess

def check_and_install_dependencies():
    marker_path = os.path.expanduser("~/.http_server_deps_ok")

    if os.path.exists(marker_path):
        return  # Already installed

    required = ["Pillow", "qrcode", "requests"]
    missing = []

    for pkg in required:
        try:
            __import__(pkg.lower() if pkg != "Pillow" else "PIL")
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"Installing missing packages: {missing}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
            with open(marker_path, "w") as f:
                f.write("Dependencies installed.\n")
            print("✅ All dependencies installed successfully.")
        except Exception as e:
            print("❌ Error installing dependencies:", e)
            input("Press Enter to exit...")
            sys.exit(1)
