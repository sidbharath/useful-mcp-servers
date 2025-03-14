import asyncio
import httpx
import sys
from urllib.parse import urljoin
from typing import Any, List, Dict, Optional
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("wordpress")

# Constants
DEFAULT_TIMEOUT = 30.0

class WordPressClient:
    """Client for WordPress REST API."""
    
    def __init__(self, base_url: str, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize WordPress API client.
        
        Args:
            base_url: Base URL of the WordPress site (e.g., https://example.com)
            username: WordPress username for authenticated requests
            password: WordPress password for authenticated requests
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/wp-json/wp/v2"
        self.username = username
        self.password = password
        self.auth = None
        
        if username and password:
            self.auth = (username, password)
    
    async def get_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None, base_path: Optional[str] = None) -> Any:
        """
        Make a GET request to the WordPress REST API.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters
            base_path: Override the base API path (default: self.api_url)
            
        Returns:
            JSON response
        """
        # Use the provided base_path or default to self.api_url
        base = base_path if base_path else self.api_url
        url = f"{base}/{endpoint.lstrip('/')}"
        
        # Print the URL for debugging
        print(f"Making request to: {url}", file=sys.stderr)
        
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.get(
                url,
                params=params,
                auth=self.auth,
                headers={"User-Agent": "WordPress-MCP-Server/1.0"}
            )
            response.raise_for_status()
            return response.json()
    
    async def post_request(self, endpoint: str, data: Dict[str, Any], base_path: Optional[str] = None) -> Any:
        """
        Make a POST request to the WordPress REST API.
        
        Args:
            endpoint: API endpoint to call
            data: Request body
            base_path: Override the base API path (default: self.api_url)
            
        Returns:
            JSON response
        """
        # Use the provided base_path or default to self.api_url
        base = base_path if base_path else self.api_url
        url = f"{base}/{endpoint.lstrip('/')}"
        
        # Print the URL for debugging
        print(f"Making POST request to: {url}", file=sys.stderr)
        
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.post(
                url,
                json=data,
                auth=self.auth,
                headers={"User-Agent": "WordPress-MCP-Server/1.0"}
            )
            response.raise_for_status()
            return response.json()

# Initialize WordPress client - will be configured during server startup
wp_client = None

# Tool implementation functions
@mcp.tool()
async def get_posts(
    limit: int = 10,
    page: int = 1, 
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    search: Optional[str] = None
) -> str:
    """Get WordPress posts with optional filtering.
    
    Args:
        limit: Maximum number of posts to return (default: 10)
        page: Page number for pagination (default: 1)
        category_id: Filter posts by category ID
        tag_id: Filter posts by tag ID
        search: Search term to filter posts
    
    Returns:
        Formatted post information
    """
    if wp_client is None:
        return "WordPress client not initialized. Please set the WORDPRESS_URL environment variable."
    
    params = {
        "per_page": limit,
        "page": page,
    }
    
    if category_id:
        params["categories"] = category_id
    
    if tag_id:
        params["tags"] = tag_id
    
    if search:
        params["search"] = search
    
    try:
        posts = await wp_client.get_request("posts", params)
        
        if not posts:
            return "No posts found matching the criteria."
        
        formatted_posts = []
        for post in posts:
            # Format each post
            formatted_post = f"""
Title: {post.get('title', {}).get('rendered', 'No title')}
Date: {post.get('date', 'Unknown date')}
ID: {post.get('id', 'No ID')}
Link: {post.get('link', 'No link')}
Status: {post.get('status', 'Unknown status')}
Excerpt: {post.get('excerpt', {}).get('rendered', 'No excerpt').strip()}
---
"""
            formatted_posts.append(formatted_post)
            
        return "\n".join(formatted_posts)
    
    except Exception as e:
        return f"Error retrieving posts: {str(e)}"

@mcp.tool()
async def get_post_by_id(post_id: int) -> str:
    """Get a single WordPress post by ID.
    
    Args:
        post_id: ID of the post to retrieve
    
    Returns:
        Detailed post information
    """
    if wp_client is None:
        return "WordPress client not initialized. Please set the WORDPRESS_URL environment variable."
    
    try:
        post = await wp_client.get_request(f"posts/{post_id}")
        
        # Format the response
        content = post.get('content', {}).get('rendered', 'No content')
        excerpt = post.get('excerpt', {}).get('rendered', 'No excerpt').strip()
        
        formatted_post = f"""
Title: {post.get('title', {}).get('rendered', 'No title')}
Date: {post.get('date', 'Unknown date')}
ID: {post.get('id', 'No ID')}
Link: {post.get('link', 'No link')}
Status: {post.get('status', 'Unknown status')}
Excerpt: {excerpt}

Content:
{content}
"""
        return formatted_post
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Post with ID {post_id} not found."
        return f"Error retrieving post: {str(e)}"
    
    except Exception as e:
        return f"Error retrieving post: {str(e)}"

@mcp.tool()
async def get_categories(limit: int = 20) -> str:
    """Get WordPress categories.
    
    Args:
        limit: Maximum number of categories to return (default: 20)
    
    Returns:
        Formatted category information
    """
    if wp_client is None:
        return "WordPress client not initialized. Please set the WORDPRESS_URL environment variable."
    
    try:
        categories = await wp_client.get_request("categories", {"per_page": limit})
        
        if not categories:
            return "No categories found."
        
        formatted_categories = []
        for category in categories:
            formatted_category = f"""
Name: {category.get('name', 'No name')}
ID: {category.get('id', 'No ID')}
Slug: {category.get('slug', 'No slug')}
Count: {category.get('count', 0)} posts
---
"""
            formatted_categories.append(formatted_category)
            
        return "\n".join(formatted_categories)
    
    except Exception as e:
        return f"Error retrieving categories: {str(e)}"

@mcp.tool()
async def get_tags(limit: int = 20) -> str:
    """Get WordPress tags.
    
    Args:
        limit: Maximum number of tags to return (default: 20)
    
    Returns:
        Formatted tag information
    """
    if wp_client is None:
        return "WordPress client not initialized. Please set the WORDPRESS_URL environment variable."
    
    try:
        tags = await wp_client.get_request("tags", {"per_page": limit})
        
        if not tags:
            return "No tags found."
        
        formatted_tags = []
        for tag in tags:
            formatted_tag = f"""
Name: {tag.get('name', 'No name')}
ID: {tag.get('id', 'No ID')}
Slug: {tag.get('slug', 'No slug')}
Count: {tag.get('count', 0)} posts
---
"""
            formatted_tags.append(formatted_tag)
            
        return "\n".join(formatted_tags)
    
    except Exception as e:
        return f"Error retrieving tags: {str(e)}"

@mcp.tool()
async def get_pages(limit: int = 10) -> str:
    """Get WordPress pages.
    
    Args:
        limit: Maximum number of pages to return (default: 10)
    
    Returns:
        Formatted page information
    """
    if wp_client is None:
        return "WordPress client not initialized. Please set the WORDPRESS_URL environment variable."
    
    try:
        pages = await wp_client.get_request("pages", {"per_page": limit})
        
        if not pages:
            return "No pages found."
        
        formatted_pages = []
        for page in pages:
            formatted_page = f"""
Title: {page.get('title', {}).get('rendered', 'No title')}
ID: {page.get('id', 'No ID')}
Link: {page.get('link', 'No link')}
Status: {page.get('status', 'Unknown status')}
---
"""
            formatted_pages.append(formatted_page)
            
        return "\n".join(formatted_pages)
    
    except Exception as e:
        return f"Error retrieving pages: {str(e)}"

@mcp.tool()
async def search_content(query: str, limit: int = 10) -> str:
    """Search WordPress content.
    
    Args:
        query: Search term
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        Search results
    """
    if wp_client is None:
        return "WordPress client not initialized. Please set the WORDPRESS_URL environment variable."
    
    try:
        # Search posts
        posts = await wp_client.get_request("posts", {"search": query, "per_page": limit})
        
        # Search pages
        pages = await wp_client.get_request("pages", {"search": query, "per_page": limit})
        
        if not posts and not pages:
            return f"No results found for '{query}'."
        
        results = []
        
        if posts:
            results.append(f"Posts matching '{query}':")
            for post in posts:
                results.append(f"- {post.get('title', {}).get('rendered', 'No title')} (ID: {post.get('id')})")
        
        if pages:
            if posts:  # Add a separator if we have both posts and pages
                results.append("")
            results.append(f"Pages matching '{query}':")
            for page in pages:
                results.append(f"- {page.get('title', {}).get('rendered', 'No title')} (ID: {page.get('id')})")
        
        return "\n".join(results)
    
    except Exception as e:
        return f"Error searching content: {str(e)}"

@mcp.tool()
async def get_media(limit: int = 10) -> str:
    """Get WordPress media items.
    
    Args:
        limit: Maximum number of media items to return (default: 10)
    
    Returns:
        Formatted media information
    """
    if wp_client is None:
        return "WordPress client not initialized. Please set the WORDPRESS_URL environment variable."
    
    try:
        media = await wp_client.get_request("media", {"per_page": limit})
        
        if not media:
            return "No media found."
        
        formatted_media = []
        for item in media:
            mime_type = item.get('mime_type', 'Unknown type')
            media_type = mime_type.split('/')[0] if '/' in mime_type else mime_type
            
            formatted_item = f"""
Title: {item.get('title', {}).get('rendered', 'No title')}
ID: {item.get('id', 'No ID')}
Type: {media_type}
URL: {item.get('source_url', 'No URL')}
Date: {item.get('date', 'Unknown date')}
---
"""
            formatted_media.append(formatted_item)
            
        return "\n".join(formatted_media)
    
    except Exception as e:
        return f"Error retrieving media: {str(e)}"

@mcp.tool()
async def get_users(limit: int = 10) -> str:
    """Get WordPress users.
    
    Args:
        limit: Maximum number of users to return (default: 10)
    
    Returns:
        Formatted user information
    """
    if wp_client is None:
        return "WordPress client not initialized. Please set the WORDPRESS_URL environment variable."
    
    try:
        users = await wp_client.get_request("users", {"per_page": limit})
        
        if not users:
            return "No users found."
        
        formatted_users = []
        for user in users:
            formatted_user = f"""
Name: {user.get('name', 'No name')}
ID: {user.get('id', 'No ID')}
Username: {user.get('slug', 'No username')}
URL: {user.get('link', 'No URL')}
---
"""
            formatted_users.append(formatted_user)
            
        return "\n".join(formatted_users)
    
    except Exception as e:
        return f"Error retrieving users: {str(e)}"

@mcp.tool()
async def get_comments(post_id: Optional[int] = None, limit: int = 10) -> str:
    """Get WordPress comments, optionally for a specific post.
    
    Args:
        post_id: Post ID to get comments for (or None for recent comments)
        limit: Maximum number of comments to return (default: 10)
    
    Returns:
        Formatted comment information
    """
    if wp_client is None:
        return "WordPress client not initialized. Please set the WORDPRESS_URL environment variable."
    
    try:
        params = {"per_page": limit}
        if post_id:
            params["post"] = post_id
        
        comments = await wp_client.get_request("comments", params)
        
        if not comments:
            return "No comments found."
        
        formatted_comments = []
        for comment in comments:
            formatted_comment = f"""
Author: {comment.get('author_name', 'Anonymous')}
Date: {comment.get('date', 'Unknown date')}
Post ID: {comment.get('post', 'Unknown post')}
Content: {comment.get('content', {}).get('rendered', 'No content').strip()}
---
"""
            formatted_comments.append(formatted_comment)
            
        return "\n".join(formatted_comments)
    
    except Exception as e:
        return f"Error retrieving comments: {str(e)}"

@mcp.tool()
async def create_post(title: str, content: str, status: str = "draft", categories: Optional[List[int]] = None, tags: Optional[List[int]] = None) -> str:
    """Create a new WordPress blog post.
    
    Args:
        title: Title of the post
        content: Content of the post (can include HTML)
        status: Post status (default: draft, options: draft, publish, private, pending)
        categories: List of category IDs to assign (optional)
        tags: List of tag IDs to assign (optional)
    
    Returns:
        Result of the post creation operation
    """
    if wp_client is None:
        return "WordPress client not initialized. Please set the WORDPRESS_URL environment variable."
    
    if not wp_client.username or not wp_client.password:
        return "Authentication credentials (WORDPRESS_USERNAME and WORDPRESS_PASSWORD) are required to create posts."
    
    try:
        # Prepare post data
        post_data = {
            "title": title,
            "content": content,
            "status": status
        }
        
        # Add categories and tags if provided
        if categories:
            post_data["categories"] = categories
            
        if tags:
            post_data["tags"] = tags
        
        # Create the post
        result = await wp_client.post_request("posts", post_data)
        
        # Format the response
        post_id = result.get("id")
        post_link = result.get("link")
        post_status = result.get("status")
        
        return f"""
Success! Post created:
ID: {post_id}
Title: {title}
Status: {post_status}
Link: {post_link}
"""
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return "Authentication failed. Please check your WordPress username and password."
        return f"Error creating post (HTTP {e.response.status_code}): {str(e)}"
    
    except Exception as e:
        return f"Error creating post: {str(e)}"

@mcp.resource("wordpress://site-info")
async def get_site_info() -> str:
    """Get basic information about the WordPress site."""
    if wp_client is None:
        return "WordPress client not initialized. Please set the WORDPRESS_URL environment variable."
    
    try:
        # WordPress REST API index provides basic site info
        base_url = wp_client.base_url
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.get(
                f"{base_url}/wp-json",
                auth=wp_client.auth,
                headers={"User-Agent": "WordPress-MCP-Server/1.0"}
            )
            response.raise_for_status()
            info = response.json()
        
        site_info = f"""
Site Name: {info.get('name', 'Unknown')}
Site Description: {info.get('description', 'No description')}
URL: {info.get('url', 'Unknown URL')}
Home URL: {info.get('home', 'Unknown home URL')}
API Base: {info.get('namespace', 'wp/v2')}
"""
        return site_info
    
    except Exception as e:
        return f"Error retrieving site information: {str(e)}"

@mcp.resource("wordpress://api-routes")
async def get_api_routes() -> str:
    """Get available WordPress REST API routes."""
    if wp_client is None:
        return "WordPress client not initialized. Please set the WORDPRESS_URL environment variable."
    
    try:
        # Get API routes from the index
        base_url = wp_client.base_url
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.get(
                f"{base_url}/wp-json",
                auth=wp_client.auth,
                headers={"User-Agent": "WordPress-MCP-Server/1.0"}
            )
            response.raise_for_status()
            info = response.json()
            
        routes = info.get('routes', {})
        
        if not routes:
            return "No API routes found."
        
        formatted_routes = ["Available WordPress API Routes:"]
        
        for route, details in routes.items():
            endpoints = details.get('endpoints', [])
            methods = []
            for endpoint in endpoints:
                methods.extend(endpoint.get('methods', []))
            
            methods_str = ", ".join(set(methods)) if methods else "No methods"
            formatted_routes.append(f"{route} [{methods_str}]")
        
        return "\n".join(formatted_routes)
    
    except Exception as e:
        return f"Error retrieving API routes: {str(e)}"

if __name__ == "__main__":
    import os
    import sys
    
    # Get WordPress URL from environment variable
    wp_url = os.environ.get("WORDPRESS_URL")
    wp_username = os.environ.get("WORDPRESS_USERNAME")
    wp_password = os.environ.get("WORDPRESS_PASSWORD")
    
    if not wp_url:
        print("Error: WORDPRESS_URL environment variable not set.")
        print("Example: WORDPRESS_URL=https://example.com python wordpress_server.py")
        sys.exit(1)
    
    # Initialize WordPress client
    wp_client = WordPressClient(wp_url, wp_username, wp_password)
    
    print(f"Starting WordPress MCP Server for: {wp_url}")
    if wp_username:
        print(f"Authenticated as: {wp_username}")
    
    # Initialize and run the server
    mcp.run(transport='stdio')