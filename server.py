#!/usr/bin/env python3

# ========= AUTO-BOOTSTRAP =========
import os, sys, subprocess

def ensure_environment_ready():
    def need_bootstrap():
        try:
            import boto3, ssl  # noqa
        except Exception:
            return True

        # SSL must exist before starting HTTPS
        if not os.path.exists("cert.pem") or not os.path.exists("key.pem"):
            return True

        return False

    if not need_bootstrap():
        return

    print("⚠ Environment not ready — running starter.sh...")

    if not os.path.exists("starter.sh"):
        print("❌ starter.sh missing — cannot auto-setup")
        sys.exit(1)

    subprocess.run(["bash", "starter.sh"], check=True)

    # reload process after setup
    os.execv(sys.executable, [sys.executable] + sys.argv)

ensure_environment_ready()
# ==================================

import http.server, socketserver, urllib.parse, cgi
import boto3, ssl, json

PORT = 443
CONFIG_FILE = "app_config.json"


# ---------- CONFIG ----------
def load_config():
    return json.load(open(CONFIG_FILE)) if os.path.exists(CONFIG_FILE) else {}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f)

def build_s3(cfg):
    return boto3.client(
        "s3",
        aws_access_key_id=cfg["aws"]["access_key"],
        aws_secret_access_key=cfg["aws"]["secret_key"],
        region_name=cfg["aws"]["region"]
    )


config = load_config()
s3 = build_s3(config) if config.get("aws") else None


# ---------- PROFESSIONAL UI ----------
def base_layout(content):
    return f"""
    <html>
    <head>
      <meta charset='utf-8'>
      <title>S3 Manager</title>
      <style>
      body {{
        margin:0;background:#020617;color:#e5e7eb;
        font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu;
      }}
      .top {{
        background:#030712;border-bottom:1px solid #1f2937;
        padding:18px 28px;font-size:18px;font-weight:600;
        display:flex;justify-content:space-between;align-items:center;
      }}
      .top .actions a {{
        margin-left:8px;padding:7px 12px;border-radius:10px;
        border:1px solid #1f2937;text-decoration:none;
        background:#0f172a;color:#e5e7eb;font-size:13px;
      }}
      .top .danger {{ background:#7f1d1d;color:#fca5a5 }}
      .wrap {{ max-width:1100px;margin:28px auto;padding:0 10px }}
      .card {{
        background:#020617;border:1px solid #1f2937;
        border-radius:16px;padding:26px 28px;
        box-shadow:0 20px 40px #0004;
      }}
      h2 {{ margin-top:0;font-size:20px }}
      .input {{
        width:100%;padding:10px;border-radius:10px;
        border:1px solid #334155;background:#020617;color:#e5e7eb;
      }}
      .btn {{
        padding:8px 14px;border-radius:10px;border:0;
        background:#2563eb;color:white;font-weight:600;cursor:pointer;
      }}
      table {{
        width:100%;border-collapse:collapse;margin-top:10px;
      }}
      th,td {{
        padding:12px;border-bottom:1px solid #1f2937;
        font-size:14px;
      }}
      th {{ color:#94a3b8;text-transform:uppercase;font-size:12px }}
      .tag {{ color:#a5b4fc }}
      .uploadbox {{
        border:1px dashed #334155;border-radius:14px;
        padding:18px;margin-top:20px;text-align:center;
        background:#020617;
      }}
      .muted {{ color:#6b7280 }}
      </style>
    </head>
    <body>
      {content}
    </body>
    </html>
    """


# ---------- PAGES ----------
def page_bucket():
    return base_layout(f"""
    <div class='wrap'>
      <div class='card' style='max-width:480px'>
        <h2>Select Bucket</h2>
        <form method='post' action='/save-bucket'>
          <input class='input' name='bucket' placeholder='bucket-name'><br><br>
          <button class='btn'>Continue</button>
        </form>
      </div>
    </div>
    """)


def page_creds():
    return base_layout(f"""
    <div class='wrap'>
      <div class='card' style='max-width:480px'>
        <h2>AWS Credentials</h2>
        <form method='post' action='/save-creds'>
          <input class='input' name='access_key' placeholder='Access Key'><br><br>
          <input class='input' name='secret_key' placeholder='Secret Key'><br><br>
          <input class='input' name='region' value='us-east-1'><br><br>
          <button class='btn'>Save</button>
        </form>
      </div>
    </div>
    """)


