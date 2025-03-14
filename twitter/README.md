For the Twitter API v2 endpoints used in this MCP server, you need to use a Bearer token rather than the traditional OAuth 1.0a credentials (API key, API secret, access token, and access token secret). Here's how to get the right token:

In the Twitter Developer Portal, navigate to your project or app
Look for "Bearer Token" or sometimes called "App-only Bearer Token"
This is a long string that typically starts with "AAAA"

To use this Twitter API MCP server with Claude for Desktop, you'll need to edit your Claude Desktop configuration file. Here's how to set it up:

First, locate your Claude Desktop configuration file:

On macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
On Windows: %APPDATA%\Claude\claude_desktop_config.json

Edit the file (or create it if it doesn't exist) with the following configuration:
{
  "mcpServers": {
    "twitter": {
      "command": "python",
      "args": [
        "/absolute/path/to/twitter_server.py"
      ],
      "env": {
        "TWITTER_API_TOKEN": "your_actual_twitter_bearer_token_here"
      }
    }
  }
}

Make sure to:

Replace /absolute/path/to/twitter_server.py with the actual absolute path to your script
Replace your_actual_twitter_bearer_token_here with your valid Twitter Bearer token
Use the correct Python command for your system (might be python3 on macOS)


After saving the configuration, restart Claude for Desktop to load the new MCP server configuration.

Once Claude for Desktop restarts, you should see the Twitter API server available, and you can use the tools to post and search tweets. You should see a hammer icon in the input area when the server is successfully connected.
If you're having trouble connecting, you can check the logs at:

On macOS: ~/Library/Logs/Claude/mcp-server-twitter-api.log
On Windows: %APPDATA%\Claude\logs\mcp-server-twitter-api.log

These logs will help you troubleshoot any issues with the connection or API requests.