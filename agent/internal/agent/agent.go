package agent

import (
	"context"
	"fmt"
	"log"
	"os/exec"
	"runtime"
	"time"

	"github.com/chatops/agent/internal/api"
	"github.com/chatops/agent/internal/config"
	"github.com/chatops/agent/internal/metrics"
)

// Agent represents the ChatOps agent
type Agent struct {
	config  *config.Config
	api     *api.Client
	ws      *api.WSClient
	metrics *metrics.Collector
	docker  *metrics.DockerClient
}

// New creates a new agent instance
func New(cfg *config.Config) (*Agent, error) {
	// Create WebSocket client (will fetch server ID automatically)
	wsClient, err := api.NewWSClient(cfg.APIURL, cfg.APIKey)
	if err != nil {
		return nil, err
	}

	// Update config with the server ID from API
	cfg.ServerID = wsClient.GetServerID()

	// Create HTTP client for initial connection test
	apiClient, err := api.NewClient(cfg.APIURL, cfg.APIKey)
	if err != nil {
		return nil, err
	}

	// Create metrics collector
	metricsCollector := metrics.NewCollector()

	// Get Docker client from collector if available
	var dockerClient *metrics.DockerClient
	if metricsCollector != nil {
		// Access the docker client from the collector
		// We'll need to expose it or create a separate instance
		dockerClient, _ = metrics.NewDockerClient()
	}

	return &Agent{
		config:  cfg,
		api:     apiClient,
		ws:      wsClient,
		metrics: metricsCollector,
		docker:  dockerClient,
	}, nil
}

// Run starts the agent and runs until context is cancelled
func (a *Agent) Run(ctx context.Context) error {
	// Connect WebSocket
	if err := a.ws.Connect(ctx); err != nil {
		return fmt.Errorf("failed to connect WebSocket: %w", err)
	}
	defer a.ws.Close()

	log.Println("Successfully connected to API via WebSocket")

	// Start message handler goroutine
	go a.handleMessages(ctx)

	// Start metrics collection loop
	ticker := time.NewTicker(a.config.PollInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			log.Println("Agent context cancelled, stopping...")
			return nil
		case <-ticker.C:
			if err := a.collectAndSendMetrics(ctx); err != nil {
				log.Printf("Error collecting/sending metrics: %v", err)
				// Try to reconnect on error
				log.Println("Attempting to reconnect...")
				// Close old connection if exists
				a.ws.Close()
				// Recreate WS client
				wsClient, err := api.NewWSClient(a.config.APIURL, a.config.APIKey)
				if err != nil {
					log.Printf("Failed to create new WS client: %v", err)
					continue
				}
				a.ws = wsClient
				if err := a.ws.Connect(ctx); err != nil {
					log.Printf("Reconnection failed: %v", err)
				} else {
					log.Println("Reconnected successfully")
					// Restart message handler
					go a.handleMessages(ctx)
				}
			}
		}
	}
}

// handleMessages processes incoming WebSocket messages
func (a *Agent) handleMessages(ctx context.Context) {
	messageChan := a.ws.GetMessageChan()
	if messageChan == nil {
		return
	}

	for {
		select {
		case <-ctx.Done():
			return
		case message, ok := <-messageChan:
			if !ok {
				log.Printf("Message channel closed")
				return
			}

			msgType := message["type"]
			switch msgType {
			case "get_container_logs":
				a.handleGetContainerLogs(ctx, message)
			case "start_container":
				a.handleStartContainer(ctx, message)
			case "stop_container":
				a.handleStopContainer(ctx, message)
			case "restart_container":
				a.handleRestartContainer(ctx, message)
			case "execute_command":
				a.handleExecuteCommand(ctx, message)
			case "pong":
				// Heartbeat response - ignore
			case "metrics_received":
				// Metrics acknowledgment - handled by SendMetrics via channel
			default:
				log.Printf("Unknown message type: %v", msgType)
			}
		}
	}
}

// handleStartContainer handles container start requests
func (a *Agent) handleStartContainer(ctx context.Context, message map[string]interface{}) {
	if a.docker == nil {
		a.ws.SendResponse(message, map[string]interface{}{
			"type":    "error",
			"message": "Docker not available",
		})
		return
	}

	containerID, ok := message["container_id"].(string)
	if !ok {
		a.ws.SendResponse(message, map[string]interface{}{
			"type":    "error",
			"message": "Invalid container_id",
		})
		return
	}

	err := a.docker.StartContainer(ctx, containerID)
	if err != nil {
		a.ws.SendResponse(message, map[string]interface{}{
			"type":    "error",
			"message": fmt.Sprintf("Failed to start container: %v", err),
		})
		return
	}

	a.ws.SendResponse(message, map[string]interface{}{
		"type": "container_started",
		"data": map[string]interface{}{
			"container_id": containerID,
			"status":       "started",
		},
	})
}

