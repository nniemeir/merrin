#!/bin/sh

if ! mkdir -p ~/.local/bin; then
    echo "Failed to create ~/.local/bin/"
    exit 1
fi

if ! cp merrin.py ~/.local/bin/merrin; then
    echo "Failed to copy executable to ~/.local/bin/"
    exit 1
fi

echo "Install successful."