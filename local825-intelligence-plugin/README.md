# Local 825 Intelligence Plugin

A comprehensive WordPress plugin for Local 825 Operating Engineers that provides real-time intelligence monitoring, company tracking, and strategic insights for the construction industry in New Jersey and New York territories.

## 🎯 Features

### **Intelligence Dashboard**
- Real-time intelligence data from your MCP server
- Article categorization by jurisdiction (NJ/NY/Local 825)
- Relevance scoring and filtering
- Strategic insights and analysis

### **Company Tracking**
- Monitor 30+ major construction companies
- Track union status, projects, and developments
- Automated updates and notifications
- Custom company management

### **WordPress Integration**
- Full WordPress admin interface
- Dashboard widget for quick access
- AJAX-powered real-time updates
- Export/import functionality

### **Automation**
- Scheduled intelligence updates
- Email notifications
- Company tracking updates
- Data retention management

## 🚀 Installation

### **Method 1: WordPress Admin (Recommended)**

1. Download the plugin ZIP file
2. Go to WordPress Admin → Plugins → Add New
3. Click "Upload Plugin" and select the ZIP file
4. Click "Install Now" and then "Activate Plugin"

### **Method 2: Manual Installation**

1. Extract the plugin files to `/wp-content/plugins/local825-intelligence-plugin/`
2. Go to WordPress Admin → Plugins
3. Find "Local 825 Intelligence System" and click "Activate"

## ⚙️ Configuration

### **Step 1: MCP Server Setup**

1. Go to **Local 825 Intel → Settings**
2. Enter your Railway-hosted MCP server URL:
   ```
   https://your-railway-app.railway.app
   ```
3. Enter your API key
4. Click "Test MCP Connection" to verify

### **Step 2: Company Tracking**

1. In Settings, go to "Company Tracking Management"
2. Click "Load Default Companies" to add the 30+ companies
3. Customize the list as needed
4. Click "Save Company List"

### **Step 3: Notifications**

1. Set your notification email address
2. Configure update frequency (15 min to 4 hours)
3. Enable/disable auto-updates

## 🏗️ MCP Server Integration

### **Required Endpoints**

Your Railway-hosted MCP server must provide these endpoints:

#### **GET /intelligence**
Returns intelligence data in this format:
```json
{
  "articles": [
    {
      "title": "Article Title",
      "url": "https://example.com/article",
      "source": "Source Name",
      "published": "2025-08-28T18:26:00Z",
      "summary": "Article summary...",
      "jurisdiction": "New Jersey",
      "relevance_score": 12,
      "category": "Construction Projects"
    }
  ],
  "metadata": {
    "total_articles": 3243,
    "last_updated": "2025-08-28T18:26:00Z"
  }
}
```

#### **GET /companies**
Returns company tracking data:
```json
{
  "companies": {
    "skanska": {
      "name": "Skanska USA",
      "status": "Signatory",
      "location": "NJ/NY Region",
      "last_update": "2025-08-28",
      "notes": "Major infrastructure projects..."
    }
  }
}
```

### **Authentication**

Use Bearer token authentication:
```
Authorization: Bearer YOUR_API_KEY
```

## 📊 Usage

### **Dashboard Widget**

The plugin adds a widget to your WordPress dashboard showing:
- Quick statistics (articles, companies)
- Top intelligence story
- Quick access to full dashboard

### **Main Dashboard**

Access via **Local 825 Intel → Dashboard**:
- Intelligence overview with statistics
- Top articles by relevance score
- Company tracking overview
- Quick actions and system status

### **Company Tracking**

Manage companies via **Local 825 Intel → Company Tracking**:
- View all tracked companies
- Update status and notes
- Track changes over time
- Export company data

### **Reports**

Generate reports via **Local 825 Intel → Reports**:
- Intelligence summaries
- Company tracking reports
- Export data in JSON format
- Historical analysis

## 🔧 Advanced Configuration

### **Custom Cron Schedules**

The plugin supports custom update frequencies:
- 15 minutes
- 30 minutes
- 1 hour (default)
- 2 hours
- 4 hours

### **Data Retention**

Configure how long to keep intelligence data:
- 7 days
- 14 days
- 30 days (default)
- 60 days
- 90 days

### **Debug Mode**

Enable detailed logging for troubleshooting:
- AJAX request logging
- MCP server communication logs
- Error tracking
- Performance metrics

## 📱 Responsive Design

The plugin is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile devices
- All screen sizes

## 🔒 Security Features

- WordPress nonce verification
- Capability checks
- Input sanitization
- AJAX security
- API key protection

## 🚨 Troubleshooting

### **MCP Server Connection Issues**

1. Verify your Railway app is running
2. Check the server URL is correct
3. Verify your API key is valid
4. Test connection in Settings

### **No Intelligence Data**

1. Check MCP server is running
2. Verify API endpoints are working
3. Check WordPress cron is enabled
4. Review error logs

### **Company Data Not Updating**

1. Verify company list is saved
2. Check MCP server `/companies` endpoint
3. Review update frequency settings
4. Check for JavaScript errors

## 📈 Performance Optimization

### **Recommended Settings**

- **Update Frequency**: Every hour (for production)
- **Data Retention**: 30 days
- **Debug Mode**: Disabled (for production)
- **Auto Updates**: Enabled

### **Server Requirements**

- PHP 7.4 or higher
- WordPress 5.0 or higher
- MySQL 5.6 or higher
- HTTPS recommended

## 🔄 Updates

### **Automatic Updates**

The plugin will automatically:
- Update intelligence data based on your schedule
- Refresh company tracking information
- Send email notifications when enabled
- Clean up old data based on retention settings

### **Manual Updates**

You can manually refresh data:
- Click "Refresh Intelligence" in the dashboard
- Use the refresh button in the dashboard widget
- Trigger updates via AJAX calls

## 📞 Support

### **Documentation**

- Plugin settings help text
- Inline documentation
- Code comments
- This README file

### **Logs**

Check WordPress debug logs for:
- MCP server communication
- AJAX request details
- Error messages
- Performance metrics

## 🎨 Customization

### **Styling**

The plugin includes CSS that can be customized:
- Color schemes
- Layout adjustments
- Responsive breakpoints
- WordPress admin integration

### **Functionality**

Extend the plugin with:
- Custom AJAX handlers
- Additional data sources
- Custom reporting
- Integration with other plugins

## 📋 Changelog

### **Version 1.0.0**
- Initial release
- Intelligence dashboard
- Company tracking
- MCP server integration
- WordPress admin interface
- Dashboard widget
- Automated updates
- Export/import functionality

## 🤝 Contributing

This plugin is designed specifically for Local 825 Operating Engineers. For modifications or enhancements:

1. Review the code structure
2. Test changes thoroughly
3. Follow WordPress coding standards
4. Document any modifications

## 📄 License

GPL v2 or later - Same as WordPress

## 🏗️ About Local 825

Local 825 represents Operating Engineers in New Jersey and relevant New York territories. This plugin provides intelligence gathering and analysis capabilities to support organizing efforts, contract negotiations, and strategic planning.

---

**Local 825 Intelligence Division**  
Contact: jeremy@augments.art  
© 2025 Local 825 Operating Engineers
