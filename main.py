from flask import Flask, request, jsonify, render_template
import requests
import base64

app = Flask(__name__)

# Replace with the Django server's API URLs
API_BASE_URL = "https://0d87-2409-4085-40c-c63d-6515-b4bd-9e36-bf3.ngrok-free.app/api"
POSTMASTER_URL = f"{API_BASE_URL}/postmaster/"
SURVEILLANCE_VIDEO_URL = f"{API_BASE_URL}/surveillance/"
FEEDBACK_URL = f"{API_BASE_URL}/feedback/"
PARCEL_IMAGE_URL = f"{API_BASE_URL}/parcel-image/"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form_postmaster')
def form_postmaster():
    return render_template('form_postmaster.html')

@app.route('/form_video')
def form_video():
    return render_template('form_video.html')

@app.route('/form_feedback')
def form_feedback():
    return render_template('form_feedback.html')

@app.route('/form_parcel_image')
def form_parcel_image():
    return render_template('form_parcel_image.html')

@app.route('/submit_postmaster', methods=['POST'])
def submit_postmaster():
    data = {
        "name": request.form['name'],
        "address": request.form['address'],
        "postal_code": request.form['postal_code']
    }

    response = requests.post(POSTMASTER_URL, json=data)
    return jsonify(response.json()), response.status_code

@app.route('/submit_video', methods=['POST'])
def submit_video():
    video_file = request.files['video']
    video_base64 = base64.b64encode(video_file.read()).decode('utf-8')
    video_data = f"data:video/{video_file.filename.split('.')[-1]};base64,{video_base64}"

    data = {
        "camera_name": request.form['camera_name'],
        "latitude": request.form['latitude'],
        "longitude": request.form['longitude'],
        "video": video_data
    }

    response = requests.post(SURVEILLANCE_VIDEO_URL, json=data)
    return jsonify(response.json()), response.status_code

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    photo_file = request.files.get('photo')
    photo_data = None

    if photo_file:
        photo_base64 = base64.b64encode(photo_file.read()).decode('utf-8')
        photo_data = f"data:image/{photo_file.filename.split('.')[-1]};base64,{photo_base64}"

    data = {
        "name": request.form['name'],
        "tracking_id": request.form['tracking_id'],
        "feedback": request.form['feedback'],
        "email": request.form['email'],
        "address": request.form['address'],
        "photos": photo_data
    }

    response = requests.post(FEEDBACK_URL, json=data)
    return jsonify(response.json()), response.status_code

@app.route('/submit_parcel_image', methods=['POST'])
def submit_parcel_image():
    image_file = request.files['image']
    image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    image_data = f"data:image/{image_file.filename.split('.')[-1]};base64,{image_base64}"

    data = {
        "article_number": request.form['article_number'],
        "date_of_registration": request.form['date_of_registration'],
        "serial_number": request.form['serial_number'],
        "image": image_data
    }

    response = requests.post(PARCEL_IMAGE_URL, json=data)
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
