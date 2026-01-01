#!/bin/bash
set -e

AWS_DIR="$HOME/.aws"
ROOT_AWS_DIR="/root/.aws"

ensure_credentials() {
  local target_user="$1"
  local target_home="$2"
  local target_dir="$target_home/.aws"

  echo "===> Checking AWS credentials for $target_user..."

  if sudo -u "$target_user" aws sts get-caller-identity >/dev/null 2>&1; then
    echo "✔ Credentials already configured for $target_user"
    return
  fi

  echo "⚠ No credentials found for $target_user — configuring..."

  mkdir -p "$target_dir"

  read -p "AWS Access Key ID: " AWS_ACCESS_KEY_ID
  read -s -p "AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY; echo
  read -p "Default AWS Region (e.g. us-east-1): " AWS_DEFAULT_REGION

  cat > "$target_dir/credentials" <<EOF
[default]
aws_access_key_id=$AWS_ACCESS_KEY_ID
aws_secret_access_key=$AWS_SECRET_ACCESS_KEY
EOF

  cat > "$target_dir/config" <<EOF
[default]
region=$AWS_DEFAULT_REGION
output=json
EOF

  chmod 600 "$target_dir"/credentials "$target_dir"/config

  echo "✔ Credentials saved for $target_user"
  sudo -u "$target_user" aws sts get-caller-identity
  echo "✔ Verified AWS identity for $target_user"
}

echo "===> Updating system..."
sudo apt update -y

echo "===> Installing pip..."
sudo apt install -y python3-pip

echo "===> Installing unzip + curl..."
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
# AWS CLI INSTALL
# ==========================

echo "===> Checking AWS CLI..."
if command -v aws >/dev/null 2>&1; then
  echo "✔ AWS CLI already installed"
  aws --version
else
  echo "===> Downloading AWS CLI v2..."
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

  echo "===> Unzipping installer..."
  unzip -o awscliv2.zip

  echo "===> Installing AWS CLI..."
  sudo ./aws/install

  echo "✔ AWS CLI installed"
  aws --version

  echo "===> Cleaning installer files..."
  rm -rf aws awscliv2.zip
fi


# ==========================
# AWS CREDENTIAL SETUP
# ==========================

ensure_credentials "$USER" "$HOME"

sudo mkdir -p "$ROOT_AWS_DIR"
sudo cp -r "$AWS_DIR/"* "$ROOT_AWS_DIR/" || true
sudo chmod 600 "$ROOT_AWS_DIR"/credentials "$ROOT_AWS_DIR"/config

echo "===> Verifying credentials for root..."
if sudo aws sts get-caller-identity >/dev/null 2>&1; then
  echo "✔ Root credentials OK"
else
  echo "⚠ Root credentials missing — configuring for root"
  sudo bash -c "$(declare -f ensure_credentials); ensure_credentials root /root"
fi

echo "🎉 Setup completed successfully — AWS + SSL ready"
