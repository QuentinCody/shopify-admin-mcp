# Shopify Admin API MCP Server

This MCP (Model Context Protocol) server provides access to Shopify's GraphQL Admin API through a standardized interface that AI agents can interact with.

## Setup Instructions

1. Clone this repository
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Copy the `.env.example` file to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

4. Edit the `.env` file with your Shopify Admin API credentials.

## Authentication

The Shopify GraphQL Admin API requires authentication via an access token. There are two main ways to obtain this token:

### For Public and Custom Apps (OAuth)

1. Create a Shopify app in the [Shopify Partner Dashboard](https://partners.shopify.com/)
2. Set up OAuth by registering a redirect URL
3. Request the necessary API scopes during the OAuth process
4. After a successful OAuth flow, you'll receive an access token
5. Store this token in your `.env` file

### For Custom Apps (Admin)

1. Go to your Shopify admin panel
2. Navigate to Apps > Develop apps
3. Create a custom app
4. Add the required Admin API access scopes
5. Generate an access token
6. Store this token in your `.env` file

## Configuration for Client

To use this MCP server with your AI agent, add the following configuration to your client config JSON file:

```json
{
  "mcp": {
    "servers": {
      "shopify": {
        "command": ["python", "path/to/shopify_mcp_server.py"],
        "tools": ["shopify_execute_graphql"]
      }
    }
  }
}
```

## Usage Examples

Here are some example GraphQL queries you can run using the `shopify_execute_graphql` tool:

### List Products

```graphql
query {
  products(first: 5) {
    edges {
      node {
        id
        title
        description
      }
    }
  }
}
```

### Create Product

```graphql
mutation {
  productCreate(input: {
    title: "New Product",
    productType: "Accessories",
    vendor: "My Store"
  }) {
    product {
      id
      title
    }
    userErrors {
      field
      message
    }
  }
}
```

## Rate Limiting Considerations

Shopify's GraphQL API uses a calculated cost system for rate limiting. Each query has a cost based on the complexity and number of fields requested. Your API request will return the cost information, which you should monitor to avoid hitting rate limits.

## More Information

- [Shopify GraphQL Admin API Documentation](https://shopify.dev/api/admin-graphql)
- [Authentication with Shopify](https://shopify.dev/apps/auth)
- [Rate Limits](https://shopify.dev/api/usage/rate-limits) 