# ---------- HANDLER ----------
class UploadHandler(http.server.BaseHTTPRequestHandler):

    def respond(self, html):
        self.send_response(200)
        self.send_header("Content-Type","text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_GET(self):
        global config, s3

        if not config.get("bucket"):
            return self.respond(page_bucket())

        if not config.get("aws") or not s3:
            return self.respond(page_creds())

        p = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(p.query)

        if p.path == "/change-bucket":
            config.pop("bucket",None); save_config(config)
            return self.respond(page_bucket())

        if p.path == "/change-creds":
            config.pop("aws",None); save_config(config)
            return self.respond(page_creds())

        # download
        if p.path == "/download":
            try:
                key = q.get("file",[""])[0]
                local = f"/tmp/{os.path.basename(key)}"
                s3.download_file(config["bucket"], key, local)
                return self.respond(base_layout(
                    f"<div class='wrap'><div class='card'>Downloaded → {local}</div></div>"
                ))
            except Exception:
                return self.respond(base_layout(
                    "<div class='wrap'><div class='card'>Error downloading</div></div>"
                ))

        # delete
        if p.path == "/delete":
            try:
                key = q.get("file",[""])[0]
                s3.delete_object(Bucket=config["bucket"], Key=key)
                return self.respond(base_layout(
                    "<div class='wrap'><div class='card'>File deleted</div></div>"
                ))
            except Exception:
                return self.respond(base_layout(
                    "<div class='wrap'><div class='card'>Delete failed</div></div>"
                ))

        # list
        try:
            objs = s3.list_objects_v2(Bucket=config["bucket"]).get("Contents",[])
        except Exception:
            objs = []

        rows = "".join([
            f"<tr><td>{o['Key']}</td>"
            f"<td class='muted'>{o['Size']:,} bytes</td>"
            f"<td style='text-align:right'>"
            f"<a class='tag' href='/download?file={urllib.parse.quote(o['Key'])}'>Download</a> &nbsp;"
            f"<a class='tag' href='/delete?file={urllib.parse.quote(o['Key'])}'>Delete</a>"
            f"</td></tr>"
            for o in objs
        ]) or "<tr><td colspan=3 class='muted'>No files</td></tr>"

        html = base_layout(f"""
        <div class='top'>
          S3 Manager — {config['bucket']}
          <div class='actions'>
            <a href='/change-bucket'>Change Bucket</a>
            <a class='danger' href='/change-creds'>Change Credentials</a>
          </div>
        </div>

        <div class='wrap'>
          <div class='card'>
            <h2>Files</h2>

            <table>
              <tr><th>Name</th><th>Size</th><th></th></tr>
              {rows}
            </table>

            <div class='uploadbox'>
              <form method='post' enctype='multipart/form-data'>
                <input type='file' name='file'><br><br>
                <button class='btn'>Upload</button>
              </form>
            </div>
          </div>
        </div>
        """)

        self.respond(html)

    def do_POST(self):
        global config, s3

        if self.path == "/save-bucket":
            body = self.rfile.read(int(self.headers["Content-Length"])).decode()
            form = urllib.parse.parse_qs(body)
            config["bucket"] = form["bucket"][0]
            save_config(config)
            return self.respond("<script>location='/'</script>")

        if self.path == "/save-creds":
            body = self.rfile.read(int(self.headers["Content-Length"])).decode()
            form = urllib.parse.parse_qs(body)
            config["aws"] = {
                "access_key": form["access_key"][0],
                "secret_key": form["secret_key"][0],
                "region": form["region"][0]
            }
            save_config(config)
            s3 = build_s3(config)
            return self.respond("<script>location='/'</script>")

        try:
            form = cgi.FieldStorage(
                fp=self.rfile, headers=self.headers,
                environ={"REQUEST_METHOD":"POST"}
            )
            s3.upload_fileobj(form["file"].file,
                              config["bucket"],
                              form["file"].filename)
            return self.respond("<script>location='/'</script>")
        except Exception:
            return self.respond("<script>alert('Upload failed')</script>")


# ---------- HTTPS SERVER ----------
with socketserver.TCPServer(("", PORT), UploadHandler) as httpd:
    print(f"Serving S3 manager on port {PORT} (HTTPS)")
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain("cert.pem","key.pem")
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
    httpd.serve_forever()
