# ChatOps Agent

The ChatOps agent is a lightweight Go application that runs on each server to collect metrics, manage Docker containers, and execute commands.

## Features

- System metrics collection (CPU, Memory, Disk, Network)
- Docker container management
- Command execution
- Secure API key authentication
- Real-time metrics reporting

## Installation

### Build from source

```bash
go build -o chatops-agent ./main.go
```

### Usage

```bash
./chatops-agent \
  -api-url http://localhost:8000 \
  -api-key YOUR_API_KEY
```

**Note**: The server ID is automatically determined from the API key - you don't need to specify it!

### Environment Variables

- `CHATOPS_API_URL` - API server URL (default: http://localhost:8000)
- `CHATOPS_API_KEY` - API key for authentication (required)

### Command Line Flags

- `-api-url` - API server URL
- `-api-key` - API key for authentication
- `-server-id` - Server ID
- `-config` - Path to config file (optional)

## Getting an API Key

1. Log into the ChatOps web interface
2. Navigate to a server's detail page
3. Create an API key for that server
4. Copy the key (it's only shown once!)
5. Use it when starting the agent

## Development

```bash
# Run the agent
go run main.go -api-key YOUR_KEY -server-id YOUR_SERVER_ID

# Build
go build -o chatops-agent

# Test
go test ./...
```

