# API Keys

API keys are used for agent authentication.

## Creating API Keys

1. Log into the web interface
2. Navigate to a server
3. Go to the "API Keys" tab
4. Click "Create API Key"
5. **Copy the key immediately** - it's only shown once!

## Using API Keys

Agents use API keys to authenticate via WebSocket:

```json
{
  "type": "auth",
  "api_key": "your-api-key-here"
}
```

## Security Best Practices

1. **Never commit API keys** to version control
2. **Rotate keys regularly**
3. **Revoke compromised keys** immediately
4. **Use one key per server**
5. **Store keys securely** (environment variables, secrets manager)

## Revoking API Keys

You can revoke an API key at any time:

1. Navigate to the server
2. Go to "API Keys" tab
3. Click "Revoke" next to the key

Once revoked, the agent will be disconnected and cannot reconnect.

## Key Format

API keys follow the format:
```
chatops_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Next Steps

- [Authentication Guide](authentication.md)
- [WebSocket API](websocket-api.md)

