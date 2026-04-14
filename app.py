from flask import Flask, render_template, request, redirect, send_from_directory
import os, shutil, socket, qrcode, webbrowser, random, string 
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import time
import datetime 
import uuid
import sys
import threading


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def create_icon():
    img = Image.new('RGB', (64, 64), color=(0, 150, 136))
    d = ImageDraw.Draw(img)
    d.text((20, 20), "A", fill=(255, 255, 255))
    return img

def open_app(icon, item):
    webbrowser.open(f"http://{ip}:5000")

def stop_app(icon, item):
    icon.stop()
    os._exit(0)   

def run_tray():
    icon = Icon(
        "AirDropApp",
        create_icon(),
        "AirDrop App",
        menu=Menu(
            MenuItem("Open Dashboard", open_app),
            MenuItem("Exit", stop_app)
        )
    )
    icon.run()


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

PENDING = "uploads/pending"
ACCEPTED = "uploads/accepted"

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

    threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=5000, debug=False),
        daemon=True
    ).start()


    threading.Thread(target=open_browser, args=(ip,)).start()
   
    run_tray()