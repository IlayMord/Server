# S3 File Manager (HTTPS)

A simple Python web server for managing files in an Amazon S3 bucket via a browser.  
The interface supports uploading, downloading, and deleting files over a secure HTTPS connection.

---

## ✨ Features
- Automatically installs:
  - `python3-pip`
  - Project dependencies from `requirements.txt`
  - `curl` and `unzip`
  - AWS CLI v2 (only if missing)
- Ensures SSL certificate files (`cert.pem`, `key.pem`) exist — generates them if needed
- Runs an HTTPS server on port **443**
- Lists files from the configured S3 bucket
- Supports:
  - Uploading files to S3
  - Downloading files to `/tmp`
  - Deleting files from S3

---

## 🔧 Requirements
- Ubuntu / Linux environment  
- Python 3  
- `openssl`  
- Valid AWS credentials  
- Existing S3 bucket  

> Default bucket: `ilay-bucket1` (can be changed inside the code)

---

## ⚙️ Setup (Auto-Bootstrap)

Run the setup script — it will prepare everything automatically:

```bash
chmod +x starter.sh
./starter.sh
