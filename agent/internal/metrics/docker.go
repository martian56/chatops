package metrics

import (
	"context"
	"fmt"
	"io"
	"strings"
	"time"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/client"
	"github.com/chatops/agent/internal/api"
)

// DockerClient wraps Docker API client
type DockerClient struct {
	cli *client.Client
}

// NewDockerClient creates a new Docker client (works on both Windows and Linux)
func NewDockerClient() (*DockerClient, error) {
	// Docker client automatically detects the platform and uses the appropriate socket
	// On Linux: /var/run/docker.sock
	// On Windows: \\.\pipe\docker_engine
	cli, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
	if err != nil {
		return nil, err
	}

	// Test connection
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	_, err = cli.Ping(ctx)
	if err != nil {
		return nil, fmt.Errorf("Docker not available: %w", err)
	}

	return &DockerClient{cli: cli}, nil
}

// GetContainers retrieves all Docker containers
func (d *DockerClient) GetContainers(ctx context.Context) ([]api.DockerContainer, error) {
	containers, err := d.cli.ContainerList(ctx, types.ContainerListOptions{All: true})
	if err != nil {
		return nil, fmt.Errorf("failed to list containers: %w", err)
	}

	result := make([]api.DockerContainer, 0, len(containers))
	for _, c := range containers {
		// Get container name (remove leading /)
		var name string
		if len(c.Names) > 0 {
			name = c.Names[0]
			if len(name) > 0 && name[0] == '/' {
				name = name[1:]
			}
		} else {
			name = c.ID[:12] // Fallback to short ID if no name
		}

		// Format status
		status := c.Status
		state := c.State

		// Parse ports
		ports := make([]api.Port, 0, len(c.Ports))
		for _, p := range c.Ports {
			port := api.Port{
				PrivatePort: int(p.PrivatePort),
				Type:        p.Type,
			}
			if p.PublicPort > 0 {
				publicPort := int(p.PublicPort)
				port.PublicPort = &publicPort
			}
			ports = append(ports, port)
		}

		// Format created time
		created := time.Unix(c.Created, 0).Format(time.RFC3339)

		result = append(result, api.DockerContainer{
			ID:      c.ID[:12], // Short ID
			Name:    name,
			Image:   c.Image,
			Status:  status,
			State:   state,
			Created: created,
			Ports:   ports,
		})
	}

	return result, nil
}

// GetContainerLogs retrieves logs for a specific container
func (d *DockerClient) GetContainerLogs(ctx context.Context, containerID string, tail int) ([]string, error) {
	options := types.ContainerLogsOptions{
		ShowStdout: true,
		ShowStderr: true,
		Tail:       fmt.Sprintf("%d", tail),
		Follow:     false,
	}

	reader, err := d.cli.ContainerLogs(ctx, containerID, options)
	if err != nil {
		return nil, fmt.Errorf("failed to get container logs: %w", err)
	}
	defer reader.Close()

	// Read logs
	logBytes, err := io.ReadAll(reader)
	if err != nil {
		return nil, fmt.Errorf("failed to read logs: %w", err)
	}

	// Docker logs come with 8-byte headers per line
	// Format: [STREAM_TYPE (1 byte)][padding (3 bytes)][SIZE (4 bytes)][DATA]
	// We need to parse this properly
	var logs []string
	offset := 0
	for offset < len(logBytes) {
		if offset+8 > len(logBytes) {
			break
		}
		
		// Read header (8 bytes)
		// First byte is stream type (0x01 = stdout, 0x02 = stderr)
		// Next 3 bytes are padding
		// Next 4 bytes are size (big-endian)
		size := int(logBytes[offset+4])<<24 | int(logBytes[offset+5])<<16 | int(logBytes[offset+6])<<8 | int(logBytes[offset+7])
		
		offset += 8
		
		if offset+size > len(logBytes) {
			break
		}
		
		// Read the actual log line
		logLine := string(logBytes[offset : offset+size])
		// Remove trailing newline if present
		logLine = strings.TrimSuffix(logLine, "\n")
		if len(logLine) > 0 {
			logs = append(logs, logLine)
		}
		
		offset += size
	}

	return logs, nil
}

// StartContainer starts a Docker container
func (d *DockerClient) StartContainer(ctx context.Context, containerID string) error {
	return d.cli.ContainerStart(ctx, containerID, types.ContainerStartOptions{})
}

// StopContainer stops a Docker container
func (d *DockerClient) StopContainer(ctx context.Context, containerID string, timeoutSeconds *int) error {
	timeout := 10 // Default timeout: 10 seconds
	if timeoutSeconds != nil {
		timeout = *timeoutSeconds
	}
	// ContainerStop takes a timeout duration
	timeoutDuration := time.Duration(timeout) * time.Second
	return d.cli.ContainerStop(ctx, containerID, &timeoutDuration)
}

// RestartContainer restarts a Docker container
func (d *DockerClient) RestartContainer(ctx context.Context, containerID string, timeoutSeconds *int) error {
	timeout := 10 // Default timeout: 10 seconds
	if timeoutSeconds != nil {
		timeout = *timeoutSeconds
	}
	// ContainerRestart takes a timeout duration
	timeoutDuration := time.Duration(timeout) * time.Second
	return d.cli.ContainerRestart(ctx, containerID, &timeoutDuration)
}

// Close closes the Docker client
func (d *DockerClient) Close() error {
	return d.cli.Close()
}

