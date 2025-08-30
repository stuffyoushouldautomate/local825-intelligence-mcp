#!/usr/bin/env python3
"""
Simple test app without external dependencies
"""

import os
import sys
import time
import json

def create_response(data):
    """Create HTTP response"""
    response = json.dumps(data)
    return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(response)}\r\n\r\n{response}"

def handle_request(path):
    """Handle HTTP requests"""
    if path == '/':
        return create_response({
            'status': 'running',
            'service': 'Local 825 Intelligence Test Server',
            'version': '1.0.0',
            'python_version': sys.version,
            'message': 'Basic Python server is working!'
        })
    elif path == '/health':
        return create_response({
            'status': 'healthy',
            'timestamp': time.time(),
            'python_version': sys.version,
            'message': 'Health check passed'
        })
    else:
        return create_response({
            'error': 'Not found',
            'path': path
        })

def main():
    """Main server function"""
    print(f"Starting Local 825 Intelligence Test Server with Python {sys.version}")
    
    # Simple HTTP server
    import socket
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    port = int(os.environ.get('PORT', 8000))
    server.bind(('0.0.0.0', port))
    server.listen(5)
    
    print(f"Server listening on port {port}")
    
    try:
        while True:
            client, addr = server.accept()
            request = client.recv(1024).decode()
            
            if request:
                lines = request.split('\n')
                if lines:
                    path = lines[0].split(' ')[1]
                    response = handle_request(path)
                    client.send(response.encode())
            
            client.close()
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        server.close()

if __name__ == '__main__':
    main()
