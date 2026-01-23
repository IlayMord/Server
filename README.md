# S3 File Manager 🚀

A lightweight Python web UI for browsing and managing files in an Amazon S3 bucket.
Runs locally and stores configuration on the server.

## ✨ Features
- Web UI for listing, uploading (multi-file), downloading, deleting, and creating folders
- Prefix navigation with breadcrumbs
- Search with server-side pagination
- Sort and grid/list view toggle
- Copy S3 URIs to clipboard
- Upload progress bar and drag-and-drop support
- Preview for common file types (images, video, audio, text, PDF)
- Share links via pre-signed URLs
- Bulk actions (move, copy, delete) and rename
- Optional basic auth (username/password)
- Theme toggle (light/dark)

## ✅ Requirements
- Python 3.8+
- AWS credentials with access to the target S3 bucket
- Existing S3 bucket

## 📦 Install
```bash
python3 -m pip install -r requirements.txt
```

## ▶️ Run
```bash
python3 server.py
```

Then open `http://localhost:80` in your browser (or the port you set).

## ⚙️ Configuration
The app stores configuration in:
- `~/.s3-file-manager/app_config.json` (preferred)
- `/tmp/s3-file-manager/app_config.json` (fallback)

You can override paths/ports with environment variables:
- `S3MGR_PORT` (default: `80`)
- `S3MGR_CONFIG_DIR`
- `S3MGR_USERNAME` (default: `admin`)
- `S3MGR_PASSWORD` (empty means no auth)

## 📝 Notes
- `/download` streams to the browser. `/download-server` saves to `/tmp/<filename>` on the server host.
- Credentials are stored locally on the server and are not encrypted.
