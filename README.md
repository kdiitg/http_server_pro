# 📡 HTTP Server PRO

**HTTP Server PRO** is a simple GUI-based file-sharing app built with Python and Tkinter that lets you:

- Serve a local folder over HTTP instantly
- Generate a QR code for easy mobile access
- Share your folder globally using ngrok
- No coding needed — just run and share

---

## 🚀 Features

✅ Share any folder over HTTP  
✅ Works on LAN (local IP)  
✅ One-click support for ngrok (public sharing)  
✅ Automatically generates QR code  
✅ Shows real-time server status  
✅ Tkinter-based GUI for ease of use  
✅ Works cross-platform (Windows, Linux, macOS)
✅ New! Secure file upload & download with PIN protection


## 🔐 Secure File Sharing with PIN (New!)
- HTTP Server PRO now includes built-in security for file sharing. Both uploads and downloads are protected using a 4-digit PIN.
---

## Key Highlights:
### 🔒 PIN-Protected Access

** A unique 4-digit PIN is generated each time the server starts. This PIN is required to: **

- Download files from the server
- Upload files to the shared folder

### 📱 QR Code with Auto Authentication
- Scanning the QR code includes the PIN in the link, so no manual entry is needed.

### 🌍 Secure Over LAN or ngrok
- PIN protection applies whether you're sharing locally or publicly via ngrok.

### How It Works:
- On server startup, a random PIN is displayed in the app.
- Upload and download pages require the correct PIN to proceed.
- QR code links include the PIN for instant access.
- Unauthorized users without the correct PIN are blocked from accessing any files.

---

## 📦 Installation
```bash
pip install http_server_pro
```
## 🧠 Usage

### Option 1: From Python code

```python
import http_server_pro
http_server_pro.start()
```
### Option 2: From terminal
```bash
http_server_pro








