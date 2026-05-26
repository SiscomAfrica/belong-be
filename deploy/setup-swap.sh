#!/usr/bin/env bash
# Setup 2GB swap for EC2 t2.small (2GB RAM)
# Run as root: sudo bash deploy/setup-swap.sh
set -euo pipefail

SWAP_SIZE="2G"
SWAP_FILE="/swapfile"

if swapon --show | grep -q "$SWAP_FILE"; then
    echo "Swap already active at $SWAP_FILE"
    swapon --show
    exit 0
fi

echo "Creating ${SWAP_SIZE} swap file..."
fallocate -l "$SWAP_SIZE" "$SWAP_FILE"
chmod 600 "$SWAP_FILE"
mkswap "$SWAP_FILE"
swapon "$SWAP_FILE"

# Persist across reboots
if ! grep -q "$SWAP_FILE" /etc/fstab; then
    echo "$SWAP_FILE none swap sw 0 0" >> /etc/fstab
fi

# Optimize for low-memory server
sysctl vm.swappiness=10
sysctl vm.vfs_cache_pressure=50
echo "vm.swappiness=10" >> /etc/sysctl.conf
echo "vm.vfs_cache_pressure=50" >> /etc/sysctl.conf

echo "Swap configured:"
free -h
