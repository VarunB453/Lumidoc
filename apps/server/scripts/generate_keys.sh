#!/usr/bin/env bash
# Generate RS256 keypair for JWT signing.
set -euo pipefail
KEY_DIR="${KEY_DIR:-./keys}"
mkdir -p "$KEY_DIR"
openssl genpkey -algorithm RSA -out "$KEY_DIR/private.pem" -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in "$KEY_DIR/private.pem" -out "$KEY_DIR/public.pem"
chmod 600 "$KEY_DIR/private.pem"
echo "JWT keys generated in $KEY_DIR/"
