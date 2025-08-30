#!/usr/bin/env python3
"""
Local 825 Intelligence MCP Server - Flask Web Application
"""

import os
import sys
import subprocess
import threading
import time
import logging
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure Python path is correct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# Global variable to track MCP server process
mcp_process = None
mcp_startup_error = None

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
        'mcp_server': 'running' if mcp_process else 'stopped',
        'mcp_error': mcp_startup_error
    })

@app.route('/start-mcp')
def start_mcp():
    """Start the MCP server"""
    global mcp_process, mcp_startup_error
    
    if mcp_process is None:
        try:
            # Start MCP server in background
            mcp_process = subprocess.Popen([sys.executable, 'mcp_server.py'])
            mcp_startup_error = None
            return jsonify({'status': 'MCP server started'})
        except Exception as e:
            mcp_startup_error = str(e)
            logger.error(f"Failed to start MCP server: {e}")
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'status': 'MCP server already running'})

def start_mcp_server():
    """Start MCP server in background thread"""
    global mcp_process, mcp_startup_error
    try:
        logger.info("Attempting to start MCP server...")
        mcp_process = subprocess.Popen([sys.executable, 'mcp_server.py'])
        logger.info("MCP server started successfully")
        mcp_startup_error = None
    except Exception as e:
        mcp_startup_error = str(e)
        logger.error(f"Failed to start MCP server: {e}")

if __name__ == '__main__':
    logger.info(f"Starting Local 825 Intelligence MCP Server with Python {sys.version}")
    
    # Start MCP server in background (but don't let it block Flask startup)
    try:
        mcp_thread = threading.Thread(target=start_mcp_server, daemon=True)
        mcp_thread.start()
        logger.info("MCP server startup thread initiated")
    except Exception as e:
        logger.error(f"Failed to start MCP server thread: {e}")
        mcp_startup_error = str(e)
    
    # Start Flask app
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Flask app starting on port {port}")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"Failed to start Flask app: {e}")
        sys.exit(1)
