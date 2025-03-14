from mcp.server.fastmcp import FastMCP
import httpx
import os
from typing import Optional, List, Dict, Any
import json

# Initialize FastMCP server
mcp = FastMCP("twitter-api")

# Environment variables for API auth
API_TOKEN = os.getenv("TWITTER_API_TOKEN")
BASE_URL = "https://api.twitter.com/2"

# Helper function for API requests
async def twitter_request(
    method: str, 
    endpoint: str, 
    params: Optional[Dict[str, Any]] = None, 
    json_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Make a request to the Twitter API with proper error handling."""
    url = f"{BASE_URL}/{endpoint}"
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=json_data, timeout=30.0)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_body = e.response.text
            return {
                "error": True,
                "status_code": e.response.status_code,
                "message": f"HTTP Error: {e.response.status_code}",
                "details": error_body
            }
        except Exception as e:
            return {
                "error": True,
                "message": f"Error: {str(e)}"
            }

@mcp.tool()
async def post_tweet(text: str, reply_to_tweet_id: Optional[str] = None, quote_tweet_id: Optional[str] = None) -> str:
    """Post a new tweet to Twitter.
    
    Args:
        text: The content of the tweet (required)
        reply_to_tweet_id: ID of the tweet to reply to (optional)
        quote_tweet_id: ID of the tweet to quote (optional)
    
    Returns:
        Result of the tweet creation including tweet ID and URL
    """
    # Validate API token
    if not API_TOKEN:
        return "Error: Twitter API token not set. Please set the TWITTER_API_TOKEN environment variable."
    
    # Build the tweet payload
    payload = {"text": text}
    
    # Add reply information if provided
    if reply_to_tweet_id:
        payload["reply"] = {"in_reply_to_tweet_id": reply_to_tweet_id}
    
    # Add quote tweet ID if provided
    if quote_tweet_id:
        payload["quote_tweet_id"] = quote_tweet_id
        
    # Ensure we're not trying to both reply and quote at the same time
    if reply_to_tweet_id and quote_tweet_id:
        return "Error: Cannot both reply to and quote a tweet in the same request."
    
    # Make the API request
    result = await twitter_request("POST", "tweets", json_data=payload)
    
    # Format the response
    if "error" in result and result["error"]:
        return f"Failed to post tweet: {result['message']}\nDetails: {result.get('details', 'No details provided')}"
    
    # Format successful response
    tweet_id = result.get("data", {}).get("id", "Unknown")
    tweet_text = result.get("data", {}).get("text", "")
    return (
        f"Tweet posted successfully!\n"
        f"Tweet ID: {tweet_id}\n"
        f"Tweet URL: https://twitter.com/i/web/status/{tweet_id}\n"
        f"Content: {tweet_text}"
    )

@mcp.tool()
async def search_recent_tweets(
    query: str,
    max_results: Optional[int] = 10,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    sort_order: Optional[str] = "recency"
) -> str:
    """Search for recent tweets matching a query.
    
    Args:
        query: Search query text (required)
        max_results: Number of results to return (default: 10, max: 100)
        start_time: Oldest timestamp to include (format: YYYY-MM-DDTHH:mm:ssZ)
        end_time: Newest timestamp to include (format: YYYY-MM-DDTHH:mm:ssZ)
        sort_order: Order of results - "recency" or "relevancy" (default: recency)
    
    Returns:
        Formatted list of matching tweets
    """
    # Validate API token
    if not API_TOKEN:
        return "Error: Twitter API token not set. Please set the TWITTER_API_TOKEN environment variable."
    
    # Validate parameters
    if max_results and (max_results < 10 or max_results > 100):
        return "Error: max_results must be between 10 and 100."
    
    if sort_order and sort_order not in ["recency", "relevancy"]:
        return "Error: sort_order must be either 'recency' or 'relevancy'."
    
    # Build the query parameters
    params = {
        "query": query,
        "max_results": max_results,
        "sort_order": sort_order,
        "tweet.fields": "created_at,author_id,public_metrics",
        "expansions": "author_id",
        "user.fields": "username,name,verified"
    }
    
    # Add optional parameters if provided
    if start_time:
        params["start_time"] = start_time
    
    if end_time:
        params["end_time"] = end_time
    
    # Make the API request
    result = await twitter_request("GET", "tweets/search/recent", params=params)
    
    # Handle errors
    if "error" in result and result["error"]:
        return f"Failed to search tweets: {result['message']}\nDetails: {result.get('details', 'No details provided')}"
    
    # Process results
    tweets = result.get("data", [])
    users = {user["id"]: user for user in result.get("includes", {}).get("users", [])}
    
    if not tweets:
        return "No tweets found matching your query."
    
    # Format the results
    formatted_results = ["=== Search Results ===\n"]
    
    for tweet in tweets:
        author_id = tweet.get("author_id", "Unknown")
        author = users.get(author_id, {})
        author_name = author.get("name", "Unknown")
        author_username = author.get("username", "Unknown")
        verified = "✓" if author.get("verified", False) else ""
        
        tweet_id = tweet.get("id", "Unknown")
        created_at = tweet.get("created_at", "Unknown date")
        text = tweet.get("text", "")
        
        # Get metrics if available
        metrics = tweet.get("public_metrics", {})
        likes = metrics.get("like_count", 0)
        retweets = metrics.get("retweet_count", 0)
        replies = metrics.get("reply_count", 0)
        
        tweet_info = (
            f"Tweet by {author_name} (@{author_username}) {verified}\n"
            f"ID: {tweet_id}\n"
            f"Posted: {created_at}\n"
            f"Likes: {likes} | Retweets: {retweets} | Replies: {replies}\n"
            f"URL: https://twitter.com/i/web/status/{tweet_id}\n"
            f"Content: {text}\n"
            f"-------------------\n"
        )
        
        formatted_results.append(tweet_info)
    
    return "\n".join(formatted_results)

# Resource to provide Twitter API documentation
@mcp.resource("twitter://api-docs")
def get_api_docs() -> str:
    """Twitter API documentation for reference."""
    return """
    Twitter API v2 Documentation
    
    # Posting Tweets
    POST /2/tweets
    Required fields:
    - text: The content of the tweet
    
    Optional fields:
    - reply.in_reply_to_tweet_id: ID of a tweet to reply to
    - quote_tweet_id: ID of a tweet to quote
    
    # Searching Recent Tweets
    GET /2/tweets/search/recent
    Required parameters:
    - query: Search query text
    
    Optional parameters:
    - max_results: Number of results (10-100)
    - start_time: Oldest UTC timestamp (YYYY-MM-DDTHH:mm:ssZ)
    - end_time: Newest UTC timestamp (YYYY-MM-DDTHH:mm:ssZ)
    - sort_order: "recency" or "relevancy"
    """

# Run the server when the script is executed directly
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')