from flask import Flask, render_template, request, jsonify, Response
from database import get_connection, create_table
from werkzeug.utils import secure_filename
import os
import hashlib
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create table on startup (this will also create DB if missing)
create_table()

def file_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

@app.route("/")
def home():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_user():
    try:
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        enrollnumber = request.form.get("enrollnumber")
        dob = request.form.get("dob")
        mobile = request.form.get("mobile")
        gmail = request.form.get("gmail")
        address = request.form.get("address")
        qualification = request.form.get("qualification")

        # Validation
        if not all([firstname, lastname, enrollnumber, dob, mobile, gmail, address, qualification]):
            return jsonify({"status": "error", "message": "All fields are required!"})

        # Handle file uploads
        photo_file = request.files.get('photo')
        resume_file = request.files.get('resume')
        signature_file = request.files.get('signature')

        if not (photo_file and photo_file.filename and resume_file and resume_file.filename and signature_file and signature_file.filename):
            return jsonify({"status": "error", "message": "All files must be uploaded!"})

        photo_bytes = photo_file.read()
        resume_bytes = resume_file.read()
        signature_bytes = signature_file.read()

        photo_filename = secure_filename(photo_file.filename)
        resume_filename = secure_filename(resume_file.filename)
        signature_filename = secure_filename(signature_file.filename)

        resume_mimetype = resume_file.mimetype or "application/octet-stream"

        # Optionally save copies on disk (keeps DB as source of truth)
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        photo_disk = os.path.join(UPLOAD_FOLDER, f"{enrollnumber}_photo_{ts}_{photo_filename}")
        resume_disk = os.path.join(UPLOAD_FOLDER, f"{enrollnumber}_resume_{ts}_{resume_filename}")
        signature_disk = os.path.join(UPLOAD_FOLDER, f"{enrollnumber}_signature_{ts}_{signature_filename}")

        with open(photo_disk, "wb") as f:
            f.write(photo_bytes)
        with open(resume_disk, "wb") as f:
            f.write(resume_bytes)
        with open(signature_disk, "wb") as f:
            f.write(signature_bytes)

        # store in DB
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            sql = """INSERT INTO users
                     (firstname, lastname, enrollnumber, dob, mobile, gmail, address, qualification,
                      photo, photo_filename, resume, resume_filename, resume_mimetype,
                      signature, signature_filename, created_at)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                     ON DUPLICATE KEY UPDATE
                       firstname=VALUES(firstname),
                       lastname=VALUES(lastname),
                       dob=VALUES(dob),
                       mobile=VALUES(mobile),
                       gmail=VALUES(gmail),
                       address=VALUES(address),
                       qualification=VALUES(qualification),
                       photo=VALUES(photo),
                       photo_filename=VALUES(photo_filename),
                       resume=VALUES(resume),
                       resume_filename=VALUES(resume_filename),
                       resume_mimetype=VALUES(resume_mimetype),
                       signature=VALUES(signature),
                       signature_filename=VALUES(signature_filename),
                       updated_at=NOW()"""
            values = (firstname, lastname, enrollnumber, dob, mobile, gmail, address, qualification,
                      photo_bytes, photo_filename,
                      resume_bytes, resume_filename, resume_mimetype,
                      signature_bytes, signature_filename)
            cursor.execute(sql, values)
            conn.commit()
            return jsonify({"status": "success", "message": "Registration Successful!"})
        except Exception as err:
            return jsonify({"status": "error", "message": f"Database error: {err}"})
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/photo/<int:user_id>')
def display_photo(user_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT photo, photo_filename FROM users WHERE id=%s", (user_id,))
        row = cursor.fetchone()
        if not row or not row[0]:
            return ("No photo found", 404)
        blob, name = row[0], (row[1] or "photo")
        return Response(blob, mimetype="image/*", headers={"Content-Disposition": f"inline; filename={name}"})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/resume/<int:user_id>')
def download_resume(user_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT resume, resume_filename, resume_mimetype FROM users WHERE id=%s", (user_id,))
        row = cursor.fetchone()
        if not row or not row[0]:
            return ("No resume found", 404)
        blob, name, mimetype = row[0], (row[1] or "resume"), (row[2] or "application/octet-stream")
        return Response(blob, mimetype=mimetype, headers={"Content-Disposition": f"attachment; filename={name}"})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/signature/<int:user_id>')
def display_signature(user_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT signature, signature_filename FROM users WHERE id=%s", (user_id,))
        row = cursor.fetchone()
        if not row or not row[0]:
            return ("No signature found", 404)
        blob, name = row[0], (row[1] or "signature")
        return Response(blob, mimetype="image/*", headers={"Content-Disposition": f"inline; filename={name}"})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug=True)
