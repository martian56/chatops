package main

import (
	"context"
	"flag"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/chatops/agent/internal/agent"
	"github.com/chatops/agent/internal/config"
)

func main() {
	// Parse command line flags
	apiURL := flag.String("api-url", "http://localhost:8000", "API server URL")
	apiKey := flag.String("api-key", "", "API key for authentication")
	configPath := flag.String("config", "", "Path to config file (optional)")
	flag.Parse()

	// Load configuration
	cfg, err := config.Load(*configPath, *apiURL, *apiKey, "")
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	// Validate required configuration
	if cfg.APIKey == "" {
		log.Fatal("API key is required. Set via -api-key flag or CHATOPS_API_KEY environment variable")
	}

	// Create agent
	a, err := agent.New(cfg)
	if err != nil {
		log.Fatalf("Failed to create agent: %v", err)
	}

	// Create context for graceful shutdown
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Handle shutdown signals
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)

	// Start agent in goroutine
	errChan := make(chan error, 1)
	go func() {
		log.Printf("Starting ChatOps agent for server %s", cfg.ServerID)
		if err := a.Run(ctx); err != nil {
			errChan <- err
		}
	}()

	// Wait for shutdown signal or error
	select {
	case sig := <-sigChan:
		log.Printf("Received signal: %v. Shutting down...", sig)
		cancel()
		// Give agent time to shutdown gracefully
		time.Sleep(2 * time.Second)
	case err := <-errChan:
		log.Fatalf("Agent error: %v", err)
	}

	log.Println("Agent stopped")
}
