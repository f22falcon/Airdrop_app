from flask import Flask, render_template, request, redirect
import os

app = Flask(__name__)

# folders
UPLOAD_FOLDER = "uploads/pending"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return redirect('/upload?token=TEST123')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    token = request.args.get('token')

    # safety check
    if not token:
        return "Token missing "

    if request.method == 'POST':
        files = request.files.getlist("files")

        for file in files:
            if file.filename == "":
                continue

            filename = f"{token}_{file.filename}"
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        return "OK"

    return render_template("upload.html", token=token)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)