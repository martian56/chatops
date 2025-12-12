# Quick Start Guide

Get up and running with ChatOps in minutes!

## Step 1: Access the Web Interface

1. Navigate to your ChatOps instance URL
2. Click **"Register"** to create a new account
3. Fill in your details:
   - Email address
   - Username
   - Password (minimum 8 characters)
   - Full name
4. Click **"Create Account"**

## Step 2: Add Your First Server

1. After logging in, navigate to **"Servers"** from the sidebar
2. Click **"Add Server"** button
3. Fill in the server details:
   - **Name**: A descriptive name (e.g., "Production Web Server")
   - **Host**: IP address or hostname (optional, for reference)
   - **Port**: SSH port (optional, for reference)
4. Click **"Create"**

## Step 3: Generate an API Key

1. Click on your newly created server
2. Navigate to the **"API Keys"** tab
3. Click **"Create API Key"**
4. Optionally give it a name (e.g., "Main Agent")
5. **⚠️ IMPORTANT**: Copy the API key immediately - it's only shown once!

## Step 4: Install the Agent

### Option A: Debian/Ubuntu Package (Recommended)

```bash
# Download the .deb package
wget https://github.com/martian56/chatops/releases/download/v1.0.3/chatops-agent_1.0.3_amd64.deb

# Install the package
sudo dpkg -i chatops-agent_1.0.3_amd64.deb
sudo apt-get install -f  # Install dependencies if needed

# Configure the API key
sudo systemctl edit chatops-agent.service
# Add: Environment="CHATOPS_API_KEY=your-api-key-here"

# Start the service
sudo systemctl daemon-reload
sudo systemctl enable chatops-agent
sudo systemctl start chatops-agent

# Check status
sudo systemctl status chatops-agent
```

### Option B: Binary Installation

```bash
# Download the binary
wget https://github.com/martian56/chatops/releases/download/v1.0.3/chatops-agent-linux-amd64-1.0.3.tar.gz
tar -xzf chatops-agent-linux-amd64-1.0.3.tar.gz

# Run the agent
./chatops-agent-linux-amd64 -api-key YOUR_API_KEY_HERE
```

### Option C: Environment Variables

```bash
export CHATOPS_API_KEY="your-api-key-here"
export CHATOPS_API_URL="https://your-chatops-instance.com"  # Optional
./chatops-agent
```

## Step 5: Verify Connection

1. Return to the ChatOps web interface
2. Navigate to your server's detail page
3. You should see:
   - Server status: **ONLINE** (green indicator)
   - Real-time metrics appearing in the Metrics tab
   - Docker containers listed (if Docker is installed)

## What Happens Next?

Once the agent is connected:

- **Metrics**: System metrics (CPU, memory, disk, network) are collected every 5 seconds
- **Docker**: Container information is available for management
- **Logs**: System and application logs are accessible
- **Terminal**: Remote command execution is enabled

## Troubleshooting

### Agent Not Connecting

- **Check API Key**: Verify the API key is correct and active
- **Check Network**: Ensure the server can reach the ChatOps API URL
- **Check Logs**: View agent logs for error messages
  ```bash
  sudo journalctl -u chatops-agent -f
  ```

### No Metrics Appearing

- **Wait a few seconds**: Metrics are sent every 5 seconds
- **Check Agent Status**: Verify the agent is running
- **Check Server Status**: Ensure the server shows as ONLINE

### API Key Issues

- **Invalid Key**: Generate a new API key if the current one is invalid
- **Inactive Key**: Check that the API key is active in the dashboard

## Next Steps

- [Detailed Installation Guide](installation.md)
- [Agent Configuration](../agent/configuration.md)
- [Using the Dashboard](../frontend/index.md)

