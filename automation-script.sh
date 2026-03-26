#!/bin/bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 /path/to/app-directory"
    exit 1
fi

APP_DIR="$1"

if [[ ! -d "$APP_DIR" ]]; then
    echo "Error: directory does not exist: $APP_DIR"
    exit 1
fi

if [[ ! -f "$APP_DIR/Dockerfile" ]]; then
    echo "Error: no Dockerfile found in: $APP_DIR"
    exit 1
fi

BASE_NAME="$(basename "$APP_DIR")"
BASE_NAME="${BASE_NAME,,}"           # lowercase
BASE_NAME="${BASE_NAME//_/-}"        # replace underscores with dashes
BASE_NAME="${BASE_NAME// /-}"        # replace spaces (just in case)

CONTAINER_NAME="${BASE_NAME}-container"
IMAGE_NAME="${BASE_NAME}-image"

echo "App directory: $APP_DIR"
echo "Image name: $IMAGE_NAME"
echo "Container name: $CONTAINER_NAME"

sudo yum install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user
echo "If you want to run 'docker' without sudo in new terminals, log out and back in. This script will continue using sudo."

cd "$APP_DIR"

if sudo docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Removing existing container: $CONTAINER_NAME"
    sudo docker rm -f "$CONTAINER_NAME"
fi

echo "Building Docker image..."
sudo docker build --no-cache -t "$IMAGE_NAME" .

echo "Starting container..."
sudo docker run -d \
    --name "$CONTAINER_NAME" \
    -p 80:5000 \
    --restart unless-stopped \
    "$IMAGE_NAME"

if sudo docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Container started successfully."
else
    echo "Container failed to start."
    echo "Check logs with: sudo docker logs $CONTAINER_NAME"
    exit 1
fi

TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" || true)

if [[ -n "$TOKEN" ]]; then
    PUBLIC_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
      http://169.254.169.254/latest/meta-data/public-ipv4 || echo "Unavailable")
else
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "Unavailable")
fi

if [[ "$PUBLIC_IP" != "Unavailable" ]]; then
    echo "Access your app at: http://$PUBLIC_IP"
else
    echo "Could not retrieve public IP (maybe no public IP assigned)."
fi

echo "Check status with: sudo docker ps"
echo "Check logs with: sudo docker logs $CONTAINER_NAME"