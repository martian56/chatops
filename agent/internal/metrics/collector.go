package metrics

import (
	"context"
	"log"
	"runtime"
	"sort"
	"time"

	"github.com/chatops/agent/internal/api"
	"github.com/shirou/gopsutil/v3/cpu"
	"github.com/shirou/gopsutil/v3/disk"
	"github.com/shirou/gopsutil/v3/mem"
	"github.com/shirou/gopsutil/v3/net"
	"github.com/shirou/gopsutil/v3/process"
)

// Collector collects system metrics
type Collector struct {
	dockerClient *DockerClient
}

// NewCollector creates a new metrics collector
func NewCollector() *Collector {
	// Try to initialize Docker client (may fail if Docker is not available)
	dockerClient, err := NewDockerClient()
	if err != nil {
		log.Printf("Docker client not available: %v (containers will not be collected)", err)
	} else {
		log.Println("Docker client initialized successfully")
	}
	return &Collector{
		dockerClient: dockerClient,
	}
}

// Collect collects current system metrics
func (c *Collector) Collect() (*api.Metrics, error) {
	now := time.Now()

	// Collect CPU metrics
	cpuPercent, err := cpu.Percent(0, false)
	if err != nil {
		return nil, err
	}
	cpuInfo, err := cpu.Info()
	if err != nil {
		return nil, err
	}

	var cpuUsage float64
	if len(cpuPercent) > 0 {
		cpuUsage = cpuPercent[0]
	}

	var cores int
	var freqMHz float64
	if len(cpuInfo) > 0 {
		cores = int(cpuInfo[0].Cores)
		freqMHz = cpuInfo[0].Mhz
	}

	// Collect memory metrics
	memStat, err := mem.VirtualMemory()
	if err != nil {
		return nil, err
	}

	// Collect disk metrics (cross-platform)
	var diskStat *disk.UsageStat
	if runtime.GOOS == "windows" {
		// On Windows, use C: drive
		diskStat, err = disk.Usage("C:")
	} else {
		// On Linux/Unix, use root
		diskStat, err = disk.Usage("/")
	}
	if err != nil {
		return nil, err
	}

	// Collect network metrics
	netStats, err := net.IOCounters(false)
	if err != nil {
		return nil, err
	}

	var bytesSent, bytesRecv, packetsSent, packetsRecv uint64
	if len(netStats) > 0 {
		bytesSent = netStats[0].BytesSent
		bytesRecv = netStats[0].BytesRecv
		packetsSent = netStats[0].PacketsSent
		packetsRecv = netStats[0].PacketsRecv
	}

	// Collect Docker containers (if Docker is available)
	var containers []api.DockerContainer
	if c.dockerClient != nil {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		dockerContainers, err := c.dockerClient.GetContainers(ctx)
		if err == nil {
			containers = dockerContainers
			log.Printf("Collected %d Docker containers", len(containers))
		} else {
			log.Printf("Failed to collect Docker containers: %v", err)
		}
		// If Docker is not available, containers will be empty (not an error)
	}

	// Collect all processes (sorted by CPU usage)
	processes, err := c.collectProcesses(10000) // Large limit to get all processes
	if err != nil {
		// If process collection fails, continue without processes
		processes = []api.Process{}
	}

	return &api.Metrics{
		Timestamp: now,
		CPU: api.CPUInfo{
			UsagePercent: cpuUsage,
			Cores:        cores,
			FrequencyMHz: freqMHz,
		},
		Memory: api.MemoryInfo{
			TotalGB:      float64(memStat.Total) / (1024 * 1024 * 1024),
			UsedGB:       float64(memStat.Used) / (1024 * 1024 * 1024),
			AvailableGB:  float64(memStat.Available) / (1024 * 1024 * 1024),
			UsagePercent: memStat.UsedPercent,
		},
		Disk: api.DiskInfo{
			TotalGB:      float64(diskStat.Total) / (1024 * 1024 * 1024),
			UsedGB:       float64(diskStat.Used) / (1024 * 1024 * 1024),
			AvailableGB:  float64(diskStat.Free) / (1024 * 1024 * 1024),
			UsagePercent: diskStat.UsedPercent,
		},
		Network: api.NetworkInfo{
			BytesSent:   bytesSent,
			BytesRecv:   bytesRecv,
			PacketsSent: packetsSent,
			PacketsRecv: packetsRecv,
		},
		Containers: containers,
		Processes:  processes,
	}, nil
}

// collectProcesses collects top N processes by CPU usage
func (c *Collector) collectProcesses(limit int) ([]api.Process, error) {
	// Get all processes
	pids, err := process.Pids()
	if err != nil {
		return nil, err
	}

	type processWithCPU struct {
		proc *process.Process
		cpu  float64
	}

	processesWithCPU := make([]processWithCPU, 0)

	// Collect CPU usage for each process
	for _, pid := range pids {
		proc, err := process.NewProcess(pid)
		if err != nil {
			continue // Skip if process no longer exists
		}

		// Get CPU percent (non-blocking, uses cached value)
		cpuPercent, err := proc.CPUPercent()
		if err != nil {
			continue
		}

		processesWithCPU = append(processesWithCPU, processWithCPU{
			proc: proc,
			cpu:  cpuPercent,
		})
	}

	// Sort by CPU usage (descending)
	sort.Slice(processesWithCPU, func(i, j int) bool {
		return processesWithCPU[i].cpu > processesWithCPU[j].cpu
	})

	// Take top N
	if len(processesWithCPU) > limit {
		processesWithCPU = processesWithCPU[:limit]
	}

	// Convert to API format
	result := make([]api.Process, 0, len(processesWithCPU))
	for _, pwc := range processesWithCPU {
		proc := pwc.proc

		// Get process name
		name, err := proc.Name()
		if err != nil {
			name = "unknown"
		}

		// Get memory info (in MB)
		memInfo, err := proc.MemoryInfo()
		var memoryMB float64
		if err == nil && memInfo != nil {
			memoryMB = float64(memInfo.RSS) / (1024 * 1024) // Convert bytes to MB
		}

		// Get status (returns array of status strings, take first one)
		statusSlice, err := proc.Status()
		var statusStr string
		if err != nil || len(statusSlice) == 0 {
			statusStr = "unknown"
		} else {
			statusStr = statusSlice[0]
			// On Windows, status might be longer, take first char if it's a single char status
			if len(statusStr) > 1 && (statusStr[0] == 'R' || statusStr[0] == 'S' || statusStr[0] == 'Z' || statusStr[0] == 'T' || statusStr[0] == 'D') {
				statusStr = string(statusStr[0])
			}
		}

		// Get username (cross-platform)
		username, err := proc.Username()
		if err != nil {
			username = "unknown"
		}

		// Get PID
		pid := int(proc.Pid)

		result = append(result, api.Process{
			PID:    pid,
			Name:   name,
			CPU:    pwc.cpu,
			Memory: memoryMB,
			Status: statusStr,
			User:   username,
		})
	}

	return result, nil
}

