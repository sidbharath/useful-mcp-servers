# MCP Servers Collection

A collection of MCP (Model Context Protocol) servers for enhancing AI capabilities.

## Included Servers

- **Twitter API**: Post tweets and search recent tweets
- **Wordrpess**: Get, create, update and delete posts

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sidbharath/useful-mcp-servers.git
cd mcp-servers
```

2. Install dependencies:
```bash
npm install -r requirements.txt
```

3. Configure your API keys and tokens (see individual server READMEs)

#Usage with Claude Desktop

Configure Claude for Desktop to use these servers by editing your configuration file:

On macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
On Windows: %APPDATA%\Claude\claude_desktop_config.json

For example:
```json
{
  "mcpServers": {
    "twitter": {
      "command": "python",
      "args": [
        "/absolute/path/to/useful-mcp-servers/twitter/twitter_server.py"
      ],
      "env": {
        "TWITTER_API_TOKEN": "your_bearer_token_here"
      }
    }
  }
}
```