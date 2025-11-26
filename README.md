# ChatOps

**Unified Server Monitoring & Management & Devops Platform**

Monitor and manage all your servers from a single, intuitive web dashboard. Real-time metrics, Docker container control, alerts, and terminal access—all in one place.

---

## 🎯 What is ChatOps?

ChatOps is a comprehensive server monitoring and management platform that lets you:

- **Monitor** your servers' CPU, memory, disk, and network in real-time
- **Control** Docker containers with one-click actions
- **Alert** on performance thresholds automatically
- **Execute** commands remotely via web terminal
- **Track** all system activity with complete audit logs

Deploy a lightweight agent on each server, and start monitoring immediately. No complex setup, no VPNs required—just secure API key authentication.

---

## 🚀 Getting Started

### Step 1: Add Your Server

1. Log into the ChatOps web interface
2. Navigate to **Servers** from the sidebar
3. Click **"Add Server"**
4. Enter a name for your server (e.g., "Production Web Server")
5. Click **"Create"**

### Step 2: Generate an API Key (keep as super secret)

1. Click on your newly created server
2. Go to the **"API Keys"** tab
3. Click **"Create API Key"**
4. Optionally give it a name (e.g., "Main Agent")
5. **Copy the API key immediately** - it's only shown once!

### Step 3: Install the Agent

Download and run the ChatOps agent on your server:

```bash
# Download the agent binary for your platform
# Then run:
./chatops-agent -api-key YOUR_API_KEY_HERE
```

Or using environment variables:

```bash
export CHATOPS_API_KEY="your-api-key-here"
export CHATOPS_API_URL="https://your-chatops-instance.com"  # Your ChatOps instance URL
./chatops-agent
```

**That's it!** The agent will automatically:
- Connect to your ChatOps instance
- Start sending metrics every 5 seconds
- Enable Docker container management
- Allow remote command execution

See [Agent Installation Guide](agent/INSTALLATION.md) for detailed installation instructions, including running as a system service.

---

## 📊 Using ChatOps

### View Real-Time Metrics

1. Navigate to **Servers** from the sidebar
2. Click on any server to view its details
3. The **Metrics** tab shows:
   - **CPU Usage**: Real-time CPU percentage with historical chart
   - **Memory Usage**: RAM usage and available memory
   - **Disk Usage**: Disk space by mount point
   - **Network**: Incoming and outgoing network traffic

All metrics update in real-time and are stored for historical analysis.

### Monitor Running Processes

1. Open a server's detail page
2. Go to the **Processes** tab
3. View all running processes sorted by CPU usage
4. Use the search bar to filter processes by name
5. See CPU and memory usage for each process

### Manage Docker Containers

1. Open a server's detail page
2. Go to the **Containers** tab
3. View all Docker containers with their status
4. **Start/Stop/Restart** containers with one click
5. Click on any container to:
   - View real-time logs
   - See container details and resource usage
   - Manage container lifecycle

### Set Up Alerts

1. Navigate to **Alerts & Thresholds** from the sidebar
2. Click **"Create Threshold"**
3. Select:
   - **Server** (or "All Servers" for global alerts)
   - **Metric Type** (CPU, Memory, Disk, Network)
   - **Condition** (Above/Below threshold)
   - **Threshold Value**
   - **Alert Name**
4. Click **"Create"**

When a threshold is exceeded, an alert will automatically appear in:
- The **Alerts & Thresholds** page
- The server's **Logs** tab
- Real-time notifications

### Execute Commands

1. Open a server's detail page
2. Go to the **Terminal** tab
3. Type your command in the terminal
4. Press Enter to execute
5. View real-time output
6. All commands are logged with:
   - Timestamp
   - Command executed
   - Output
   - Exit code
   - Duration

### View Logs & Activity

1. Open a server's detail page
2. Go to the **Logs** tab
3. See a unified view of:
   - **Application Logs**: System and application events
   - **Alerts**: All triggered alerts
   - **System Events**: Agent connections/disconnections
   - **Historical Logs**: Past log entries from the database

Logs are color-coded by level (INFO, WARNING, ERROR) and update in real-time.

### View Command History

1. Navigate to **Servers** from the sidebar
2. Click on any server
3. Go to the **Terminal** tab
4. Scroll up to see all previously executed commands
5. Each entry shows:
   - Command executed
   - Output
   - Exit code
   - Execution time

---

## 🔐 Security Features

- **Secure Authentication**: JWT-based authentication with refresh tokens
- **API Key Management**: Generate, view, and revoke API keys per server
- **Audit Trail**: Complete history of all user actions
- **Connection Tracking**: Monitor when agents connect and disconnect
- **Command Logging**: All terminal commands are logged with full output

---

## 🎨 Dashboard Overview

The ChatOps dashboard provides:

- **Servers List**: View all your servers at a glance with status indicators
- **Server Details**: Deep dive into each server's metrics, containers, processes, and logs
- **Alerts & Thresholds**: Manage alert configurations and view active alerts
- **Settings**: Update your profile and change your password

All data updates in real-time via WebSocket connections—no page refresh needed!

---

## 📱 Features at a Glance

| Feature | Location | Description |
|---------|----------|-------------|
| **Metrics** | Server → Metrics tab | Real-time CPU, memory, disk, network charts |
| **Processes** | Server → Processes tab | All running processes with search |
| **Containers** | Server → Containers tab | Docker container management |
| **Terminal** | Server → Terminal tab | Remote command execution |
| **Logs** | Server → Logs tab | Unified log viewer |
| **Alerts** | Alerts & Thresholds page | Configure and view alerts |
| **API Keys** | Server → API Keys tab | Manage agent authentication |

---

## 🎯 Use Cases

- **Server Monitoring**: Monitor multiple servers from a single dashboard
- **Container Management**: Control Docker containers without SSH access
- **Performance Tracking**: Track system performance over time
- **Incident Response**: Quickly identify and respond to system issues
- **Audit Compliance**: Maintain complete audit trails for compliance
- **Remote Management**: Manage servers without direct SSH access

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Support

For issues and questions, please open an issue on GitHub.
