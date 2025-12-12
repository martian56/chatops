# Agent Configuration

Configuration options for the ChatOps agent.

## Configuration Methods

### Command-line Flags

```bash
./chatops-agent \
  -api-key YOUR_API_KEY \
  -api-url https://your-chatops-instance.com
```

### Environment Variables

```bash
export CHATOPS_API_KEY="your-api-key-here"
export CHATOPS_API_URL="https://your-chatops-instance.com"
./chatops-agent
```

### Config File

Create a JSON config file:

```json
{
  "api_key": "your-api-key-here",
  "api_url": "https://your-chatops-instance.com"
}
```

Use with:
```bash
./chatops-agent -config /path/to/config.json
```

## Configuration Options

### API Key

- **Required**: Yes
- **Flag**: `-api-key`
- **Env**: `CHATOPS_API_KEY`
- **Description**: API key for authentication

### API URL

- **Required**: No (default: https://chatops.onrender.com)
- **Flag**: `-api-url`
- **Env**: `CHATOPS_API_URL`
- **Description**: ChatOps API server URL

## Defaults

- **API URL**: `https://chatops.onrender.com`
- **Metrics Interval**: 5 seconds
- **Reconnection Delay**: Exponential backoff starting at 1 second

## Next Steps

- [Installation Guide](installation.md)
- [Development Guide](development.md)

