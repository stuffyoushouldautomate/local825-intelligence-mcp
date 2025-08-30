#!/usr/bin/env python3
"""
Test Notion Access for MyTribal AI
Tests the connection and database access
"""

import os
from notion_client import Client as NotionClient
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def test_notion_connection():
    """Test basic Notion connection"""
    print("🔍 Testing Notion Connection...")
    
    # Check environment variables
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")
    
    if not notion_api_key:
        print("❌ NOTION_API_KEY not found in environment variables")
        return None, None
    
    if not notion_database_id:
        print("❌ NOTION_DATABASE_ID not found in environment variables")
        return None, None
    
    print(f"✅ Environment variables found:")
    print(f"   API Key: {notion_api_key[:10]}...")
    print(f"   Database ID: {notion_database_id}")
    
    try:
        # Initialize Notion client
        notion_client = NotionClient(auth=notion_api_key)
        print("✅ Notion client initialized successfully")
        
        # Test connection by getting user info
        user_info = notion_client.users.me()
        print(f"✅ Connected to Notion as: {user_info.get('name', 'Unknown')}")
        
        return notion_client, notion_database_id
        
    except Exception as e:
        print(f"❌ Error connecting to Notion: {e}")
        return None, None

def test_database_access(notion_client, database_id):
    """Test access to specific database"""
    print(f"\n📊 Testing Database Access...")
    
    # Format database ID (add hyphens if missing)
    formatted_db_id = database_id
    if len(database_id) == 32 and '-' not in database_id:
        formatted_db_id = f"{database_id[:8]}-{database_id[8:12]}-{database_id[12:16]}-{database_id[16:20]}-{database_id[20:32]}"
    
    print(f"📝 Formatted Database ID: {formatted_db_id}")
    
    try:
        # Try to query the database
        response = notion_client.databases.query(database_id=formatted_db_id)
        print("✅ Database access successful!")
        print(f"   Found {len(response.get('results', []))} entries")
        return True
        
    except Exception as e:
        print(f"❌ Database access failed: {e}")
        return False

def list_available_databases(notion_client):
    """List all databases accessible to the integration"""
    print(f"\n🔍 Listing Available Databases...")
    
    try:
        # Search for databases
        response = notion_client.search(
            query="",
            filter={"property": "object", "value": "database"}
        )
        
        databases = response.get('results', [])
        if databases:
            print(f"✅ Found {len(databases)} accessible databases:")
            for i, db in enumerate(databases[:5], 1):  # Show first 5
                db_id = db.get('id', 'Unknown')
                title = "Untitled"
                if db.get('title') and db['title']:
                    title = db['title'][0].get('plain_text', 'Untitled')
                print(f"   {i}. {title} (ID: {db_id})")
            
            if len(databases) > 5:
                print(f"   ... and {len(databases) - 5} more")
        else:
            print("❌ No databases found accessible to this integration")
            
    except Exception as e:
        print(f"❌ Error listing databases: {e}")

def list_available_pages(notion_client):
    """List all pages accessible to the integration"""
    print(f"\n📄 Listing Available Pages...")
    
    try:
        # Search for pages
        response = notion_client.search(
            query="",
            filter={"property": "object", "value": "page"}
        )
        
        pages = response.get('results', [])
        if pages:
            print(f"✅ Found {len(pages)} accessible pages:")
            for i, page in enumerate(pages[:5], 1):  # Show first 5
                page_id = page.get('id', 'Unknown')
                title = "Untitled"
                if page.get('properties') and 'title' in page['properties']:
                    title_prop = page['properties']['title']
                    if title_prop.get('title') and title_prop['title']:
                        title = title_prop['title'][0].get('plain_text', 'Untitled')
                print(f"   {i}. {title} (ID: {page_id})")
            
            if len(pages) > 5:
                print(f"   ... and {len(pages) - 5} more")
        else:
            print("❌ No pages found accessible to this integration")
            
    except Exception as e:
        print(f"❌ Error listing pages: {e}")

def main():
    """Main test function"""
    print("🧪 Testing Notion Access for MyTribal AI")
    print("=" * 50)
    
    # Test connection
    notion_client, database_id = test_notion_connection()
    if not notion_client:
        return
    
    # Test database access
    database_accessible = test_database_access(notion_client, database_id)
    
    # List available resources
    list_available_databases(notion_client)
    list_available_pages(notion_client)
    
    if not database_accessible:
        print(f"\n🔧 Troubleshooting steps:")
        print("1. Make sure the database ID is correct")
        print("2. Ensure the database is shared with your integration")
        print("3. Check that your integration has the right permissions")
        print("4. Verify the integration is added to the database")
        
        print(f"\n📋 NOTION INTEGRATION SETUP:")
        print("=" * 50)
        print("1. Go to https://www.notion.so/my-integrations")
        print("2. Create a new integration")
        print("3. Give it a name (e.g., 'MyTribal AI')")
        print("4. Select the workspace where your database is")
        print("5. Copy the 'Internal Integration Token'")
        print("6. Go to your database page")
        print("7. Click 'Share' in the top right")
        print("8. Click 'Invite' and search for your integration name")
        print("9. Select it and give it 'Can edit' permissions")
        print("10. The integration should now appear in the database")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    from datetime import datetime
    main()
