# Local 825 Intelligence MCP Server

A high-performance Model Context Protocol (MCP) server that provides real-time intelligence data for Local 825 Operating Engineers. This server aggregates construction industry data, company tracking information, and strategic insights.

## 🚀 Features

- **Real-time Intelligence Data** - Live scraping and analysis of construction industry sources
- **Company Tracking** - Monitor 30+ major construction companies in NJ/NY
- **MCP Protocol** - Standardized API endpoints for external integrations
- **MySQL Database** - Robust data storage with Railway MySQL
- **Automated Updates** - Scheduled intelligence gathering and reporting

## 🏗️ Architecture

- **MCP Server** - HTTP server with RESTful endpoints
- **Database** - MySQL with optimized schema for intelligence data
- **Scraping Engine** - Multi-source data collection system
- **Analysis Engine** - AI-powered content analysis and categorization

## 📡 API Endpoints

### Health Check
- `GET /health` - Server health status

### Intelligence Data
- `GET /intelligence` - Get intelligence articles and insights
- `GET /companies` - Get company tracking data
- `GET /reports` - Get generated intelligence reports

### Configuration
- `POST /config` - Update API configurations
- `GET /status` - Get server and database status

## 🗄️ Database Schema

- **scraped_data** - Raw scraped content and metadata
- **reports** - Generated intelligence reports
- **api_configs** - API configurations and keys
- **scraping_jobs** - Scheduled scraping tasks
- **data_quality** - Data quality metrics
- **local825_intelligence** - Processed intelligence data
- **companies** - Company tracking information

## 🚀 Deployment

### Railway Deployment
This server is configured for Railway deployment with:
- Automatic environment variable management
- MySQL database integration
- Health check monitoring
- Auto-restart on failure

### Environment Variables
Required environment variables are automatically set in Railway:
- Database connection details
- MCP server configuration
- API keys and endpoints
- Scraping configuration

## 🔧 Local Development

1. **Clone the repository**
2. **Install dependencies**: `pip install -r railway-requirements.txt`
3. **Set environment variables** in `.env` file
4. **Run the server**: `python mcp_server.py`

## 📊 Monitoring

- **Health checks** at `/health` endpoint
- **Logging** with structured output
- **Database connection monitoring**
- **Performance metrics**

## 🤝 Integration

This MCP server integrates with:
- **WordPress Plugin** - Local 825 Intelligence Dashboard
- **External Tools** - Via MCP protocol
- **Data Sources** - Multiple construction industry APIs

## 📝 License

Built for Local 825 Operating Engineers | augments.art
