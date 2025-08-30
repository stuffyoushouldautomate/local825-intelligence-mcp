#!/usr/bin/env python3
"""
Simple Notion connection test
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_notion_connection():
    """Test Notion API connection"""
    print("🔍 Testing Notion API connection...")
    
    try:
        from notion_client import Client as NotionClient
        
        api_key = os.getenv("NOTION_API_KEY")
        database_id = os.getenv("NOTION_DATABASE_ID")
        
        print(f"API Key: {api_key[:10]}...")
        print(f"Database ID: {database_id}")
        
        client = NotionClient(auth=api_key)
        
        # Test by trying to retrieve the database
        database = client.databases.retrieve(database_id)
        
        print(f"✅ Notion API: Connected successfully!")
        print(f"   Database: {database.get('title', [{}])[0].get('plain_text', 'Untitled')}")
        
        # Test creating a simple page
        print("\n🧪 Testing page creation...")
        test_page = client.pages.create(
            parent={"database_id": database_id},
            properties={
                "Title": {"title": [{"text": {"content": "Test Entry - AI Automation"}}]},
                "Content": {"rich_text": [{"text": {"content": "This is a test entry to verify the automation is working."}}]},
                "Image URL": {"url": "https://via.placeholder.com/1024x1024/007bff/ffffff?text=Test"},
                "Status": {"select": {"name": "Draft"}}
            }
        )
        
        print("✅ Test page created successfully!")
        print(f"   Page ID: {test_page['id']}")
        
        # Clean up - delete the test page
        print("\n🧹 Cleaning up test page...")
        client.pages.update(test_page['id'], archived=True)
        print("✅ Test page archived successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Notion API: Connection failed - {e}")
        return False

if __name__ == "__main__":
    test_notion_connection()

