from flask import Flask, render_template, request, redirect, send_from_directory
import os, shutil, socket, qrcode, webbrowser, random, string 
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import time
import datetime 
import uuid
import sys
import threading
import customtkinter as ctk




# Windows only shortcut
def create_shortcut():
    try:
        import winshell
        from win32com.client import Dispatch

        desktop = winshell.desktop()
        path = os.path.join(desktop, "AirDrop App.lnk")

        target = os.path.abspath(sys.executable)  # IMPORTANT for EXE

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = os.getcwd()
        shortcut.IconLocation = target
        shortcut.save()

    except:
        pass  # ignore on Linux




def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


def open_app(icon, item):
    webbrowser.open(f"http://{ip}:5000")




def get_file_data(folder, filename, status):
    path = os.path.join(folder, filename)
    timestamp = os.path.getmtime(path)

    dt = datetime.datetime.fromtimestamp(timestamp)

    return {
        "name": filename,
        "status": status,
        "time": dt.strftime("%H:%M"),
        "date": dt.strftime("%d/%m/%Y"),
        "timestamp": timestamp   
    }

app = Flask(__name__)

BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")

PENDING = os.path.join(BASE_DIR, "uploads/pending")
ACCEPTED = os.path.join(BASE_DIR, "uploads/accepted")

os.makedirs(PENDING, exist_ok=True)
os.makedirs(ACCEPTED, exist_ok=True)

# ---------------- TOKEN ----------------
def generate_token(length=6):
     return str(uuid.uuid4())[:length]

CURRENT_TOKEN = None

# ---------------- IP ----------------
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

# ---------------- QR ----------------
def generate_qr(ip):
    global CURRENT_TOKEN
    CURRENT_TOKEN = generate_token()

    url = url = f"http://{ip}:5000/new"
    img = qrcode.make(url)
    img.save(resource_path("static/qr.png"))

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return redirect('/dashboard')

@app.route('/new')
def new_user():
    token = generate_token()
    return redirect(f'/upload?token={token}')

@app.route('/check-updates')
def check_updates():
    all_files = []

    for f in os.listdir(PENDING):
        path = os.path.join(PENDING, f)
        all_files.append(os.path.getmtime(path))

    for f in os.listdir(ACCEPTED):
        path = os.path.join(ACCEPTED, f)
        all_files.append(os.path.getmtime(path))

    latest = max(all_files) if all_files else 0

    return {"last_update": latest}

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    token = request.args.get('token')

    if not token:
        return "Token missing "

    if request.method == 'POST':
        files = request.files.getlist("files")

        for file in files:
            if file.filename:
                filename = f"{token}_{file.filename}"
                file.save(os.path.join(PENDING, filename))

        return "OK"

    return render_template("upload.html", token=token)

@app.route('/dashboard')
def dashboard():
    pending_files = os.listdir(PENDING)
    accepted_files = os.listdir(ACCEPTED)

    files = []

    for f in pending_files:
        files.append(get_file_data(PENDING, f, "pending"))

    for f in accepted_files:
        files.append(get_file_data(ACCEPTED, f, "accepted"))

    files.sort(
    key=lambda x: (x["status"] != "pending", -x["timestamp"])
    )

    ip = get_ip()

    return render_template("dashboard.html", files=files, ip=ip, token=CURRENT_TOKEN)

# ---------------- ACTIONS ----------------

@app.route('/accept/<filename>')
def accept(filename):
    src = os.path.join(PENDING, filename)
    dst = os.path.join(ACCEPTED, filename)

    if os.path.exists(src):
        shutil.move(src, dst)

    return redirect('/dashboard')

@app.route('/reject/<filename>')
def reject(filename):
    path = os.path.join(PENDING, filename)

    if os.path.exists(path):
        os.remove(path)

    return redirect('/dashboard')

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(ACCEPTED, filename, as_attachment=True)

@app.route('/print/<filename>')
def print_file(filename):
    return send_from_directory(ACCEPTED, filename)

@app.route('/delete/<filename>')
def delete_file(filename):
    path = os.path.join(ACCEPTED, filename)

    if os.path.exists(path):
        os.remove(path)

    return redirect('/dashboard')

def launch_control_panel(ip):

    def open_dashboard():
        webbrowser.open(f"http://{ip}:5000")

    def quit_app():
        app.destroy()
        os._exit(0)

    # MAIN WINDOW
    app = ctk.CTk()
    app.geometry("320x220")
    app.title("AirDrop App")
    app.resizable(False, False)

    # ICON
    try:
        icon_path = os.path.join(BASE_DIR, "static/icon.ico")
        app.iconbitmap(icon_path)
    except:
        pass

    # BODY (CREATE FIRST ✅)
    body = ctk.CTkFrame(app, fg_color="white")
    body.pack(fill="both", expand=True)

    try:
     # Windows
     ico_path = os.path.join(BASE_DIR, "static/icon.ico")
     app.iconbitmap(ico_path)
    except:
      try:
        # Linux fallback
        png_path = os.path.join(BASE_DIR, "static/icon.png")
        img = Image.open(png_path)
        app.iconphoto(True, ctk.CTkImage(light_image=img)._light_image)
      except:
        pass
      
    # TEXT
    label = ctk.CTkLabel(
        body,
        text="Server is running.........",
        text_color="#7B5CF5",
        font=("Arial", 20)
    )
    label.pack(pady=15)

    label = ctk.CTkLabel(
        body,
        text="to launch dashboard click launh",
        text_color="Black",
        font=("Calibary", 10)
    )
    label.pack(pady=15,padx=5)

    # BUTTON FRAME
    btn_frame = ctk.CTkFrame(body, fg_color="white")
    btn_frame.pack(pady=15)

    # RELAUNCH BUTTON
    launch_btn = ctk.CTkButton(
        btn_frame,
        text="LAUNCH",
        width=120,
        height=42,
        corner_radius=20,
        fg_color="#B8E986",
        text_color="black",
        hover_color="#a3d974",
        font=("Arial", 11, "bold"),
        command=open_dashboard
    )
    launch_btn.grid(row=0, column=0, padx=12)

    # QUIT BUTTON
    quit_btn = ctk.CTkButton(
        btn_frame,
        text="QUIT",
        width=120,
        height=42,
        corner_radius=20,
        fg_color="#F36C6C",
        text_color="black",
        hover_color="#e25555",
        font=("Arial", 11, "bold"),
        command=quit_app
    )
    quit_btn.grid(row=0, column=1, padx=12)

    app.mainloop()

def cleanup(folder, seconds=86400):  # 1 day
    now = time.time()

    for f in os.listdir(folder):
        path = os.path.join(folder, f)

        if os.path.isfile(path):
            if now - os.path.getmtime(path) > seconds:
                os.remove(path)

#---------------- RUN ----------------
def open_browser(ip):
    time.sleep(2)
    webbrowser.open(f"http://{ip}:5000")

if __name__ == '__main__':
    ip = get_ip()
    
    cleanup("uploads/accepted")
    cleanup("uploads/pending")
    generate_qr(ip)

    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_path = os.path.join(desktop, "AirDrop App.lnk")

    if sys.platform == "win32" and not os.path.exists(shortcut_path):
      create_shortcut()


    threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=5000, debug=False),
        daemon=True
    ).start()

    launch_control_panel(ip)

# pyinstaller --onefile --noconsole ^
# --icon=icon.ico ^
# --hidden-import customtkinter ^
# --hidden-import winshell ^
# --hidden-import win32com ^
# --add-data "templates;templates" ^
# --add-data "static;static" ^
# app.py


