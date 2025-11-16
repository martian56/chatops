# Agent Installation Guide

## Quick Start

### Installation Methods

- **Debian/Ubuntu (.deb package)** - Recommended for Debian-based systems
- **Binary Archive** - For any Linux distribution

### 1. Create an API Key

1. Log into the ChatOps web interface
2. Navigate to the server you want to monitor
3. Click on the **"API Keys"** tab
4. Click **"Create API Key"**
5. Optionally give it a name (e.g., "Production Server Agent")
6. **Copy the API key immediately** - it's only shown once!

### 2. Install the Agent

#### Option A: Debian/Ubuntu Package (Recommended)

```bash
# Download the .deb package from GitHub Releases
wget https://github.com/your-org/chatops/releases/download/v1.0.0/chatops-agent_1.0.0_amd64.deb

# Install the package
sudo dpkg -i chatops-agent_1.0.0_amd64.deb
sudo apt-get install -f  # Install dependencies if needed

# Edit the service file with your API key
sudo systemctl edit chatops-agent.service
# Add: Environment="CHATOPS_API_KEY=your-api-key-here"

# Or edit the service file directly
sudo nano /lib/systemd/system/chatops-agent.service
# Replace YOUR_API_KEY_HERE with your actual API key

# Reload systemd and start the service
sudo systemctl daemon-reload
sudo systemctl enable chatops-agent
sudo systemctl start chatops-agent

# Check status
sudo systemctl status chatops-agent
```

#### Option B: Binary Archive

```bash
# Download from GitHub Releases
wget https://github.com/your-org/chatops/releases/download/v1.0.0/chatops-agent-linux-amd64-1.0.0.tar.gz
tar -xzf chatops-agent-linux-amd64-1.0.0.tar.gz

# Run the agent
./chatops-agent-linux-amd64 -api-key YOUR_API_KEY_HERE
```

#### Option C: Build from Source

```bash
cd agent
go build -o chatops-agent
./chatops-agent -api-key YOUR_API_KEY_HERE
```

Or using environment variables:

```bash
export CHATOPS_API_KEY="your-api-key-here"
export CHATOPS_API_URL="http://your-api-server:8000"  # Optional, defaults to localhost:8000
./chatops-agent
```

### 3. Verify Connection

The agent will:
- Automatically fetch its server ID from the API key
- Connect to the API
- Start sending metrics every 5 seconds

Check the web interface - you should see metrics appearing in real-time!

## Running as a Service

### Linux (systemd)

Create `/etc/systemd/system/chatops-agent.service`:

```ini
[Unit]
Description=ChatOps Agent
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/agent
ExecStart=/path/to/agent/chatops-agent -api-key YOUR_API_KEY
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable chatops-agent
sudo systemctl start chatops-agent
```

### Windows (Service)

Use NSSM (Non-Sucking Service Manager) or Task Scheduler to run as a service.

## Troubleshooting

- **"Failed to fetch server ID"**: Check that your API key is correct and active
- **"API returned status 401"**: Your API key may be inactive or expired
- **No metrics appearing**: Check that the agent is running and can reach the API server

