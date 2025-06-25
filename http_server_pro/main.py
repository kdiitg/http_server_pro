# --- File: main.py ---
from .dependencies_checker import check_and_install_dependencies
check_and_install_dependencies()

from .class_handler_copy import MyHandler, current_pin
from .useful_fn import get_local_ip

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from http.server import HTTPServer
from PIL import Image, ImageTk
import qrcode
import subprocess
import requests
import time


# --- Globals ---
server_instance = None
server_thread = None
ngrok_process = None
ngrok_url = None
current_mode = "local"
server_running = False
ngrok_running = False

# --- Start HTTP server ---
def start_server(folder, port):
    global server_instance
    os.chdir(folder)
    server_instance = HTTPServer(('0.0.0.0', port), MyHandler)
    print(f"Serving HTTP on {get_local_ip()}:{port}")
    server_instance.serve_forever()

# --- Start/Stop Server button ---
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
            print("Error getting ngrok URL:", e)
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
            # url = f"http://{ip}:{port}/?pin={current_pin}"
            url_label.config(text=ngrok_url + f"?pin={current_pin}")
            # Generate QR code for ngrok URL
            generate_qr(ngrok_url + f"?pin={current_pin}")
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
    # url = f"http://{ip}:{port}/"
    url = f"http://{ip}:{port}/?pin={current_pin}"
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

# --- UI ---
root = tk.Tk()
root.title("📡 Local HTTP Server PRO")
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