// handleStopContainer handles container stop requests
func (a *Agent) handleStopContainer(ctx context.Context, message map[string]interface{}) {
	if a.docker == nil {
		a.ws.SendResponse(message, map[string]interface{}{
			"type":    "error",
			"message": "Docker not available",
		})
		return
	}

	containerID, ok := message["container_id"].(string)
	if !ok {
		a.ws.SendResponse(message, map[string]interface{}{
			"type":    "error",
			"message": "Invalid container_id",
		})
		return
	}

	var timeout *int
	if t, ok := message["timeout"].(float64); ok {
		timeoutInt := int(t)
		timeout = &timeoutInt
	}

	err := a.docker.StopContainer(ctx, containerID, timeout)
	if err != nil {
		a.ws.SendResponse(message, map[string]interface{}{
			"type":    "error",
			"message": fmt.Sprintf("Failed to stop container: %v", err),
		})
		return
	}

	a.ws.SendResponse(message, map[string]interface{}{
		"type": "container_stopped",
		"data": map[string]interface{}{
			"container_id": containerID,
			"status":       "stopped",
		},
	})
}

// handleRestartContainer handles container restart requests
func (a *Agent) handleRestartContainer(ctx context.Context, message map[string]interface{}) {
	if a.docker == nil {
		a.ws.SendResponse(message, map[string]interface{}{
			"type":    "error",
			"message": "Docker not available",
		})
		return
	}

	containerID, ok := message["container_id"].(string)
	if !ok {
		a.ws.SendResponse(message, map[string]interface{}{
			"type":    "error",
			"message": "Invalid container_id",
		})
		return
	}

	var timeout *int
	if t, ok := message["timeout"].(float64); ok {
		timeoutInt := int(t)
		timeout = &timeoutInt
	}

	err := a.docker.RestartContainer(ctx, containerID, timeout)
	if err != nil {
		a.ws.SendResponse(message, map[string]interface{}{
			"type":    "error",
			"message": fmt.Sprintf("Failed to restart container: %v", err),
		})
		return
	}

	a.ws.SendResponse(message, map[string]interface{}{
		"type": "container_restarted",
		"data": map[string]interface{}{
			"container_id": containerID,
			"status":       "restarted",
		},
	})
}

// handleGetContainerLogs handles container logs requests
func (a *Agent) handleGetContainerLogs(ctx context.Context, message map[string]interface{}) {
	if a.docker == nil {
		a.ws.SendResponse(message, map[string]interface{}{
			"type":    "error",
			"message": "Docker not available",
		})
		return
	}

	containerID, ok := message["container_id"].(string)
	if !ok {
		a.ws.SendResponse(message, map[string]interface{}{
			"type":    "error",
			"message": "Invalid container_id",
		})
		return
	}

	tail := 500
	if t, ok := message["tail"].(float64); ok {
		tail = int(t)
	}

	logs, err := a.docker.GetContainerLogs(ctx, containerID, tail)
	if err != nil {
		a.ws.SendResponse(message, map[string]interface{}{
			"type":    "error",
			"message": err.Error(),
		})
		return
	}

	a.ws.SendResponse(message, map[string]interface{}{
		"type": "container_logs",
		"data": map[string]interface{}{
			"container_id": containerID,
			"logs":         logs,
		},
	})
}

// handleExecuteCommand handles command execution requests
func (a *Agent) handleExecuteCommand(ctx context.Context, message map[string]interface{}) {
	cmdStr, ok := message["command"].(string)
	if !ok {
		a.ws.SendResponse(message, map[string]interface{}{
			"type":    "error",
			"message": "Invalid command",
		})
		return
	}

	// Execute command based on OS
	var cmd *exec.Cmd
	if runtime.GOOS == "windows" {
		// On Windows, use cmd.exe
		cmd = exec.CommandContext(ctx, "cmd.exe", "/C", cmdStr)
	} else {
		// On Linux/Unix, use sh
		cmd = exec.CommandContext(ctx, "sh", "-c", cmdStr)
	}

	// Execute and capture output
	output, err := cmd.CombinedOutput()
	exitCode := 0
	if err != nil {
		if exitError, ok := err.(*exec.ExitError); ok {
			exitCode = exitError.ExitCode()
		} else {
			exitCode = 1
		}
	}

	a.ws.SendResponse(message, map[string]interface{}{
		"type": "command_result",
		"data": map[string]interface{}{
			"output":    string(output),
			"exit_code": exitCode,
		},
	})
}

// collectAndSendMetrics collects system metrics and sends them to the API
func (a *Agent) collectAndSendMetrics(ctx context.Context) error {
	if !a.config.MetricsEnabled {
		return nil
	}

	// Collect metrics
	m, err := a.metrics.Collect()
	if err != nil {
		return err
	}

	// Set server ID
	m.ServerID = a.config.ServerID

	// Send to API via WebSocket
	if err := a.ws.SendMetrics(ctx, m); err != nil {
		return err
	}

	log.Printf("Metrics sent successfully")
	return nil
}
