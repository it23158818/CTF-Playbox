"""
CyberVault Stage 6 Capstone Host Service
Local & WSGI Application Entrypoint
Author: Member 3 - IT24103027 (Hettige D.R.B)
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from capstone_server import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5006))
    print(f"[*] Starting CyberVault Stage 6 Capstone Service on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
