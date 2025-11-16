package api

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// Client handles communication with the ChatOps API
type Client struct {
	baseURL  string
	apiKey   string
	serverID string
	client   *http.Client
}

// APIKeyInfo represents API key information from the server
type APIKeyInfo struct {
	ServerID string `json:"server_id"`
	KeyID    string `json:"key_id"`
	Name     string `json:"name"`
	IsActive bool   `json:"is_active"`
}

// NewClient creates a new API client
func NewClient(baseURL, apiKey string) (*Client, error) {
	client := &Client{
		baseURL: baseURL,
		apiKey:  apiKey,
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
	}

	// Fetch server ID from API using the API key
	ctx := context.Background()
	serverID, err := client.fetchServerID(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch server ID: %w", err)
	}

	client.serverID = serverID
	return client, nil
}

// fetchServerID fetches the server ID associated with this API key
func (c *Client) fetchServerID(ctx context.Context) (string, error) {
	url := c.baseURL + "/api/v1/api-keys/me"

	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return "", err
	}

	req.Header.Set("X-API-Key", c.apiKey)

	resp, err := c.client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("API error: %d - %s", resp.StatusCode, string(bodyBytes))
	}

	var info APIKeyInfo
	if err := json.NewDecoder(resp.Body).Decode(&info); err != nil {
		return "", err
	}

	return info.ServerID, nil
}

// GetServerID returns the server ID associated with this client
func (c *Client) GetServerID() string {
	return c.serverID
}

// TestConnection tests the API connection
func (c *Client) TestConnection(ctx context.Context) error {
	req, err := http.NewRequestWithContext(ctx, "GET", c.baseURL+"/health", nil)
	if err != nil {
		return err
	}

	resp, err := c.client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to connect to API: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("API returned status %d", resp.StatusCode)
	}

	return nil
}

// SendMetrics sends metrics to the API
func (c *Client) SendMetrics(ctx context.Context, metrics *Metrics) error {
	// For now, we'll use a placeholder endpoint
	// This will be implemented when the metrics endpoint is ready
	url := fmt.Sprintf("%s/api/v1/metrics/%s", c.baseURL, c.serverID)

	body, err := json.Marshal(metrics)
	if err != nil {
		return err
	}

	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(body))
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-API-Key", c.apiKey)

	resp, err := c.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		bodyBytes, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("API error: %d - %s", resp.StatusCode, string(bodyBytes))
	}

	return nil
}

// Metrics represents system metrics
type Metrics struct {
	ServerID   string            `json:"server_id"`
	Timestamp  time.Time         `json:"timestamp"`
	CPU        CPUInfo           `json:"cpu"`
	Memory     MemoryInfo        `json:"memory"`
	Disk       DiskInfo          `json:"disk"`
	Network    NetworkInfo       `json:"network"`
	Containers []DockerContainer `json:"containers,omitempty"`
	Processes  []Process         `json:"processes,omitempty"`
}

type CPUInfo struct {
	UsagePercent float64 `json:"usage_percent"`
	Cores        int     `json:"cores"`
	FrequencyMHz float64 `json:"frequency_mhz"`
}

type MemoryInfo struct {
	TotalGB      float64 `json:"total_gb"`
	UsedGB       float64 `json:"used_gb"`
	AvailableGB  float64 `json:"available_gb"`
	UsagePercent float64 `json:"usage_percent"`
}

type DiskInfo struct {
	TotalGB      float64 `json:"total_gb"`
	UsedGB       float64 `json:"used_gb"`
	AvailableGB  float64 `json:"available_gb"`
	UsagePercent float64 `json:"usage_percent"`
}

type NetworkInfo struct {
	BytesSent   uint64 `json:"bytes_sent"`
	BytesRecv   uint64 `json:"bytes_recv"`
	PacketsSent uint64 `json:"packets_sent"`
	PacketsRecv uint64 `json:"packets_recv"`
}

type DockerContainer struct {
	ID      string `json:"id"`
	Name    string `json:"name"`
	Image   string `json:"image"`
	Status  string `json:"status"`
	State   string `json:"state"`
	Created string `json:"created"`
	Ports   []Port `json:"ports"`
}

type Port struct {
	PrivatePort int    `json:"private_port"`
	PublicPort  *int   `json:"public_port,omitempty"`
	Type        string `json:"type"`
}

type Process struct {
	PID    int     `json:"pid"`
	Name   string  `json:"name"`
	CPU    float64 `json:"cpu"`
	Memory float64 `json:"memory"`
	Status string  `json:"status"`
	User   string  `json:"user"`
}
