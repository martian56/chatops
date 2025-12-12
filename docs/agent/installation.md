# Agent Installation

Complete installation guide for the ChatOps agent.

## Prerequisites

- Linux/Unix system (x86_64 or ARM64)
- Network access to ChatOps API
- Optional: Docker installed for container management

## Installation Methods

### Method 1: Debian/Ubuntu Package (Recommended)

```bash
# Download the .deb package
wget https://github.com/martian56/chatops/releases/download/v1.0.3/chatops-agent_1.0.3_amd64.deb

# Install the package
sudo dpkg -i chatops-agent_1.0.3_amd64.deb
sudo apt-get install -f  # Install dependencies if needed

# Configure the API key
sudo systemctl edit chatops-agent.service
# Add: Environment="CHATOPS_API_KEY=your-api-key-here"

# Or edit the service file directly
sudo nano /usr/lib/systemd/system/chatops-agent.service
# Replace YOUR_API_KEY_HERE with your actual API key

# Start the service
sudo systemctl daemon-reload
sudo systemctl enable chatops-agent
sudo systemctl start chatops-agent

# Check status
sudo systemctl status chatops-agent
```

### Method 2: Binary Installation

```bash
# Download the binary archive
wget https://github.com/martian56/chatops/releases/download/v1.0.3/chatops-agent-linux-amd64-1.0.3.tar.gz
tar -xzf chatops-agent-linux-amd64-1.0.3.tar.gz

# Run the agent
./chatops-agent-linux-amd64 -api-key YOUR_API_KEY_HERE
```

### Method 3: Build from Source

```bash
# Clone the repository
git clone https://github.com/martian56/chatops.git
cd chatops/agent

# Build the agent
go build -o chatops-agent ./main.go

# Run the agent
./chatops-agent -api-key YOUR_API_KEY_HERE
```

## Configuration

### Environment Variables

```bash
export CHATOPS_API_KEY="your-api-key-here"
export CHATOPS_API_URL="https://your-chatops-instance.com"  # Optional
./chatops-agent
```

### Command-line Flags

```bash
./chatops-agent \
  -api-key YOUR_API_KEY \
  -api-url https://your-chatops-instance.com
```

## Running as a Service

### systemd Service

Create `/etc/systemd/system/chatops-agent.service`:

```ini
[Unit]
Description=ChatOps Agent
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/agent
Environment="CHATOPS_API_KEY=your-api-key-here"
Environment="CHATOPS_API_URL=https://your-chatops-instance.com"
ExecStart=/path/to/agent/chatops-agent
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable chatops-agent
sudo systemctl start chatops-agent
```

### Windows Service

Use NSSM (Non-Sucking Service Manager) or Task Scheduler.

## Verification

1. Check agent logs:
   ```bash
   sudo journalctl -u chatops-agent -f
   ```

2. Verify in web interface:
   - Server status should show "ONLINE"
   - Metrics should appear in real-time
   - Docker containers should be listed (if Docker installed)

## Uninstallation

### Debian/Ubuntu Package

```bash
sudo systemctl stop chatops-agent
sudo systemctl disable chatops-agent
sudo dpkg -r chatops-agent
```

### Binary Installation

```bash
# Stop the agent
pkill chatops-agent

# Remove files
rm -f chatops-agent chatops-agent-linux-*
```

## Troubleshooting

### Connection Issues

- Verify API URL is correct
- Check network connectivity
- Ensure firewall allows outbound connections

### Authentication Issues

- Verify API key is correct
- Check API key is active in web interface
- Ensure API key hasn't been revoked

### Metrics Not Appearing

- Wait a few seconds (metrics sent every 5 seconds)
- Check agent logs for errors
- Verify agent has necessary system permissions

## Next Steps

- [Configuration Guide](configuration.md)
- [Development Guide](development.md)

