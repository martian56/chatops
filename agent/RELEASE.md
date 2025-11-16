# Creating Releases for ChatOps Agent

## Manual Build (Local)

### Prerequisites
- Go 1.24+ installed
- Linux environment (or use Docker/WSL on Windows/Mac)
- For .deb packages: `dpkg-dev` and `fakeroot` (install with `sudo apt-get install dpkg-dev fakeroot`)

### Build Binary Archive

```bash
# Make build script executable
chmod +x build.sh

# Build for AMD64 (default)
./build.sh 1.0.0 amd64

# Build for ARM64
./build.sh 1.0.0 arm64
```

The build script will create:
- `dist/chatops-agent-linux-amd64` - Binary for AMD64
- `dist/chatops-agent-linux-amd64-1.0.0.tar.gz` - Archive with binary and docs

### Build .deb Package

```bash
# Make build script executable
chmod +x scripts/build-deb.sh

# Build .deb for AMD64
./scripts/build-deb.sh 1.0.0 amd64

# Build .deb for ARM64
./scripts/build-deb.sh 1.0.0 arm64
```

The .deb build script will create:
- `dist/chatops-agent_1.0.0_amd64.deb` - Debian package
- `dist/chatops-agent_1.0.0_amd64.deb.sha256` - Checksum file

### Manual Build Commands

If you prefer to build manually:

```bash
# AMD64
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o chatops-agent-linux-amd64 ./main.go

# ARM64
GOOS=linux GOARCH=arm64 CGO_ENABLED=0 go build -o chatops-agent-linux-arm64 ./main.go
```

## Automated Releases (GitHub Actions)

### Creating a Release

1. **Create a version tag:**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. **Or use GitHub UI:**
   - Go to Releases → Draft a new release
   - Create a new tag (e.g., `v1.0.0`)
   - The GitHub Actions workflow will automatically build and create the release

3. **Manual trigger (workflow_dispatch):**
   - Go to Actions → Release Agent → Run workflow
   - Enter version tag (e.g., `v1.0.0`)
   - The workflow will build and create a release

### What Gets Created

The GitHub Actions workflow automatically:
- Builds binaries for Linux AMD64 and ARM64
- Creates `.tar.gz` archives with the binary and documentation
- Creates `.deb` packages for Debian/Ubuntu systems
- Generates SHA256 checksums for all artifacts
- Creates a GitHub Release with all artifacts attached

### Release Artifacts

Each release includes:

**Debian Packages (.deb):**
- `chatops-agent_{version}_amd64.deb` - Debian package for AMD64
- `chatops-agent_{version}_arm64.deb` - Debian package for ARM64

**Binary Archives:**
- `chatops-agent-linux-amd64-{version}.tar.gz` - AMD64 binary + docs
- `chatops-agent-linux-arm64-{version}.tar.gz` - ARM64 binary + docs

**Checksums:**
- SHA256 checksums for all packages and archives

## Distribution

Users can download releases from:
- GitHub Releases page: `https://github.com/your-org/chatops/releases`
- Direct download links for automation

## Installation Instructions for Users

### Debian/Ubuntu (Recommended)

```bash
# Download .deb package
wget https://github.com/your-org/chatops/releases/download/v1.0.0/chatops-agent_1.0.0_amd64.deb

# Verify checksum (optional)
wget https://github.com/your-org/chatops/releases/download/v1.0.0/chatops-agent_1.0.0_amd64.deb.sha256
sha256sum -c chatops-agent_1.0.0_amd64.deb.sha256

# Install package
sudo dpkg -i chatops-agent_1.0.0_amd64.deb
sudo apt-get install -f  # Install dependencies if needed

# Configure and start (edit service file with your API key)
sudo systemctl edit chatops-agent.service
sudo systemctl start chatops-agent
```

### Binary Archive

```bash
# Download and extract
wget https://github.com/your-org/chatops/releases/download/v1.0.0/chatops-agent-linux-amd64-1.0.0.tar.gz
tar -xzf chatops-agent-linux-amd64-1.0.0.tar.gz

# Verify checksum (optional)
sha256sum -c chatops-agent-linux-amd64-1.0.0.tar.gz.sha256

# Run the agent
./chatops-agent-linux-amd64 -api-key YOUR_API_KEY
```

## Versioning

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.0.0)
- Use tags: `v1.0.0`, `v1.1.0`, `v2.0.0`, etc.

