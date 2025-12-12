# Agent Documentation

The ChatOps agent is a lightweight Go application that runs on each monitored server.

## Overview

The agent is responsible for:

- **Metrics Collection**: CPU, memory, disk, and network metrics every 5 seconds
- **Docker Management**: Container lifecycle operations
- **Command Execution**: Remote command execution via WebSocket
- **Real-time Communication**: Bidirectional WebSocket connection to API

## Features

- ✅ Lightweight and efficient (single binary)
- ✅ Low resource usage
- ✅ Automatic reconnection
- ✅ Secure API key authentication
- ✅ Docker integration
- ✅ System metrics collection
- ✅ Command execution with output capture

## Architecture

```
┌─────────────────────────────────────────┐
│         Go Agent                        │
├─────────────────────────────────────────┤
│  Components                             │
│  ├── Metrics Collector                  │
│  │   ├── CPU                            │
│  │   ├── Memory                         │
│  │   ├── Disk                           │
│  │   └── Network                        │
│  ├── Docker Client                      │
│  ├── WebSocket Client                   │
│  └── Command Executor                   │
├─────────────────────────────────────────┤
│  Communication                         │
│  ├── WebSocket Connection               │
│  ├── Authentication (API Key)           │
│  └── Message Protocol                   │
└─────────────────────────────────────────┘
```

## Quick Start

1. **Get an API Key**: Create one in the web interface
2. **Download Agent**: Get the binary for your platform
3. **Run Agent**: `./chatops-agent -api-key YOUR_KEY`
4. **Verify**: Check the web interface for metrics

See [Installation Guide](installation.md) for detailed instructions.

## Configuration

The agent can be configured via:

- **Command-line flags**: `-api-key`, `-api-url`
- **Environment variables**: `CHATOPS_API_KEY`, `CHATOPS_API_URL`
- **Config file**: JSON configuration file (optional)

See [Configuration Guide](configuration.md) for details.

## Communication Protocol

### Agent → API

**Message Types**:
- `auth`: Initial authentication
- `metrics`: System metrics data
- `command_response`: Command execution result
- `docker_response`: Docker operation result

### API → Agent

**Message Types**:
- `auth_success`: Authentication confirmation
- `command`: Command execution request
- `docker_command`: Docker operation request

## Metrics Collection

The agent collects the following metrics every 5 seconds:

- **CPU**: Usage percentage per core
- **Memory**: Total, used, available, percentage
- **Disk**: Usage per filesystem
- **Network**: Bytes sent/received per interface

## Docker Support

The agent can manage Docker containers if Docker is installed:

- List containers
- Start/stop/restart containers
- Get container logs
- Container status information

## Security

- **API Key Authentication**: Secure key-based authentication
- **WebSocket Encryption**: TLS/SSL encryption in production
- **No Root Required**: Agent can run as non-root user
- **Minimal Permissions**: Only requires necessary system access

## Troubleshooting

Common issues and solutions:

- **Connection Failed**: Check API URL and network connectivity
- **Authentication Failed**: Verify API key is correct and active
- **No Metrics**: Ensure agent has necessary system permissions
- **Docker Not Working**: Verify Docker is installed and accessible

## Next Steps

- [Installation Guide](installation.md)
- [Configuration Guide](configuration.md)
- [Development Guide](development.md)

