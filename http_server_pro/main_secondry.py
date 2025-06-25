# --- Auto Dependency Installer ---
import os
import sys
import subprocess

def check_and_install_dependencies():
    marker_path = os.path.expanduser("~/.http_server_deps_ok")

    if os.path.exists(marker_path):
        return  # Already installed

    required = ["Pillow", "qrcode", "requests"]
    missing = []

    for pkg in required:
        try:
            __import__(pkg.lower() if pkg != "Pillow" else "PIL")
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"Installing missing packages: {missing}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
            with open(marker_path, "w") as f:
                f.write("Dependencies installed.\n")
            print("✅ All dependencies installed successfully.")
        except Exception as e:
            print("❌ Error installing dependencies:", e)
            input("Press Enter to exit...")
            sys.exit(1)

check_and_install_dependencies()


import socket
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import qrcode
import requests
import time

# --- Get local IP ---
def get_local_ip():
    ip = '127.0.0.1'
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        pass
    finally:
        s.close()
    return ip

# --- HTTP handler ---
class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-Type', 'image/x-icon')
            self.end_headers()
            self.wfile.write(
                b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x04\x00'
                b'\x28\x01\x00\x00\x16\x00\x00\x00\x16\x00\x00\x00\x00\x00'
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            )
        else:
            super().do_GET()

    def list_directory(self, path):
        try:
            entries = os.listdir(path)
        except OSError:
            self.send_error(404, "No permission to list directory")
            return None

        if not entries:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            message = f"""
            <html>
            <head><title>Empty Folder</title></head>
            <body style='font-family: Arial; text-align: center;'>
                <h2>📂 Folder is empty</h2>
                <p>Path: {path}</p>
            </body>
            </html>
            """
            self.wfile.write(message.encode("utf-8"))
            return None

        return super().list_directory(path)

# --- Globals ---
server_instance = None
server_thread = None
ngrok_process = None
ngrok_url = None
current_mode = "local"
server_running = False
ngrok_running = False

def start_server(folder, port):
    global server_instance
    os.chdir(folder)
    server_instance = HTTPServer(('0.0.0.0', port), MyHandler)
    print(f"Serving HTTP on {get_local_ip()}:{port}")
    server_instance.serve_forever()

def toggle_server():
    global server_thread, current_mode, server_running
    if not server_running:
        folder = folder_path.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder first.")
            return
        try:
            port = int(port_entry.get())
            if not (1 <= port <= 65535):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid port number (1-65535).")
            return
        if not os.listdir(folder):
            index_path = os.path.join(folder, "index.html")
            with open(index_path, "w") as f:
                f.write(f"""
                <html>
                <head><title>My Local HTTP Server</title></head>
                <body style='font-family: Arial; text-align: center;'>
                    <h1>🚀 Welcome to my local HTTP server!</h1>
                    <p>Serving folder: {folder}</p>
                </body>
                </html>
                """)
        server_thread = threading.Thread(target=start_server, args=(folder, port), daemon=True)
        server_thread.start()
        server_running = True
        current_mode = "local"
        update_ui_state()
        switch_to_local()
    else:
        stop_server()

def stop_server():
    global server_instance, ngrok_process, current_mode, server_running, ngrok_running
    if server_instance:
        server_instance.shutdown()
        server_instance.server_close()
        server_instance = None
    if ngrok_process:
        stop_ngrok()
        ngrok_process = None
    current_mode = "local"
    server_running = False
    ngrok_running = False
    url_label.config(text="Server stopped.")
    qr_label.config(image='')
    update_ui_state()
    messagebox.showinfo("Server Stopped", "HTTP server has been stopped.")

def stop_ngrok():
    global ngrok_process
    if ngrok_process:
        try:
            if os.name == 'nt':
                os.system("taskkill /F /IM ngrok.exe")
            else:
                os.system("pkill ngrok")
        except Exception as e:
            print("Error stopping ngrok:", e)
        ngrok_process = None

