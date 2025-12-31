#!/bin/bash
set -e

echo "===> Generating SSL certificate..."
openssl req -newkey rsa:2048 -nodes \
  -keyout key.pem \
  -x509 -days 365 \
  -out cert.pem \
  -subj "/C=IL/ST=None/L=None/O=Server/CN=localhost"

chmod 600 key.pem
echo "✔ cert.pem + key.pem created"

echo "===> Installing unzip (if missing)..."
sudo apt update -y
sudo apt install -y unzip curl

echo "===> Installing AWS CLI v2..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -o awscliv2.zip
sudo ./aws/install

echo "===> AWS CLI version:"
aws --version

echo "🎉 Setup completed successfully"
