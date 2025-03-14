# WordPress MCP Server Example Usage

This document provides examples of using the WordPress MCP server with Claude.

## Setup

First, ensure you have configured the WordPress MCP server in your Claude for Desktop configuration file as described in the README. Once configured, restart Claude for Desktop to load the server.

## Example Interactions

### Getting Recent Posts

**User Question:**
> What are the recent posts on my WordPress site?

**Claude Response:**
Claude will use the `get_posts` tool to retrieve recent posts from your WordPress site and display them in a formatted list, showing titles, dates, and excerpts.

### Finding Content by Category

**User Question:**
> Show me all posts in the "Technology" category.

**Claude's Process:**
1. Claude will first use the `get_categories` tool to find the ID of the "Technology" category
2. Then use the `get_posts` tool with the appropriate category_id parameter
3. Present the results in a readable format

### Researching Site Content

**User Question:**
> I need information about "artificial intelligence" from my WordPress site. Can you find relevant content?

**Claude's Process:**
1. Claude will use the `search_content` tool with "artificial intelligence" as the query
2. Retrieve matching posts and pages
3. For the most relevant results, it might use `get_post_by_id` to get more details
4. Summarize the findings

### Site Overview

**User Question:**
> Give me an overview of my WordPress site's content.

**Claude's Process:**
1. Retrieve site information using the `wordpress://site-info` resource
2. Get category counts with `get_categories`
3. Count posts using `get_posts`
4. Count pages using `get_pages`
5. Compile a comprehensive overview

### Finding Media

**User Question:**
> What images do I have on my WordPress site?

**Claude's Process:**
Claude will use the `get_media` tool filtered for image types and display the results, including image titles, IDs, and URLs.

### Analyzing User Engagement

**User Question:**
> Which of my recent posts have received the most comments?

**Claude's Process:**
1. Get recent posts with `get_posts`
2. For each post, check comments using `get_comments` with the post's ID
3. Sort and present posts by comment count
4. Provide insights on engagement

### Content Creation and Management

**User Question:**
> I'd like to publish a new blog post about sustainable gardening practices for beginners.

**Claude's Process:**
1. Claude will draft high-quality content based on your request
2. Use the `get_categories` tool to find relevant categories
3. Use the `create_post` tool to publish the post (defaults to draft status for your review)
4. Provide you with the post ID and link where you can preview it

**User Question:**
> Our "About Us" page needs updating with our new mission statement.

**Claude's Process:**
1. Use `get_pages` to locate the About Us page and its ID
2. Retrieve the current content with a specific page request
3. Draft the updated content incorporating the new mission statement
4. Use `update_page` to publish the changes
5. Provide a confirmation with a link to view the updated page

## Advanced Uses

### Content Audit

**User Question:**
> Help me audit my WordPress site's content. I want to know what needs updating.

**Claude's Process:**
1. Get categories, posts, pages using the respective tools
2. Analyze publication dates, content length, and structure
3. Identify old content that might need refreshing
4. Recommend posts for updates based on age and relevance

### SEO Analysis

**User Question:**
> Analyze the SEO aspects of my WordPress posts.

**Claude's Process:**
1. Retrieve posts using `get_posts`
2. For detailed content, use `get_post_by_id`
3. Analyze title lengths, content structure, internal linking
4. Provide SEO recommendations based on content analysis

## Troubleshooting

If Claude responds with errors like "WordPress client not initialized," check that:

1. The `WORDPRESS_URL` environment variable is correctly set in your configuration
2. Your WordPress site is accessible
3. If using authentication, the credentials are correct
4. The WordPress REST API is enabled on your site

For connection timeouts, ensure your WordPress site is responsive and not blocking API requests.