import feedparser
from openai import OpenAI
from notion_client import Client as NotionClient
from wordpress_xmlrpc import Client as WPClient
from wordpress_xmlrpc.methods.posts import NewPost
import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
WP_URL = os.getenv("WP_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

# RSS feed URL
RSS_URL = "https://www.reddit.com/r/technology/hot.rss?limit=5"  # Limit to 5 for testing

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
notion_client = NotionClient(auth=NOTION_API_KEY)
wp_client = WPClient(WP_URL, WP_USERNAME, WP_APP_PASSWORD)

# Fetch and process RSS feed
feed = feedparser.parse(RSS_URL)
for entry in feed.entries:
    title = entry.title
    description = entry.get("contentSnippet", "general tech theme")  # Use get() for safety

    # Generate Article with ChatGPT
    article_response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Generate a 500-word blog article based on this Reddit post: Title: {title}. Description: {description}. Include SEO keywords like 'trending 2025', headings, and bullet points. Make it original."}]
    )
    article = article_response.choices[0].message.content

    # Generate Image with DALL-E
    image_response = openai_client.images.generate(
        model="dall-e-3",
        prompt=f"{title} - Create a high-quality, eye-catching image for this blog post. Include elements from: {description}. Style: vibrant digital illustration.",
        size="1024x1024",
        quality="standard",
        n=1
    )
    image_url = image_response.data[0].url

    # Store in Notion
    notion_client.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "Title": {"title": [{"text": {"content": title}}]},
            "Content": {"rich_text": [{"text": {"content": article}}]},
            "Image URL": {"url": image_url},
            "Status": {"select": {"name": "Draft"}}
        }
    )

    # Publish to WordPress
    post = {
        'title': title,
        'content': article + f'<img src="{image_url}" alt="{title}">',
        'status': 'publish'
    }
    wp_client.call(NewPost(post))

print("Workflow completed. Check Notion and WordPress!")
