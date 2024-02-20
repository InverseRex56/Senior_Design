import time
import socket
import threading
import json
import requests
import cv2
import datetime
import base64
import subprocess
from flask import Flask, request, jsonify

ip_address = None
app = Flask(__name__)

def get_ip_address():
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Connect to a known server (Google's DNS server)
        s.connect(("8.8.8.8", 80))

        # Get the socket's own address (IP and port)
        ip_address = s.getsockname()[0]

        return ip_address
    except socket.error:
        return None


def capture_image():
    # Initialize USB webcam
    cap = cv2.VideoCapture(0)
    
    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise Exception("Could not open webcam")
    
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    # Release the webcam
    cap.release()
    
    # Check if the frame is captured successfully
    if not ret:
        raise Exception("Could not capture frame")
    
    return frame

# Function to convert image to Base64 byte array
def image_to_byte_array(image):
    _, jpeg = cv2.imencode('.jpg', image)
    return base64.b64encode(jpeg.tobytes()).decode('utf-8')

@app.route('/get_picture', methods=['GET', 'POST'])
def get_picture():
    ip_address = get_ip_address()
    print(f"IP address: {ip_address}")
    try:
        # Capture image using OpenCV
        image = capture_image()
        
        # Get current datetime
        dt = datetime.datetime.now()
        
        # Convert image to Base64 byte array
        picture_base64 = image_to_byte_array(image)
        
        # Create JSON response
        response_data = {
            "ip": ip_address,
            "time": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "picture": picture_base64
        }
        
        return jsonify(response_data)
    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/init', methods=['GET', 'POST'])
def init():
    # ip_address = get_ip_address()
    remote_server_url = "http://network:8080/client_init"
    
    try:
        # Sending IP address to remote server
        response = requests.post(remote_server_url, json={'ip': ip_address})
        if response.ok:
            return 'IP address sent successfully to remote server.'
        else:
            return 'Failed to send IP address to remote server.', 500
    except Exception as e:
        return f'Error: {str(e)}', 500

network_url = 'http://network:8080' 

@app.route('/update_and_send', methods=['GET'])
def update_and_send_data():
    try:
        with open("config.json", "r") as config_file:
            data_to_send = json.load(config_file)
            response = requests.post(network_url, json=data_to_send)
            return response.text
    except FileNotFoundError:
        return "Config file not found."
    except json.JSONDecodeError:
        return "Error reading the JSON config file."
    

@app.route('/send_status', methods=['GET'])
def send_status():
    cam_status_url = network_url + '/send_status'
    try:
        with open("config.json", "r") as config_file:
            data = json.load(config_file)['status']
            response = requests.post(cam_status_url, json=data)
            return response.text
    except FileNotFoundError:
        return "Config file not found."
    except json.JSONDecodeError:
        return "Error reading the JSON config file."
    

@app.route('/send_event', methods=['GET'])
def send_event():
    cam_event_url = network_url + '/send_event'
    try:
        with open("config.json", "r") as config_file:
            data = json.load(config_file)['event']
            response = requests.post(cam_event_url, json=data)
            return response.text
    except FileNotFoundError:
        return "Config file not found."
    except json.JSONDecodeError:
        return "Error reading the JSON config file."


@app.route('/test', methods=['GET'])
def test():
    return 'test\n'

if __name__ == "__main__":
    ip_address = get_ip_address()

    flask_thread = threading.Thread(target=app.run, kwargs={'host':'0.0.0.0', 'port':8081})
    flask_thread.start()

    init()

