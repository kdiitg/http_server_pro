# --- File: class_handler.py ---

import os
import uuid
import html
from http.server import SimpleHTTPRequestHandler
from .useful_fn import format_size  # Import shared utility

from http import cookies
import random

current_pin = f"{random.randint(1000, 9999)}"
print(f"Access PIN is: {current_pin}")

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs

        session_cookie = self.headers.get("Cookie")
        session_ok = False

        # Check cookie first
        if session_cookie:
            c = cookies.SimpleCookie(session_cookie)
            if "access" in c and c["access"].value == current_pin:
                session_ok = True

        # Check URL token ?pin=XXXX
        if not session_ok:
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            if 'pin' in query and query['pin'][0] == current_pin:
                session_ok = True
                self.send_response(302)
                self.send_header("Location", parsed.path or "/")
                self.send_header("Set-Cookie", f"access={current_pin}; Path=/")
                self.end_headers()
                return

        # If still not valid
        if not session_ok and self.path not in ["/favicon.ico", "/pin"]:

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write("""
                <html>
                <head>
                    <title>🔒 Enter Access PIN</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            text-align: center;
                            margin-top: 100px;
                        }
                        input[type="password"] {
                            font-size: 24px;
                            padding: 10px;
                            width: 120px;
                            text-align: center;
                        }
                        button {
                            font-size: 20px;
                            padding: 10px 24px;
                            background-color: #4CAF50;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            cursor: pointer;
                        }
                        button:hover {
                            background-color: #45a049;
                        }
                    </style>
                </head>
                <body>
                    <h2>Enter 4-digit PIN</h2>
                    <form method="POST">
                        <input type="password" name="pin" maxlength="4" pattern="\d{4}" inputmode="numeric" required>
                        <br><br>
                        <button type="submit">Unlock</button>
                    </form>
                </body>
                </html>
                """.encode("utf-8"))

            return

        if self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-Type', 'image/x-icon')
            self.end_headers()
            self.wfile.write(
                b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x04\x00'
                b'\x28\x01\x00\x00\x16\x00\x00\x00\x16\x00\x00\x00\x00\x00'
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            )
        elif self.path == '/upload':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Upload File</title>
                <meta name="viewport" content="width=device-width, initial-scale=0.9">
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        text-align: center;
                        padding: 20px;
                    }
                    .upload-box {
                        border: 2px dashed #ccc;
                        border-radius: 10px;
                        padding: 30px;
                        background-color: #f9f9f9;
                        max-width: 90%;
                        margin: auto;
                    }
                    input[type="file"] {
                        font-size: 18px;
                        padding: 12px;
                        margin-bottom: 20px;
                    }
                    input[type="submit"] {
                        font-size: 18px;
                        padding: 12px 30px;
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                    }
                    input[type="submit"]:hover {
                        background-color: #45a049;
                    }
                </style>
            </head>
            <body>
                <h2>Upload Files to Server</h2>
                <div class="upload-box">
                    <form enctype="multipart/form-data" method="post">
                        <input type="file" name="file" required><br>
                        <input type="submit" value="Upload File">
                    </form>
                </div>
                <p><a href="/">Back to Home</a></p>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
            return
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/upload':
            content_length = int(self.headers.get('Content-Length', 0))
            content_type = self.headers.get('Content-Type')
            boundary = content_type.split("boundary=")[-1].encode()
            data = self.rfile.read(content_length)
            parts = data.split(b"--" + boundary)
            saved_files = 0

            for part in parts:
                if b'Content-Disposition:' in part:
                    header, file_data = part.split(b"\r\n\r\n", 1)
                    header = header.decode()
                    file_data = file_data.rstrip(b"\r\n--")
                    filename = "upload_" + uuid.uuid4().hex
                    for line in header.split("\r\n"):
                        if "filename=" in line:
                            filename = line.split("filename=")[-1].strip('"')
                            break

                    base, ext = os.path.splitext(filename)
                    count = 1
                    while os.path.exists(filename):
                        filename = f"{base}_{count}{ext}"
                        count += 1

                    with open(filename, "wb") as f:
                        f.write(file_data)
                        saved_files += 1

            self.send_response(200)
            self.end_headers()
            self.wfile.write(f"""
            <html>
            <head>
                <title>Upload Complete</title>
                <meta name='viewport' content='width=device-width, initial-scale=0.9'>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 100px; }}
                    h2 {{ color: green; }}
                    a {{ display: inline-block; margin-top: 20px; font-size: 18px; color: #2196F3; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                </style>
            </head>
            <body>
                <h2>{saved_files} file(s) uploaded successfully!</h2>
                <a href='/'>Go back to Home</a>
            </body>
            </html>
            """.encode())

        else:
            # PIN submission
            length = int(self.headers.get("Content-Length", 0))
            data = self.rfile.read(length).decode()
            pin_value = data.split("pin=")[-1]

            if pin_value == current_pin:
                self.send_response(302)
                self.send_header("Location", "/")
                self.send_header("Set-Cookie", f"access={current_pin}; Path=/")
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h3>Incorrect PIN. Try again.</h3>")

    def list_directory(self, path):
        try:
            entries = os.listdir(path)
        except OSError:
            self.send_error(404, "No permission to list directory")
            return None

        f = []
        displaypath = html.escape(self.path)
        f.append(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>📁 File Share</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        padding: 20px;
                        text-align: center;
                    }}
                    h2 {{
                        margin-bottom: 10px;
                    }}
                    a.upload-btn {{
                        display: inline-block;
                        margin-bottom: 20px;
                        padding: 12px 24px;
                        font-size: 18px;
                        background-color: #2196F3;
                        color: white;
                        text-decoration: none;
                        border-radius: 6px;
                    }}
                    a.upload-btn:hover {{
                        background-color: #0b7dda;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 10px;
                    }}
                    th, td {{
                        text-align: left;
                        padding: 8px;
                        border-bottom: 1px solid #ddd;
                    }}
                </style>
            </head>
            <body>
                <h2>📁 Shared Folder</h2>
                <a href="/upload" class="upload-btn">📤 Upload Files</a>
                <hr>
                <table>
                    <tr><th>Name</th><th>Size</th></tr>
        """)

        entries.sort(key=lambda a: a.lower())
        for name in entries:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            size = os.path.getsize(fullname)
            size_str = format_size(size)
            f.append(f"<tr><td><a href=\"{html.escape(linkname)}\">{html.escape(displayname)}</a></td><td>{size_str}</td></tr>")


        f.append("""
                </table>
            </body>
            </html>
        """)
        encoded = "\n".join(f).encode("utf-8", "surrogateescape")
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
        return None
