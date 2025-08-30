#!/usr/bin/env python3
"""
Local 825 Intelligence MCP Server - Flask Web Application
"""

import os
import sys
import subprocess
import threading
import time
from flask import Flask, jsonify

# Ensure Python path is correct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# Global variable to track MCP server process
mcp_process = None

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'Local 825 Intelligence MCP Server',
        'version': '1.0.0',
        'python_version': sys.version,
        'endpoints': {
            'health': '/health',
            'intelligence': '/intelligence',
            'companies': '/companies'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'python_version': sys.version,
        'mcp_server': 'running' if mcp_process else 'stopped'
    })

@app.route('/start-mcp')
def start_mcp():
    """Start the MCP server"""
    global mcp_process
    
    if mcp_process is None:
        try:
            # Start MCP server in background
            mcp_process = subprocess.Popen([sys.executable, 'mcp_server.py'])
            return jsonify({'status': 'MCP server started'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'status': 'MCP server already running'})

def start_mcp_server():
    """Start MCP server in background thread"""
    global mcp_process
    try:
        mcp_process = subprocess.Popen([sys.executable, 'mcp_server.py'])
        print("MCP server started successfully")
    except Exception as e:
        print(f"Failed to start MCP server: {e}")

if __name__ == '__main__':
    print(f"Starting Local 825 Intelligence MCP Server with Python {sys.version}")
    
    # Start MCP server in background
    mcp_thread = threading.Thread(target=start_mcp_server, daemon=True)
    mcp_thread.start()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 8000))
    print(f"Flask app starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
