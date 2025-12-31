# S3 File Manager (HTTPS)

A simple Python web server for managing files in an Amazon S3 bucket via a browser.  
The interface supports uploading, downloading, and deleting files over a secure HTTPS connection.

---

## ✨ Features
- Verifies that **AWS CLI** is installed (runs `starter.sh` if missing)
- Ensures SSL certificate files (`cert.pem`, `key.pem`) exist — generates new ones if needed
- Runs an HTTPS server on port **443**
- Lists files from the configured S3 bucket
- Supports:
  - Uploading files to S3
  - Downloading files to `/tmp`
  - Deleting files from S3

---

## 🔧 Requirements
- Python 3
- `boto3`
- `openssl`
- Valid AWS credentials
- Existing S3 bucket

> Default bucket: `ilay-bucket1` (can be changed in the code)

---

## 🚀 Run

```bash
sudo python3 server.py
