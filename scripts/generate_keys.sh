#!/bin/bash
# generate_keys.sh - Generate RSA key pair for JWT authentication
set -e

KEYS_DIR="apps/server/keys"

echo "🔑 Generating RSA key pair..."

mkdir -p "$KEYS_DIR"

# Generate private key
openssl genrsa -out "$KEYS_DIR/private.pem" 2048

# Generate public key from private key
openssl rsa -in "$KEYS_DIR/private.pem" -pubout -out "$KEYS_DIR/public.pem"

# Set permissions
chmod 600 "$KEYS_DIR/private.pem"
chmod 644 "$KEYS_DIR/public.pem"

echo "✅ Keys generated in $KEYS_DIR"
echo "   - private.pem (keep secret!)"
echo "   - public.pem"
