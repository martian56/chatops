# Agent Development

Development guide for the ChatOps agent.

## Prerequisites

- Go 1.24+
- Docker (optional, for testing Docker features)

## Building

```bash
cd agent
go build -o chatops-agent ./main.go
```

## Running Locally

```bash
./chatops-agent -api-key YOUR_API_KEY -api-url http://localhost:8000
```

## Project Structure

```
agent/
├── main.go                 # Entry point
├── internal/
│   ├── agent/              # Agent core logic
│   ├── api/                # API client
│   ├── config/             # Configuration
│   ├── metrics/            # Metrics collection
│   └── pkg/                # Shared packages
└── package/                # Packaging scripts
```

## Testing

```bash
go test ./...
```

## Contributing

1. Follow Go best practices
2. Write tests for new features
3. Update documentation
4. Submit pull request

## Next Steps

- [Installation Guide](installation.md)
- [Configuration Guide](configuration.md)

