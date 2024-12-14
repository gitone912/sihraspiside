import tkinter as tk
from tkinter import messagebox
import cv2
import threading
import time
import requests
import base64
import os

# Global variables
initial_data_url = "https://7e41-115-248-83-146.ngrok-free.app/api/postmaster/"
surveillance_url = "https://7e41-115-248-83-146.ngrok-free.app/api/surveillance/"
data = {}
recording = False
initial_data_submitted = False

# Function to send video to API
def send_video(video_path):
    try:
        with open(video_path, "rb") as video_file:
            video_base64 = base64.b64encode(video_file.read()).decode("utf-8")
            video_data = f"data:video/mp4;base64,{video_base64}"

        payload = {
            "camera_name": data["name"],
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "video": video_data
        }

        response = requests.post(surveillance_url, json=payload)
        print(f"Video sent. Response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending video: {e}")

# Function to record video

import subprocess

def record_with_ffmpeg(output_path, duration=15, resolution=(640, 480), fps=20):
    """
    Records video using FFmpeg directly via subprocess.

    Args:
        output_path (str): The path where the output video file will be saved.
        duration (int): Duration of the video in seconds. Default is 15 seconds.
        resolution (tuple): The resolution of the video as (width, height). Default is (640, 480).
        fps (int): Frames per second for the recorded video. Default is 20 fps.

    Returns:
        bool: True if recording was successful, False otherwise.
    """
    try:
        # FFmpeg command to capture video from the default camera
        command = [
            "ffmpeg", "-y",  # Overwrite output file if it exists
            "-f", "v4l2",  # Linux: Video4Linux2 as the input device
            "-framerate", str(fps),  # Frames per second
            "-video_size", f"{resolution[0]}x{resolution[1]}",  # Resolution
            "-i", "/dev/video0",  # Input device (Linux default camera)
            "-t", str(duration),  # Duration in seconds
            "-vcodec", "libx264",  # Video codec for MP4 output
            "-preset", "ultrafast",  # Encoding preset (speed vs. compression)
            output_path
        ]

        # Run the FFmpeg command
        subprocess.run(command, check=True)
        print(f"Video successfully recorded to {output_path}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg recording failed: {e}")
        return False

    except Exception as e:
        print(f"Unexpected error during FFmpeg recording: {e}")
        return False


def record_video():
    global recording
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Camera not accessible")
        return

    try:
        # Get camera resolution
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Camera Resolution: {frame_width}x{frame_height}")

        # Test different codecs if VideoWriter fails
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter("output.mp4", fourcc, 20.0, (frame_width, frame_height))

        if not out.isOpened():
            print("Error: VideoWriter not initialized. Testing alternative codecs...")
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter('test_output.avi', cv2.VideoWriter_fourcc(*'XVID'), 20.0, (frame_width, frame_height))
        if not out.isOpened():
            print("VideoWriter failed. Trying FFmpeg as a fallback...")
            if not record_with_ffmpeg("output_ffmpeg.mp4", duration=15, resolution=(frame_width, frame_height), fps=20):
                print("FFmpeg recording also failed. Aborting...")
                return
            else:
                send_video("output_ffmpeg.mp4")
                if os.path.exists("output_ffmpeg.mp4"):
                    os.remove("output_ffmpeg.mp4")
            return


        if not out.isOpened():
            print("Error: VideoWriter failed to initialize with all tested codecs.")
            return

        print("VideoWriter initialized successfully.")
        start_time = time.time()
        frames_written = 0

        while recording and time.time() - start_time < 15:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
                frames_written += 1
            else:
                print("Error: Failed to capture frame")
                break

        out.release()

        if frames_written > 0:
            print(f"{frames_written} frames written to output.mp4")
            send_video("output.mp4")
            if os.path.exists("output.mp4"):
                os.remove("output.mp4")
        else:
            print("No frames captured; skipping video upload")

    except Exception as e:
        print(f"Error during video recording: {e}")
    finally:
        cap.release()

# Function to start monitoring
def start_monitoring():
    global recording
    recording = True
    monitor_label.config(text="Monitoring: Working", fg="green")  # Ensure monitor_label is global
    threading.Thread(target=record_video).start()
    
# Function to submit initial user data to API
def submit_initial_data():
    global data, initial_data_submitted
    name = name_entry.get()
    latitude = lat_entry.get()
    longitude = long_entry.get()
    pincode = pincode_entry.get()
    address = address_entry.get()

    if not (name and latitude and longitude and pincode and address):
        messagebox.showerror("Error", "All fields are required")
        return

    data = {
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "pincode": pincode,
        "address": address
    }

    try:
        response = requests.post(initial_data_url, json=data)
        if response.status_code == 201:
            response_json = response.json()
            if "message" in response_json and response_json["message"] == "Data saved successfully!":
                messagebox.showinfo("Success", "Initial data submitted successfully")
                initial_data_submitted = True
                root.destroy()
                main_app()
            else:
                messagebox.showerror("Error", f"Unexpected response: {response_json}")
        else:
            messagebox.showerror("Error", f"Failed to submit initial data: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"Error submitting initial data: {e}")

# Function to check if initial data is submitted
def check_initial_data():
    if initial_data_submitted:
        root.destroy()
        main_app()
    else:
        root.deiconify()

# Main surveillance app GUI
def main_app():
    global monitor_label  # Declare it as global so it can be accessed in start_monitoring
    main_root = tk.Tk()
    main_root.title("Raspberry Pi Surveillance App")

    # Start button
    start_button = tk.Button(main_root, text="Start Monitoring", state=tk.NORMAL, command=start_monitoring)
    start_button.pack(pady=20)

    # Monitoring label
    monitor_label = tk.Label(main_root, text="Monitoring: Not Started", fg="red")
    monitor_label.pack(pady=10)

    main_root.mainloop()

# Tkinter GUI for initial data submission
root = tk.Tk()
root.title("Initial Data Submission")

# User input fields
fields = ["Name", "Latitude", "Longitude", "Pincode", "Address"]
entries = {}

for idx, field in enumerate(fields):
    label = tk.Label(root, text=field)
    label.grid(row=idx, column=0, padx=10, pady=5)
    entry = tk.Entry(root)
    entry.grid(row=idx, column=1, padx=10, pady=5)
    entries[field.lower()] = entry

name_entry = entries["name"]
lat_entry = entries["latitude"]
long_entry = entries["longitude"]
pincode_entry = entries["pincode"]
address_entry = entries["address"]

# Submit button
submit_button = tk.Button(root, text="Submit", command=submit_initial_data)
submit_button.grid(row=len(fields), column=0, columnspan=2, pady=10)

# Check if initial data is already submitted
check_initial_data()
root.mainloop()
