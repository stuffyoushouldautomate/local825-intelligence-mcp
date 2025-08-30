#!/usr/bin/env python3
"""
DataPilotPlus MCP Server
Provides Model Context Protocol endpoints for external integrations
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading
from typing import Dict, Any, Optional
import mysql.connector  # type: ignore
from mysql.connector import Error  # type: ignore
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Configure logging with colorful console output
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and emojis"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨',
        'STARTUP': '🚀',
        'DATABASE': '🗄️',
        'SCRAPING': '🕷️',
        'PROCESSING': '⚙️',
        'SUCCESS': '🎉',
        'WAITING': '⏳',
        'CONNECTING': '🔌',
        'ANALYZING': '🧠',
        'SAVING': '💾',
        'REPORTING': '📊',
        'SERVER': '🌐',
        'REQUEST': '📡',
        'RESPONSE': '📤'
    }
    
    def format(self, record):
        # Add emoji based on log level or custom attributes
        if hasattr(record, 'emoji'):
            emoji = record.emoji
        elif record.levelname in self.EMOJIS:
            emoji = self.EMOJIS[record.levelname]
        else:
            emoji = '📝'
        
        # Color the log level
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        colored_level = f"{level_color}{record.levelname}{self.COLORS['RESET']}"
        
        # Format the message
        formatted = super().format(record)
        return f"{emoji} {formatted}"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Apply colored formatter to console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(console_handler)

def print_banner():
    """Print startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🌐 DataPilotPlus MCP Server 🌐                           ║
║                                                                              ║
║  📡 Model Context Protocol Endpoints                                        ║
║  🔌 External Tool Integration                                               ║
║  📊 Real-time Data Access                                                   ║
║  🚀 High-Performance API Server                                            ║
║                                                                              ║
║  Built with ❤️ by Jeremy Harris | augments.art                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def print_status(message: str, status_type: str = "info"):
    """Print formatted status message"""
    status_icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "processing": "⚙️",
        "waiting": "⏳",
        "connecting": "🔌",
        "analyzing": "🧠",
        "saving": "💾",
        "scraping": "🕷️",
        "server": "🌐",
        "request": "📡",
        "response": "📤"
    }
    
    icon = status_icons.get(status_type, "📝")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] {message}")

