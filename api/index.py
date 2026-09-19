"""
Vercel Serverless Function Entry Point for BloodChain AI.
Exports the WSGI Flask application object 'app' so Vercel can run it serverlessly.
"""

import sys
import os

# Add root project directory to sys.path so app, database, and ml_engine can be imported
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app
