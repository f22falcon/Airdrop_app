# 🚀 AirDrop App

A fast and simple **local file transfer application** that allows users to upload files from their mobile devices to a desktop using a QR code — no internet required.

---

## ✨ Features

* 📱 Upload files from mobile via QR code
* 🖥 Real-time dashboard for file management
* ✅ Accept / Reject incoming files
* ⬇ Download files easily
* 🖨 Print supported files
* 🗑 Delete unnecessary files
* 🔄 Auto-refresh dashboard
* 🔐 Unique token-based upload system
* 🧹 Auto cleanup of old files (24 hours)

---

## 🛠 Tech Stack

* **Backend:** Flask (Python)
* **Frontend:** HTML, Tailwind CSS
* **Desktop UI:** CustomTkinter
* **Packaging:** PyInstaller

---

## 📦 Installation & Usage

### ▶ Windows

1. Download the latest release:
   👉 [Download AirDrop App](../../releases/latest)

2. Run:

   ```bash
   AirDropApp.exe
   ```

3. A control panel will open

4. Click **RELAUNCH** to open the dashboard

5. Scan QR from mobile and upload files

---

### ▶ Linux

1. Download and extract the ZIP

2. Give permission:

   ```bash
   chmod +x app airdrop.sh
   ```

3. Run:

   ```bash
   ./airdrop.sh
   ```

---

## 📡 How It Works

```text
Run App
   ↓
Dashboard Opens
   ↓
Scan QR Code
   ↓
Upload Files from Mobile
   ↓
Manage Files on Dashboard
```

---

## 📌 Requirements

* All devices must be on the **same WiFi network**
* Modern web browser (Chrome recommended)

---

## 📁 Project Structure

```
AirDropApp/
│
├── app.py
├── icon.ico
│
├── static/
│   ├── icon.png
│   ├── qr.png
│
├── templates/
├── uploads/
│   ├── pending/
│   └── accepted/
```

---

## 🔧 Build (For Developers)

To create executable:

```bash
pyinstaller --onefile --noconsole \
--icon=icon.ico \
--add-data "templates;templates" \
--add-data "static;static" \
app.py
```

---

## ⚠ Notes

* Linux may not display custom app icons without `.desktop` configuration
* Windows provides full UI + icon support
* Files older than 24 hours are automatically deleted

---

## 👨‍💻 Author

**Tanmoy Giri**

---

## 🌟 Future Improvements

* Cloud file transfer
* Mobile app version
* Drag & drop dashboard uploads
* User authentication system

---

## 📜 License

This project is for educational and personal use.

---

## ⭐ Support

If you like this project, consider giving it a ⭐ on GitHub!
