# WordPress MCP Server

A Model Context Protocol (MCP) server that provides tools and resources for interacting with a WordPress site through its REST API.

## Features

This MCP server provides the following capabilities:

### Tools
- `get_posts`: Retrieve and filter WordPress posts
- `get_post_by_id`: Get detailed information about a specific post
- `create_post`: Create a new WordPress blog post
- `update_post`: Update an existing WordPress blog post
- `get_categories`: List WordPress categories
- `get_tags`: List WordPress tags
- `get_pages`: List WordPress pages
- `create_page`: Create a new WordPress page
- `update_page`: Update an existing WordPress page
- `search_content`: Search posts and pages by keyword
- `get_media`: List media items (images, videos, etc.)
- `get_users`: List WordPress users
- `get_comments`: Get comments, optionally for a specific post

### Resources
- `wordpress://site-info`: Get basic site information
- `wordpress://api-routes`: List available WordPress REST API routes

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/wordpress-mcp-server
cd wordpress-mcp-server
```

2. Install the required dependencies:
```bash
pip install "mcp[cli]" httpx
```

## Usage

### Running the server

Set environment variables for your WordPress site:

```bash
export WORDPRESS_URL="https://example.com"
# Optional authentication (for protected endpoints)
export WORDPRESS_USERNAME="your_username"
export WORDPRESS_PASSWORD="your_password"
```

Then run the server:

```bash
python wordpress_server.py
```

### Using with Claude for Desktop

To use this server with Claude for Desktop, edit your Claude for Desktop configuration file:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Add the following configuration:

```json
{
  "mcpServers": {
    "wordpress": {
      "command": "python",
      "args": [
        "/absolute/path/to/wordpress_server.py"
      ],
      "env": {
        "WORDPRESS_URL": "https://example.com",
        "WORDPRESS_USERNAME": "your_username",
        "WORDPRESS_PASSWORD": "your_password"
      }
    }
  }
}
```

Replace the placeholder values with your actual WordPress site information.

### Using with MCP Inspector

For testing and debugging, you can use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector):

```bash
npx @modelcontextprotocol/inspector python wordpress_server.py
```

## API Reference

### Environment Variables

- `WORDPRESS_URL` (required): The base URL of your WordPress site
- `WORDPRESS_USERNAME` (optional): Username for authenticated requests
- `WORDPRESS_PASSWORD` (optional): Password for authenticated requests

### Tool Parameters

#### get_posts
- `limit` (int, default=10): Maximum number of posts to return
- `page` (int, default=1): Page number for pagination
- `category_id` (int, optional): Filter posts by category ID
- `tag_id` (int, optional): Filter posts by tag ID
- `search` (string, optional): Search term to filter posts

#### get_post_by_id
- `post_id` (int, required): ID of the post to retrieve

#### get_categories
- `limit` (int, default=20): Maximum number of categories to return

#### get_tags
- `limit` (int, default=20): Maximum number of tags to return

#### get_pages
- `limit` (int, default=10): Maximum number of pages to return

#### search_content
- `query` (string, required): Search term
- `limit` (int, default=10): Maximum number of results to return

#### get_media
- `limit` (int, default=10): Maximum number of media items to return

#### get_users
- `limit` (int, default=10): Maximum number of users to return

#### create_post
- `title` (string, required): Title of the post
- `content` (string, required): Content of the post (can include HTML)
- `status` (string, default="draft"): Post status (options: draft, publish, private, pending)
- `categories` (list of int, optional): List of category IDs to assign
- `tags` (list of int, optional): List of tag IDs to assign

#### update_post
- `post_id` (int, required): ID of the post to update
- `title` (string, optional): New title of the post
- `content` (string, optional): New content of the post (can include HTML)
- `status` (string, optional): New post status (options: draft, publish, private, pending)
- `categories` (list of int, optional): New list of category IDs to assign
- `tags` (list of int, optional): New list of tag IDs to assign

#### get_pages
- `limit` (int, default=10): Maximum number of pages to return

#### create_page
- `title` (string, required): Title of the page
- `content` (string, required): Content of the page (can include HTML)
- `status` (string, default="draft"): Page status (options: draft, publish, private, pending)
- `parent_id` (int, optional): Parent page ID for hierarchical pages

#### update_page
- `page_id` (int, required): ID of the page to update
- `title` (string, optional): New title of the page
- `content` (string, optional): New content of the page (can include HTML)
- `status` (string, optional): New page status (options: draft, publish, private, pending)
- `parent_id` (int, optional): New parent page ID for hierarchical pages

## Limitations

- Some WordPress features might not be available depending on your site configuration and plugins
- Authentication is required for creating and updating content
- Some WordPress security plugins may restrict REST API access
- The server depends on the WordPress REST API, which may vary between WordPress versions
- Pagination is implemented through the `limit` and `page` parameters
- Media content is referenced by URL but not directly accessible through the server
- The server depends on the WordPress REST API, which may vary between WordPress versions

## License

MIT