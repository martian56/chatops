# Agent Installation Guide

## Quick Start

### 1. Create an API Key

1. Log into the ChatOps web interface
2. Navigate to the server you want to monitor
3. Click on the **"API Keys"** tab
4. Click **"Create API Key"**
5. Optionally give it a name (e.g., "Production Server Agent")
6. **Copy the API key immediately** - it's only shown once!

### 2. Install the Agent

#### Build the Agent

```bash
cd agent
go build -o chatops-agent
```

#### Run the Agent

```bash
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

