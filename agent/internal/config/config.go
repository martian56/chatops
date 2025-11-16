package config

import (
	"fmt"
	"os"
	"time"
)

// Config holds the agent configuration
type Config struct {
	APIURL         string
	APIKey         string
	ServerID       string // Will be fetched from API after authentication
	PollInterval   time.Duration
	MetricsEnabled bool
	DockerEnabled  bool
}

// Load loads configuration from environment variables and command line flags
// Command line flags take precedence over environment variables
func Load(configPath, apiURL, apiKey, serverID string) (*Config, error) {
	cfg := &Config{
		APIURL:         getEnvOrFlag("CHATOPS_API_URL", apiURL),
		APIKey:         getEnvOrFlag("CHATOPS_API_KEY", apiKey),
		ServerID:       serverID, // Optional - will be fetched from API
		PollInterval:   5 * time.Second, // Default 5 seconds
		MetricsEnabled: true,
		DockerEnabled:  true,
	}

	// Load from config file if provided
	if configPath != "" {
		// TODO: Implement config file loading (YAML/JSON)
	}

	// Override with environment variables if not set via flags
	if cfg.APIURL == "" {
		cfg.APIURL = os.Getenv("CHATOPS_API_URL")
		if cfg.APIURL == "" {
			cfg.APIURL = "http://localhost:8000"
		}
	}

	if cfg.APIKey == "" {
		cfg.APIKey = os.Getenv("CHATOPS_API_KEY")
	}

	// ServerID is optional - will be fetched from API
	if cfg.ServerID == "" {
		cfg.ServerID = os.Getenv("CHATOPS_SERVER_ID")
	}

	// Validate
	if err := cfg.Validate(); err != nil {
		return nil, err
	}

	return cfg, nil
}

// Validate validates the configuration
func (c *Config) Validate() error {
	if c.APIKey == "" {
		return fmt.Errorf("API key is required")
	}
	if c.APIURL == "" {
		return fmt.Errorf("API URL is required")
	}
	// ServerID is optional - will be fetched from API
	return nil
}

func getEnvOrFlag(envVar, flagValue string) string {
	if flagValue != "" {
		return flagValue
	}
	return os.Getenv(envVar)
}

