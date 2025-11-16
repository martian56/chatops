#!/bin/bash

# Build .deb package for ChatOps Agent
# Usage: ./build-deb.sh [version] [arch]
# Example: ./build-deb.sh 1.0.0 amd64

set -e

VERSION=${1:-"1.0.0"}
ARCH=${2:-"amd64"}
BINARY_NAME="chatops-agent"
PACKAGE_NAME="chatops-agent"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PACKAGE_DIR="$AGENT_DIR/package/deb"
BUILD_DIR="$AGENT_DIR/build/deb"
OUTPUT_DIR="$AGENT_DIR/dist"

# Strip 'v' prefix from version if present (e.g., v1.0.0 -> 1.0.0)
DEB_VERSION="${VERSION#v}"

echo "Building .deb package for ChatOps Agent..."
echo "Version: $VERSION (deb: $DEB_VERSION)"
echo "Architecture: $ARCH"

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Build the binary
echo "Building binary..."
cd "$AGENT_DIR"
GOOS=linux GOARCH=$ARCH CGO_ENABLED=0 go build \
  -ldflags "-X main.version=$VERSION" \
  -o "$BUILD_DIR/$BINARY_NAME" \
  ./main.go

# Create package structure
DEB_ROOT="$BUILD_DIR/${PACKAGE_NAME}_${DEB_VERSION}_${ARCH}"
mkdir -p "$DEB_ROOT/DEBIAN"
mkdir -p "$DEB_ROOT/usr/bin"
mkdir -p "$DEB_ROOT/etc/chatops-agent"
mkdir -p "$DEB_ROOT/lib/systemd/system"
mkdir -p "$DEB_ROOT/usr/share/doc/${PACKAGE_NAME}"

# Copy binary
cp "$BUILD_DIR/$BINARY_NAME" "$DEB_ROOT/usr/bin/"

# Copy control file and update version/arch
sed "s/Version: .*/Version: ${DEB_VERSION}/" "$PACKAGE_DIR/control" | \
  sed "s/Architecture: .*/Architecture: ${ARCH}/" > "$DEB_ROOT/DEBIAN/control"

# Copy maintainer scripts
cp "$PACKAGE_DIR/postinst" "$DEB_ROOT/DEBIAN/"
cp "$PACKAGE_DIR/prerm" "$DEB_ROOT/DEBIAN/"
cp "$PACKAGE_DIR/postrm" "$DEB_ROOT/DEBIAN/"
chmod +x "$DEB_ROOT/DEBIAN/"*.sh 2>/dev/null || true
chmod +x "$DEB_ROOT/DEBIAN/postinst"
chmod +x "$DEB_ROOT/DEBIAN/prerm"
chmod +x "$DEB_ROOT/DEBIAN/postrm"

# Copy systemd service file
cp "$PACKAGE_DIR/chatops-agent.service" "$DEB_ROOT/lib/systemd/system/"

# Copy documentation
cp "$AGENT_DIR/README.md" "$DEB_ROOT/usr/share/doc/${PACKAGE_NAME}/"
cp "$AGENT_DIR/INSTALLATION.md" "$DEB_ROOT/usr/share/doc/${PACKAGE_NAME}/"
gzip -9 "$DEB_ROOT/usr/share/doc/${PACKAGE_NAME}/README.md" 2>/dev/null || true
gzip -9 "$DEB_ROOT/usr/share/doc/${PACKAGE_NAME}/INSTALLATION.md" 2>/dev/null || true

# Create changelog
cat > "$DEB_ROOT/usr/share/doc/${PACKAGE_NAME}/changelog.Debian" <<EOF
chatops-agent (${DEB_VERSION}) stable; urgency=medium

  * Initial release

 -- ChatOps Team <support@chatops.com>  $(date -R)
EOF
gzip -9 "$DEB_ROOT/usr/share/doc/${PACKAGE_NAME}/changelog.Debian"

# Build the .deb package
echo "Creating .deb package..."
mkdir -p "$OUTPUT_DIR"
if command -v fakeroot >/dev/null 2>&1; then
    fakeroot dpkg-deb --build "$DEB_ROOT" "$OUTPUT_DIR/${PACKAGE_NAME}_${DEB_VERSION}_${ARCH}.deb"
elif command -v dpkg-deb >/dev/null 2>&1; then
    dpkg-deb --build "$DEB_ROOT" "$OUTPUT_DIR/${PACKAGE_NAME}_${DEB_VERSION}_${ARCH}.deb"
else
    echo "Error: dpkg-deb or fakeroot not found. Install with: sudo apt-get install dpkg-dev fakeroot"
    exit 1
fi

echo "Package created: $OUTPUT_DIR/${PACKAGE_NAME}_${DEB_VERSION}_${ARCH}.deb"

# Create checksum
cd "$OUTPUT_DIR"
sha256sum "${PACKAGE_NAME}_${DEB_VERSION}_${ARCH}.deb" > "${PACKAGE_NAME}_${DEB_VERSION}_${ARCH}.deb.sha256"
cd ..

echo "Checksum created: $OUTPUT_DIR/${PACKAGE_NAME}_${DEB_VERSION}_${ARCH}.deb.sha256"

