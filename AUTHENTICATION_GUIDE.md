# Shopify Admin API Authentication Guide

This guide provides detailed steps for authenticating with Shopify's GraphQL Admin API.

## Authentication Methods

Shopify offers two main authentication approaches:

1. **OAuth for public apps and custom apps created in the Partner Dashboard**
2. **Direct token generation for custom apps created in the Shopify admin**

## Method 1: OAuth Authentication (Partner Dashboard)

This approach is required for public apps and custom apps created in the Shopify Partner Dashboard.

### Step 1: Create an app in the Partner Dashboard

1. Go to [Shopify Partners](https://partners.shopify.com/) and log in
2. Navigate to Apps > Create app
3. Select "Public App" or "Custom App" as appropriate
4. Fill in the app details and save

### Step 2: Configure OAuth

1. In your app settings, go to "App setup"
2. Add a redirect URL (where users will be sent after authorizing your app)
   - For development, use something like: `https://localhost:3000/auth/callback`
3. Save your changes

### Step 3: Note your API credentials

1. Note your API key and API secret key from the app settings
2. Keep these secure and do not share them publicly

### Step 4: Implement the OAuth flow

The OAuth flow involves:

1. Redirecting the merchant to Shopify's authorization URL:
```
https://{shop}.myshopify.com/admin/oauth/authorize?client_id={api_key}&scope={scopes}&redirect_uri={redirect_uri}&state={nonce}
```

2. After the merchant approves, they'll be redirected to your redirect URL with a code parameter
3. Exchange this code for a permanent access token:

```
POST https://{shop}.myshopify.com/admin/oauth/access_token
{
  "client_id": "{api_key}",
  "client_secret": "{api_secret}",
  "code": "{authorization_code}"
}
```

4. Store the returned access token securely
5. Add this token to your `.env` file as `SHOPIFY_ACCESS_TOKEN`

## Method 2: Custom App Token (Shopify Admin)

This approach is simpler but only works for custom apps created in the Shopify admin.

### Step 1: Create a custom app in Shopify admin

1. Log in to your Shopify admin
2. Go to Apps > Develop apps
3. Click "Create an app"
4. Name your app and select "Configure Admin API scopes"

### Step 2: Set required scopes

1. Select all the required API access scopes your app needs
2. Common scopes include:
   - `read_products`, `write_products` for product operations
   - `read_orders`, `write_orders` for order operations
   - `read_customers`, `write_customers` for customer operations
3. Only request the minimum scopes required for your app to function

### Step 3: Generate an access token

1. After configuring scopes, click "Install app"
2. Shopify will generate an Admin API access token
3. **Important**: Copy this token immediately, as you won't be able to see it again
4. Add this token to your `.env` file as `SHOPIFY_ACCESS_TOKEN`

## Setting Up Your Environment Variables

After obtaining your access token through either method:

1. Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```

2. Edit the `.env` file:
```
SHOPIFY_ACCESS_TOKEN=your_access_token_here
SHOPIFY_STORE_NAME=your_store_name_here
SHOPIFY_API_VERSION=2025-01
```

Replace `your_store_name_here` with your store's name (the part before .myshopify.com).

## Testing Your Authentication

After setting up your authentication, you can test it with a simple GraphQL query:

```graphql
query {
  shop {
    name
    myshopifyDomain
    primaryDomain {
      url
    }
  }
}
```

If successful, you should receive shop information in the response.

## Security Best Practices

1. **Never commit your access token to version control**
2. Store your `.env` file outside of version control (add it to `.gitignore`)
3. Rotate your access tokens periodically
4. Only request the specific scopes your app needs
5. Handle tokens securely in your application
6. Consider using a secrets management solution for production environments

## Troubleshooting

If you encounter authentication errors:

1. Verify your access token is correct and not expired
2. Confirm your app has the necessary scopes for the operations you're attempting
3. Check that you're using the correct store name
4. Ensure you're using a supported API version
5. Verify the "X-Shopify-Access-Token" header is being sent correctly

## Additional Resources

- [Shopify Authentication Documentation](https://shopify.dev/apps/auth)
- [Shopify OAuth Flow](https://shopify.dev/apps/auth/oauth)
- [Shopify API Scopes](https://shopify.dev/api/usage/access-scopes)
- [Admin API Rate Limits](https://shopify.dev/api/usage/rate-limits) 