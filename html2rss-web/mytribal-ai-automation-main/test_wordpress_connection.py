#!/usr/bin/env python3
"""
Test WordPress Connection
Diagnose WordPress XML-RPC connection issues
"""

import os
import ssl
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# WordPress configuration
WP_URL = os.getenv("WP_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

def test_xmlrpc_availability():
    """Test if XML-RPC endpoint is available"""
    print("🔍 Testing XML-RPC Endpoint Availability...")
    
    if not WP_URL:
        print("❌ WP_URL not found in environment variables")
        return False
    
    wp_url = WP_URL.rstrip('/')
    xmlrpc_url = wp_url + '/xmlrpc.php'
    
    try:
        # Disable SSL verification
        ssl._create_default_https_context = ssl._create_unverified_context
        
        print(f"🌐 Testing: {xmlrpc_url}")
        
        # Test with a simple POST request
        response = requests.post(
            xmlrpc_url,
            headers={'Content-Type': 'text/xml'},
            data='<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName></methodCall>',
            verify=False,
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ XML-RPC endpoint is available and responding")
            return True
        elif response.status_code == 403:
            print("⚠️ XML-RPC endpoint found but access forbidden")
            print("   This might mean:")
            print("   - XML-RPC is disabled via security plugin")
            print("   - Application passwords not set up")
            print("   - Incorrect credentials")
            return False
        elif response.status_code == 404:
            print("❌ XML-RPC endpoint not found")
            print("   This might mean:")
            print("   - XML-RPC is disabled")
            print("   - WordPress is using custom permalink structure")
            return False
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing XML-RPC: {e}")
        return False

def test_wordpress_credentials():
    """Test WordPress credentials using XML-RPC"""
    print("\n🔐 Testing WordPress Credentials...")
    
    if not all([WP_URL, WP_USERNAME, WP_APP_PASSWORD]):
        missing = []
        if not WP_URL: missing.append("WP_URL")
        if not WP_USERNAME: missing.append("WP_USERNAME") 
        if not WP_APP_PASSWORD: missing.append("WP_APP_PASSWORD")
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return False
    
    try:
        from wordpress_xmlrpc import Client as WPClient
        from wordpress_xmlrpc.methods import posts
        
        # Disable SSL verification
        ssl._create_default_https_context = ssl._create_unverified_context
        
        wp_url = WP_URL.rstrip('/')
        if not wp_url.endswith('/xmlrpc.php'):
            wp_url += '/xmlrpc.php'
        
        print(f"🔗 Connecting to: {wp_url}")
        print(f"👤 Username: {WP_USERNAME}")
        print(f"🔑 App Password: {'*' * len(WP_APP_PASSWORD) if WP_APP_PASSWORD else 'Not set'}")
        
        wp_client = WPClient(wp_url, WP_USERNAME, WP_APP_PASSWORD)
        
        # Try to get posts (this will test authentication)
        recent_posts = wp_client.call(posts.GetPosts({'number': 1}))
        
        print("✅ WordPress connection successful!")
        print(f"📝 Found {len(recent_posts)} recent posts")
        
        if recent_posts:
            latest_post = recent_posts[0]
            print(f"   Latest post: '{latest_post.title}' (ID: {latest_post.id})")
        
        return True
        
    except Exception as e:
        print(f"❌ WordPress connection failed: {e}")
        
        # Provide troubleshooting guidance
        error_str = str(e).lower()
        if 'forbidden' in error_str or '403' in error_str:
            print("\n🔧 TROUBLESHOOTING - 403 Forbidden:")
            print("1. Enable XML-RPC in WordPress:")
            print("   - Go to WordPress Admin → Settings → Writing")
            print("   - Look for 'XML-RPC' settings")
            print("2. Create Application Password:")
            print("   - Go to WordPress Admin → Users → Your Profile")
            print("   - Scroll to 'Application Passwords'")
            print("   - Create new password for 'MyTribal AI Automation'")
            print("3. Check security plugins:")
            print("   - Temporarily disable security plugins that might block XML-RPC")
            print("   - Common plugins: Wordfence, iThemes Security, etc.")
            
        elif 'not found' in error_str or '404' in error_str:
            print("\n🔧 TROUBLESHOOTING - 404 Not Found:")
            print("1. Check if XML-RPC is enabled")
            print("2. Try different URL formats:")
            print(f"   - {WP_URL}/xmlrpc.php")
            print(f"   - {WP_URL}/wp/xmlrpc.php")
            print("3. Check WordPress installation path")
            
        return False

def show_setup_guide():
    """Show WordPress setup guide"""
    print("\n📋 WORDPRESS XML-RPC SETUP GUIDE:")
    print("=" * 50)
    print("1. Login to your WordPress admin dashboard")
    print("2. Go to Users → Your Profile")
    print("3. Scroll down to 'Application Passwords'")
    print("4. Enter a name like 'MyTribal AI Automation'")
    print("5. Click 'Add New Application Password'")
    print("6. Copy the generated password")
    print("7. Update your .env file with:")
    print(f"   WP_URL=https://mytribal.ai")
    print(f"   WP_USERNAME=your_wordpress_username")
    print(f"   WP_APP_PASSWORD=generated_app_password")
    print("\n⚠️ Note: Use the APPLICATION PASSWORD, not your regular WordPress password!")

def main():
    """Main test function"""
    print("🧪 Testing WordPress Connection for MyTribal AI")
    print("=" * 60)
    
    # Test XML-RPC availability
    xmlrpc_available = test_xmlrpc_availability()
    
    if xmlrpc_available:
        # Test credentials
        credentials_valid = test_wordpress_credentials()
        
        if not credentials_valid:
            show_setup_guide()
    else:
        print("\n🔧 XML-RPC endpoint issues detected.")
        print("Please check your WordPress configuration.")
        show_setup_guide()
    
    print(f"\n⏰ Test completed at: {__import__('datetime').datetime.now()}")

if __name__ == "__main__":
    main()
