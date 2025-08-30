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
            'data': '/data',
            'intelligence': '/intelligence',
            'companies': '/companies',
            'start-mcp': '/start-mcp'
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

@app.route('/data')
def get_data():
    """Get intelligence data endpoint"""
    try:
        # For now, return sample data structure
        # In production, this would query your database
        sample_data = {
            'articles': [
                {
                    'title': 'Sample Local 825 Intelligence Article',
                    'source': 'Local 825 Intelligence System',
                    'published': '2025-08-30',
                    'summary': 'This is a sample article showing the data structure expected by the WordPress plugin.',
                    'jurisdiction': 'Local 825 Specific',
                    'relevance_score': 95,
                    'category': 'Intelligence',
                    'url': 'https://local825.org'
                }
            ],
            'metadata': {
                'total_articles': 1,
                'last_updated': '2025-08-30T10:00:00Z'
            }
        }
        return jsonify(sample_data)
    except Exception as e:
        logger.error(f"Error in /data endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/intelligence')
def get_intelligence():
    """Get intelligence data (alias for /data)"""
    return get_data()

@app.route('/companies')
def get_companies():
    """Get company data endpoint"""
    try:
        # For now, return sample company data
        # In production, this would query your database
        sample_companies = {
            'skanska': {
                'name': 'Skanska USA',
                'industry': 'Construction',
                'status': 'active',
                'last_updated': '2025-08-30',
                'notes': 'Major construction company in Local 825 jurisdiction'
            },
            'turner': {
                'name': 'Turner Construction',
                'industry': 'Construction',
                'status': 'active',
                'last_updated': '2025-08-30',
                'notes': 'Leading construction management company'
            }
        }
        return jsonify(sample_companies)
    except Exception as e:
        logger.error(f"Error in /companies endpoint: {e}")
        return jsonify({'error': str(e)}), 500

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
