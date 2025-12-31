#!/bin/bash
set -e

echo "===> Updating system..."
sudo apt update -y

echo "===> Installing pip (if missing)..."
sudo apt install -y python3-pip

echo "===> Installing unzip + curl (if missing)..."
sudo apt install -y unzip curl

echo "===> Installing Python requirements..."
pip3 install -r requirements.txt
echo "✔ Python dependencies installed"


# ==========================
# SSL CERTIFICATE
# ==========================

echo "===> Checking SSL certificate..."
if [[ -f cert.pem && -f key.pem ]]; then
  echo "✔ cert.pem + key.pem already exist — skipping"
else
  echo "===> Generating SSL certificate..."
  openssl req -newkey rsa:2048 -nodes \
    -keyout key.pem \
    -x509 -days 365 \
    -out cert.pem \
    -subj "/C=IL/ST=None/L=None/O=Server/CN=localhost"

  chmod 600 key.pem
  echo "✔ cert.pem + key.pem created"
fi


# ==========================
# AWS CLI
# ==========================

echo "===> Checking AWS CLI..."
if command -v aws >/dev/null 2>&1; then
  echo "✔ AWS CLI already installed"
  aws --version
else
  echo "===> Installing AWS CLI v2..."
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
  unzip -o awscliv2.zip
  sudo ./aws/install
  echo "✔ AWS CLI installed"
  aws --version
fi


echo "🎉 Setup completed successfully"