def toggle_ngrok():
    global ngrok_process, ngrok_url, current_mode, ngrok_running
    if not ngrok_running:
        port = int(port_entry.get())
        if ngrok_process:
            stop_ngrok()
            ngrok_process = None
        ngrok_process = subprocess.Popen(['ngrok', 'http', str(port)],
                                         stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        time.sleep(3)
        try:
            resp = requests.get("http://127.0.0.1:4040/api/tunnels")
            tunnels = resp.json()["tunnels"]
            for t in tunnels:
                if t["proto"] == "https":
                    ngrok_url = t["public_url"]
                    break
        except Exception as e:
            messagebox.showerror("Ngrok Error", "Unable to get ngrok URL. Is ngrok running?")
            return
        if ngrok_url:
            ngrok_running = True
            update_ui_state()
    else:
        stop_ngrok()
        ngrok_process = None
        ngrok_running = False
        update_ui_state()

def switch_url():
    global current_mode
    if current_mode == "local":
        if ngrok_running and ngrok_url:
            url_label.config(text=ngrok_url)
            generate_qr(ngrok_url)
            current_mode = "global"
            update_ui_state()
        else:
            messagebox.showerror("Error", "Ngrok is not running!")
    else:
        switch_to_local()

def switch_to_local():
    global current_mode
    port = int(port_entry.get())
    ip = get_local_ip()
    url = f"http://{ip}:{port}/"
    url_label.config(text=url)
    generate_qr(url)
    current_mode = "local"
    update_ui_state()

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_path.set(folder)
        selected_folder_label.config(text=f"📂 {folder}")

def generate_qr(url):
    qr = qrcode.make(url)
    qr = qr.resize((130, 130))
    qr_img = ImageTk.PhotoImage(qr)
    qr_label.config(image=qr_img)
    qr_label.image = qr_img

def update_ui_state():
    if server_running:
        server_button.config(text="⛔ Stop Server", bg="#f44336")
        ngrok_button.config(state="normal")
        switch_button.config(state="normal")
        server_status_label.config(text="🟢 Server running", fg="#7ABD7C")
        if ngrok_running:
            ngrok_button.config(text="⛔ Stop ngrok", bg="#f44336")
        else:
            ngrok_button.config(text="🌐 Start ngrok", bg="#9c27b0")
        if current_mode == "local":
            switch_button.config(text="🌐 Switch to Global")
        else:
            switch_button.config(text="🏠 Switch to Local")
    else:
        server_button.config(text="🚀 Start Server", bg="#2196F3")
        ngrok_button.config(state="disabled")
        switch_button.config(state="disabled")
        server_status_label.config(text="🔴 Server stopped", fg="#f44336")

def main():
    global root, folder_path, port_entry, selected_folder_label, server_button, ngrok_button, switch_button, url_label, qr_label, server_status_label

    root = tk.Tk()
    root.title("📡 HTTP Server PRO")
    root.geometry("500x700")
    root.resizable(False, False)
    root.configure(bg="#f8f8f8")

    folder_path = tk.StringVar()

    tk.Label(root, text="🌍 HTTP Server PRO", font=("Arial", 18, "bold"), bg="#f8f8f8").pack(pady=10)
    tk.Label(root, text="Select Folder to Share:", font=("Arial", 12), bg="#f8f8f8").pack(pady=5)
    tk.Button(root, text="📂 Browse Folder", command=select_folder, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=5)

    selected_folder_label = tk.Label(root, text="No folder selected", fg="#3333cc", bg="#f8f8f8", wraplength=440, justify="left")
    selected_folder_label.pack(pady=5)

    tk.Label(root, text="Enter Port:", font=("Arial", 12), bg="#f8f8f8").pack(pady=10)
    port_entry = tk.Entry(root, width=10, font=("Arial", 12), justify="center")
    port_entry.insert(0, "8000")
    port_entry.pack(pady=5)

    server_button = tk.Button(root, text="🚀 Start Server", command=toggle_server, font=("Arial", 14, "bold"), bg="#2196F3", fg="white", padx=10, pady=5)
    server_button.pack(pady=15)

    row_frame = tk.Frame(root, bg="#f8f8f8")
    row_frame.pack(pady=5)

    ngrok_button = tk.Button(row_frame, text="🌐 Start ngrok", command=toggle_ngrok, font=("Arial", 12), bg="#9c27b0", fg="white", padx=10, pady=5, state="disabled")
    ngrok_button.pack(side="left", padx=10)

    switch_button = tk.Button(row_frame, text="🌐 Switch to Global", command=switch_url, font=("Arial", 12), bg="#607d8b", fg="white", padx=10, pady=5, state="disabled")
    switch_button.pack(side="left", padx=10)

    tk.Label(root, text="📡 Current URL:", font=("Arial", 12), bg="#f8f8f8").pack(pady=10)
    url_label = tk.Label(root, text="", fg="#e91e63", font=("Arial", 12), bg="#f8f8f8", wraplength=440)
    url_label.pack(pady=5)

    tk.Label(root, text="📱 QR Code:", font=("Arial", 12), bg="#f8f8f8").pack(pady=10)
    qr_label = tk.Label(root, bg="#f8f8f8")
    qr_label.pack(pady=10)

    server_status_label = tk.Label(root, text="🔴 Server stopped", font=("Arial", 12), bg="#f8f8f8", fg="#f44336")
    server_status_label.pack(pady=10)

    tk.Label(root, text="Created by Kuldeep Singh 🤖 V7.2 PRO", font=("Arial", 10), fg="#888888", bg="#f8f8f8").pack(side="bottom", pady=10)

    root.mainloop()

# Entry point for pip or command-line usage
def start():
    main()

# Optional: allow `python main.py` run directly for dev
if __name__ == "__main__":
    start()