class DataPilotPlusMCPHandler(BaseHTTPRequestHandler):
    """MCP Server handler for DataPilotPlus scraper"""
    
    def __init__(self, *args, **kwargs):
        self.db_connection = None
        super().__init__(*args, **kwargs)
    
    def init_db_connection(self):
        """Initialize database connection"""
        if not self.db_connection or not self.db_connection.is_connected():
            try:
                print_status("🔌 Connecting to MySQL database...", "connecting")
                self.db_connection = mysql.connector.connect(
                    host=os.getenv('MYSQL_HOST', 'localhost'),
                    port=int(os.getenv('MYSQL_PORT', 3306)),
                    database=os.getenv('MYSQL_DATABASE', 'datapilotplus_scraper'),
                    user=os.getenv('MYSQL_USERNAME'),
                    password=os.getenv('MYSQL_PASSWORD'),
                    charset=os.getenv('MYSQL_CHARSET', 'utf8mb4')
                )
                print_status("✅ MCP Server: Database connection established", "success")
            except Error as e:
                print_status(f"❌ MCP Server: Database connection failed: {e}", "error")
                self.db_connection = None
    
    def send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        print_status(f"📡 GET request: {path}", "request")
        
        try:
            if path == '/health':
                self.handle_health_check()
            elif path == '/status':
                self.handle_status()
            elif path == '/stats':
                self.handle_stats()
            elif path == '/sources':
                self.handle_sources()
            elif path == '/reports':
                self.handle_reports()
            elif path == '/data':
                self.handle_data_query(parsed_path.query)
            else:
                self.send_json_response({'error': 'Endpoint not found'}, 404)
                
        except Exception as e:
            print_status(f"❌ MCP Server GET error: {e}", "error")
            self.send_json_response({'error': str(e)}, 500)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        print_status(f"📡 POST request: {path}", "request")
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}
            
            if path == '/scrape':
                self.handle_scrape_request(data)
            elif path == '/query':
                self.handle_custom_query(data)
            elif path == '/config':
                self.handle_config_update(data)
            else:
                self.send_json_response({'error': 'Endpoint not found'}, 404)
                
        except json.JSONDecodeError:
            print_status("❌ Invalid JSON in POST request", "error")
            self.send_json_response({'error': 'Invalid JSON'}, 400)
        except Exception as e:
            print_status(f"❌ MCP Server POST error: {e}", "error")
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_health_check(self):
        """Health check endpoint"""
        print_status("🏥 Health check requested", "info")
        self.send_json_response({
            'status': 'healthy',
            'service': 'DataPilotPlus MCP Server',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
        print_status("✅ Health check completed", "success")
    
    def handle_status(self):
        """Status endpoint"""
        print_status("📊 Status check requested", "info")
        self.send_json_response({
            'service': 'DataPilotPlus MCP Server',
            'status': 'running',
            'uptime': 'active',
            'database': 'connected' if self.db_connection and self.db_connection.is_connected() else 'disconnected',
            'timestamp': datetime.now().isoformat()
        })
        print_status("✅ Status check completed", "success")
    
    def handle_stats(self):
        """Statistics endpoint"""
        print_status("📈 Statistics requested", "info")
        self.init_db_connection()
        
        if not self.db_connection:
            print_status("❌ Database not available for stats", "error")
            self.send_json_response({'error': 'Database not available'}, 503)
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Get total records
            cursor.execute("SELECT COUNT(*) FROM scraped_data")
            total_records = cursor.fetchone()[0]
            
            # Get records by category
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM scraped_data
                GROUP BY category
                ORDER BY count DESC
            """)
            category_stats = dict(cursor.fetchall())
            
            # Get recent activity
            cursor.execute("""
                SELECT COUNT(*) FROM scraped_data
                WHERE scraped_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            """)
            last_24h = cursor.fetchone()[0]
            
            cursor.close()
            
            self.send_json_response({
                'total_records': total_records,
                'last_24h_records': last_24h,
                'category_breakdown': category_stats,
                'timestamp': datetime.now().isoformat()
            })
            
            print_status(f"✅ Statistics retrieved: {total_records} total records", "success")
            
        except Error as e:
            print_status(f"❌ Database error in stats: {e}", "error")
            self.send_json_response({'error': 'Database error'}, 500)
    
    def handle_sources(self):
        """Data sources endpoint"""
        print_status("📚 Data sources requested", "info")
        sources = {
            'company_information': ['SEC EDGAR', 'OpenCorporates', 'Company Websites'],
            'leadership': ['SEC Insiders', 'LinkedIn'],
            'operations': ['USAspending.gov', 'State DOT Databases'],
            'compliance': ['OSHA API', 'DOL Enforcement', 'NLRB API', 'EPA ECHO'],
            'financial': ['Yahoo Finance', 'Federal Contracts'],
            'political': ['FEC API', 'OpenSecrets API'],
            'corporate_structure': ['Business Registrations', 'Ownership Data']
        }
        
        self.send_json_response({
            'data_sources': sources,
            'total_categories': len(sources),
            'timestamp': datetime.now().isoformat()
        })
        print_status("✅ Data sources retrieved", "success")
    
    def handle_reports(self):
        """Reports endpoint"""
        print_status("📋 Reports requested", "info")
        self.init_db_connection()
        
        if not self.db_connection:
            print_status("❌ Database not available for reports", "error")
            self.send_json_response({'error': 'Database not available'}, 503)
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Get recent reports
            cursor.execute("""
                SELECT report_type, report_date, generated_at
                FROM reports
                ORDER BY generated_at DESC
                LIMIT 10
            """)
            reports = []
            for row in cursor.fetchall():
                reports.append({
                    'type': row[0],
                    'date': row[1].isoformat() if row[1] else None,
                    'generated_at': row[2].isoformat() if row[2] else None
                })
            
            cursor.close()
            
            self.send_json_response({
                'reports': reports,
                'total_reports': len(reports),
                'timestamp': datetime.now().isoformat()
            })
            
            print_status(f"✅ Reports retrieved: {len(reports)} reports", "success")
            
        except Error as e:
            print_status(f"❌ Database error in reports: {e}", "error")
            self.send_json_response({'error': 'Database error'}, 500)
    
    def handle_data_query(self, query_string):
        """Data query endpoint"""
        print_status("🔍 Data query requested", "info")
        self.init_db_connection()
        
        if not self.db_connection:
            print_status("❌ Database not available for data query", "error")
            self.send_json_response({'error': 'Database not available'}, 503)
            return
        
        try:
            # Parse query parameters
            params = urllib.parse.parse_qs(query_string)
            category = params.get('category', [None])[0]
            source = params.get('source', [None])[0]
            limit = min(int(params.get('limit', [10])[0]), 100)  # Max 100 records
            
            cursor = self.db_connection.cursor()
            
            # Build query
            query = "SELECT source_name, category, method_type, url, scraped_at FROM scraped_data"
            conditions = []
            query_params = []
            
            if category:
                conditions.append("category = %s")
                query_params.append(category)
            
            if source:
                conditions.append("source_name = %s")
                query_params.append(source)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY scraped_at DESC LIMIT %s"
            query_params.append(limit)
            
            cursor.execute(query, query_params)
            results = []
            
            for row in cursor.fetchall():
                results.append({
                    'source_name': row[0],
                    'category': row[1],
                    'method_type': row[2],
                    'url': row[3],
                    'scraped_at': row[4].isoformat() if row[4] else None
                })
            
            cursor.close()
            
            self.send_json_response({
                'query': {
                    'category': category,
                    'source': source,
                    'limit': limit
                },
                'results': results,
                'total_results': len(results),
                'timestamp': datetime.now().isoformat()
            })
            
            print_status(f"✅ Data query completed: {len(results)} results", "success")
            
        except Error as e:
            print_status(f"❌ Database error in data query: {e}", "error")
            self.send_json_response({'error': 'Database error'}, 500)
    
    def handle_scrape_request(self, data: Dict[str, Any]):
        """Handle scraping requests"""
        source = data.get('source')
        category = data.get('category')
        
        print_status(f"🕷️ Scraping request: {source} in {category}", "scraping")
        
        if not source or not category:
            print_status("❌ Missing source or category in scraping request", "error")
            self.send_json_response({'error': 'Source and category required'}, 400)
            return
        
        # This would trigger the actual scraping
        # For now, return success response
        self.send_json_response({
            'status': 'scraping_initiated',
            'source': source,
            'category': category,
            'message': f'Scraping request received for {source} in {category}',
            'timestamp': datetime.now().isoformat()
        })
        
        print_status(f"✅ Scraping request processed for {source}", "success")
    
    def handle_custom_query(self, data: Dict[str, Any]):
        """Handle custom database queries"""
        query = data.get('query')
        
        print_status("🔍 Custom database query requested", "info")
        
        if not query:
            print_status("❌ No query provided in custom query request", "error")
            self.send_json_response({'error': 'Query required'}, 400)
            return
        
        self.init_db_connection()
        
        if not self.db_connection:
            print_status("❌ Database not available for custom query", "error")
            self.send_json_response({'error': 'Database not available'}, 503)
            return
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                columns = [desc[0] for desc in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        if hasattr(value, 'isoformat'):  # Handle datetime objects
                            value = value.isoformat()
                        row_dict[col] = value
                    results.append(row_dict)
                
                cursor.close()
                
                self.send_json_response({
                    'query': query,
                    'columns': columns,
                    'results': results,
                    'total_results': len(results),
                    'timestamp': datetime.now().isoformat()
                })
                
                print_status(f"✅ Custom SELECT query completed: {len(results)} results", "success")
            else:
                cursor.close()
                self.db_connection.commit()
                
                self.send_json_response({
                    'query': query,
                    'status': 'executed',
                    'message': 'Query executed successfully',
                    'timestamp': datetime.now().isoformat()
                })
                
                print_status("✅ Custom query executed successfully", "success")
                
        except Error as e:
            print_status(f"❌ Database error in custom query: {e}", "error")
            self.send_json_response({'error': f'Database error: {str(e)}'}, 500)
    
    def handle_config_update(self, data: Dict[str, Any]):
        """Handle configuration updates"""
        api_name = data.get('api_name')
        api_key = data.get('api_key')
        base_url = data.get('base_url')
        
        print_status(f"⚙️ Configuration update requested for {api_name}", "processing")
        
        if not api_name:
            print_status("❌ No API name provided in config update", "error")
            self.send_json_response({'error': 'API name required'}, 400)
            return
        
        self.init_db_connection()
        
        if not self.db_connection:
            print_status("❌ Database not available for config update", "error")
            self.send_json_response({'error': 'Database not available'}, 503)
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Update or insert API configuration
            upsert_query = """
            INSERT INTO api_configs (api_name, api_key, base_url, last_used)
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
                api_key = VALUES(api_key),
                base_url = VALUES(base_url),
                last_used = NOW()
            """
            
            cursor.execute(upsert_query, (api_name, api_key, base_url))
            self.db_connection.commit()
            cursor.close()
            
            self.send_json_response({
                'status': 'config_updated',
                'api_name': api_name,
                'message': 'API configuration updated successfully',
                'timestamp': datetime.now().isoformat()
            })
            
            print_status(f"✅ Configuration updated for {api_name}", "success")
            
        except Error as e:
            print_status(f"❌ Database error in config update: {e}", "error")
            self.send_json_response({'error': 'Database error'}, 500)
    
    def log_message(self, format, *args):
        """Custom logging for MCP server"""
        print_status(f"MCP Server: {format % args}", "server")

def start_mcp_server(host: str = 'localhost', port: int = 8000):
    """Start the MCP server"""
    try:
        server = HTTPServer((host, port), DataPilotPlusMCPHandler)
        print_status(f"🚀 DataPilotPlus MCP Server started on {host}:{port}", "startup")
        
        def run_server():
            server.serve_forever()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        return server, server_thread
    except Exception as e:
        print_status(f"❌ Failed to start MCP server: {e}", "error")
        return None, None

if __name__ == "__main__":
    print_banner()
    
    # Start MCP server
    host = os.getenv('MCP_SERVER_HOST', 'localhost')
    port = int(os.getenv('MCP_SERVER_PORT', 8000))
    
    print_status(f"🌐 Starting MCP Server on {host}:{port}...", "server")
    
    server, thread = start_mcp_server(host, port)
    
    if server:
        try:
            print_status("✅ MCP Server is running and ready for connections", "success")
            print_status("💡 Press Ctrl+C to stop the server", "info")
            
            # Keep the main thread alive
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print_status("🛑 Shutting down MCP server...", "warning")
            server.shutdown()
            print_status("👋 MCP Server stopped successfully", "success")
    else:
        print_status("❌ Failed to start MCP server", "error")
