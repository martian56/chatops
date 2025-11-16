#!/bin/bash

# Build script for ChatOps Agent (Linux)
# Usage: ./build.sh [version] [arch]
# Example: ./build.sh 1.0.0 amd64

set -e

VERSION=${1:-"dev"}
ARCH=${2:-"amd64"}
BINARY_NAME="chatops-agent"
OUTPUT_DIR="dist"

echo "Building ChatOps Agent..."
echo "Version: $VERSION"
echo "Architecture: $ARCH"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Build for Linux
GOOS=linux GOARCH=$ARCH go build \
  -ldflags "-X main.version=$VERSION" \
  -o "$OUTPUT_DIR/${BINARY_NAME}-linux-${ARCH}" \
  ./main.go

echo "Build complete: $OUTPUT_DIR/${BINARY_NAME}-linux-${ARCH}"

# Create a tar.gz archive
cd "$OUTPUT_DIR"
tar -czf "${BINARY_NAME}-linux-${ARCH}-${VERSION}.tar.gz" \
  "${BINARY_NAME}-linux-${ARCH}" \
  ../README.md \
  ../INSTALLATION.md

cd ..

echo "Archive created: $OUTPUT_DIR/${BINARY_NAME}-linux-${ARCH}-${VERSION}.tar.gz"

