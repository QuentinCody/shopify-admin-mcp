import os
import httpx
import json
import sys
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from typing import Any, Dict, Optional

# Use absolute path to the script's directory instead of relying on current working directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Look for .env file using absolute path
env_path = os.path.join(script_dir, '.env')
load_dotenv(dotenv_path=env_path)

# Shopify Configuration
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE_NAME = os.getenv("SHOPIFY_STORE_NAME")
SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2025-01")  # Default to latest API version

# Validate essential configuration
if not all([SHOPIFY_ACCESS_TOKEN, SHOPIFY_STORE_NAME]):
    print("ERROR: Shopify credentials not found in .env file.", file=sys.stderr)
    # In a real app, you might exit or raise an exception

# Construct the Shopify GraphQL endpoint
SHOPIFY_API_URL = f"https://{SHOPIFY_STORE_NAME}.myshopify.com/admin/api/{SHOPIFY_API_VERSION}/graphql.json"

# Initialize MCP server
mcp = FastMCP("shopify", version="0.1.0")
print("Shopify MCP Server initialized.", file=sys.stderr)

async def execute_shopify_graphql(query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Makes an authenticated GraphQL request to Shopify's Admin API.
    Handles authentication and error checking.
    """
    if not SHOPIFY_ACCESS_TOKEN:
        return {"errors": [{"message": "Server missing Shopify access token."}]}
    
    if not SHOPIFY_STORE_NAME:
        return {"errors": [{"message": "Shopify store name not configured."}]}

    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json",
        "User-Agent": "MCPShopifyServer/0.1.0"
    }

    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                SHOPIFY_API_URL,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()  # Raise HTTP errors (4xx, 5xx)
            result = response.json()
            
            # Check for GraphQL errors within the response body
            if "errors" in result:
                print(f"GraphQL Errors detected", file=sys.stderr)
            
            return result
        except httpx.RequestError as e:
            print(f"HTTP Request Error", file=sys.stderr)
            return {"errors": [{"message": "HTTP Request Error connecting to Shopify"}]}
        except httpx.HTTPStatusError as e:
            print(f"HTTP Status Error: {e.response.status_code}", file=sys.stderr)
            return {"errors": [{"message": f"HTTP Status Error: {e.response.status_code}"}]}
        except Exception as e:
            print(f"Error during Shopify request", file=sys.stderr)
            return {"errors": [{"message": "An unexpected error occurred"}]}

@mcp.tool()
async def shopify_execute_graphql(query: str, variables: Dict[str, Any] = None) -> str:
    """
    Use this tool to query Shopify store data or perform store management operations through the Shopify Admin API.
    Perfect for retrieving product information, managing inventory, processing orders, or updating store content.
    **Before using this tool, make sure run an introspection query to get the schema of the object types and fields.**
    This tool executes arbitrary GraphQL queries/mutations with the Shopify Admin API, providing access to all 
    available operations permitted by your access token's scopes.
    
    ## Common Operation Patterns

    ### Fetching products
    ```graphql
    query GetProducts {
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

    ### Fetching orders
    ```graphql
    query GetOrders {
      orders(first: 5) {
        edges {
          node {
            id
            name
            totalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
          }
        }
      }
    }
    ```

    ### Creating a product
    ```graphql
    mutation CreateProduct($input: ProductInput!) {
      productCreate(input: $input) {
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
    Variables: `{"input": {"title": "New Product", "productType": "Accessories"}}`

    ## Response Parsing
    
    Shopify uses a nested structure with connection patterns. Here's how to navigate responses:
    
    1. Extract nodes from edges: Shopify returns paginated data in `edges→node` format
    ```python
    # Example response parsing
    response = json.loads(result)
    products = [edge["node"] for edge in response["data"]["products"]["edges"]]
    ```
    
    2. Handle pagination by using the pageInfo object:
    ```graphql
    query GetProducts {
      products(first: 5) {
        pageInfo {
          hasNextPage
          endCursor
        }
        edges {
          node {
            id
            title
          }
        }
      }
    }
    ```
    
    Then for subsequent requests, use the endCursor:
    ```graphql
    query GetMoreProducts($cursor: String!) {
      products(first: 5, after: $cursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        edges {
          node {
            id
            title
          }
        }
      }
    }
    ```
    Variables: `{"cursor": "endCursorFromPreviousRequest"}`

    ## Error Handling Tips
    - Check for the "errors" array in the response
    - For mutations, check the "userErrors" field for validation issues
    - Common error reasons:
      - Invalid GraphQL syntax: verify query structure
      - Unknown fields: check field names through introspection
      - Missing required fields: ensure all required fields are in queries
      - Permission issues: verify API token has appropriate access scopes
      - Rate limits: Shopify has query cost limits which may be exceeded

    ## Advanced: Schema Introspection
    You can discover the schema using introspection:
    ```graphql
    query TypeQuery($name: String!) {
      __type(name: $name) {
        name
        description
        fields {
          name
          description
        }
      }
    }
    ```
    Variables: `{"name": "Product"}`

    Args:
        query: The complete GraphQL query or mutation to execute.
        variables: Optional dictionary of variables for the query. Should match
                  the parameter names defined in the query with appropriate types.

    Returns:
        JSON string containing the complete response from Shopify, including data and errors if any.
    """
    # Make the API call
    result = await execute_shopify_graphql(query, variables)

    # Return the raw result as JSON
    return json.dumps(result)

if __name__ == "__main__":
    print("Starting Shopify MCP server...", file=sys.stderr)
    # Basic check before running
    if not all([SHOPIFY_ACCESS_TOKEN, SHOPIFY_STORE_NAME]):
        print("FATAL: Cannot start server, Shopify credentials missing.", file=sys.stderr)
    else:
        try:
            mcp.run(transport='stdio')
            print("Server stopped.", file=sys.stderr)
        except Exception as e:
            print(f"Error running server: {e}", file=sys.stderr) 