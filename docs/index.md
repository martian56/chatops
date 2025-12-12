# ChatOps Documentation

Welcome to the ChatOps documentation! ChatOps is a comprehensive server monitoring and management platform that enables you to monitor, manage, and control your servers from a single, intuitive web dashboard.

## What is ChatOps?

ChatOps is a unified server monitoring and DevOps platform that provides:

- **Real-time Monitoring**: Live metrics for CPU, memory, disk, and network usage
- **Docker Management**: Control containers with one-click actions
- **Alert System**: Configure and monitor performance thresholds
- **Remote Terminal**: Execute commands remotely via web terminal
- **Audit Logging**: Complete history of all system activity

## Key Features

### 🎯 Core Capabilities

- **Multi-Server Management**: Monitor and manage multiple servers from one dashboard
- **Real-time Updates**: WebSocket-based live updates for metrics and logs
- **Secure Authentication**: JWT-based authentication with API key support
- **Docker Integration**: Full Docker container lifecycle management
- **Alert Management**: Configurable thresholds with automatic alerting
- **Command Execution**: Secure remote command execution with full logging

### 🏗️ Architecture

ChatOps follows a three-tier architecture:

1. **Web Frontend** (React/TypeScript) - Modern, responsive UI
2. **API Backend** (FastAPI/Python) - RESTful API with WebSocket support
3. **Agent** (Go) - Lightweight agent deployed on monitored servers

## Quick Navigation

### For Users

- [Getting Started](getting-started/index.md) - Start using ChatOps
- [Agent Installation](agent/installation.md) - Deploy agents on your servers
- [API Reference](api/index.md) - Integrate with the API

### For Developers

- [Architecture Overview](architecture/index.md) - Understand the system design
- [Development Setup](contributing/development.md) - Set up your development environment
- [API Documentation](api/rest-endpoints.md) - Detailed API reference

### For DevOps

- [Deployment Guide](deployment/index.md) - Deploy ChatOps in production
- [Docker Setup](deployment/docker.md) - Container-based deployment
- [Production Best Practices](deployment/production.md) - Production recommendations

## Documentation Structure

This documentation is organized into the following sections:

- **[Getting Started](getting-started/index.md)**: Installation and quick start guides
- **[Architecture & Design](architecture/index.md)**: System architecture and design decisions
- **[API Reference](api/index.md)**: Complete API documentation
- **[Agent](agent/index.md)**: Agent installation and configuration
- **[Frontend](frontend/index.md)**: Frontend development guide
- **[Technologies](technologies/index.md)**: Technology stack overview
- **[Deployment](deployment/index.md)**: Deployment guides and best practices
- **[Contributing](contributing/index.md)**: Development and contribution guidelines

## Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/martian56/chatops/issues)
- **Documentation**: Browse the sections above for detailed information
- **API Docs**: Interactive API documentation at `/docs` endpoint when running the API

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.

---

**Ready to get started?** Check out the [Quick Start Guide](getting-started/quick-start.md)!

