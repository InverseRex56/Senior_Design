import json
import os
import base64
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/db'
# ip_address=os.environ.get("IP_ADDRESS", "127.0.0.1")
# sql_address = f"postgresql://postgres:postgres:@{ip_address}:5432/db"
# app.config['SQLALCHEMY_DATABASE_URI'] = sql_address
CORS(app)
db = SQLAlchemy(app)


class Camera(db.Model):
    __tablename__ = 'Camera'

    cam_id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100))
    is_streaming = db.Column(db.Integer)
    
    def __init__(self, cam_id, ip, is_streaming):
        self.cam_id = cam_id
        self.ip = ip
        self.is_streaming = is_streaming

    def jsonify(self):
        return {"cam_id": self.cam_id, "ip": self.ip, "is_streaming" : self.is_streaming}

@app.route('/send_camera/<int:cam_id>/<string:ip>/<int:is_streaming>', methods=['POST'])
def send_camera(cam_id, ip, is_streaming):
    try:
        camera = Camera(cam_id, ip, is_streaming)
        db.session.add(camera)
        db.session.commit()
        return camera.jsonify()
    except Exception as e: 
        print(f"Exception: {e}")
        return jsonify({'message': f"{e}"}), 400


class Status(db.Model):
    __tablename__ = 'Status'

    cam_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer)
    most_recent_pic = db.Column(db.String(100))
    
    def __init__(self, cam_id, status, most_recent_pic):
        self.cam_id = cam_id
        self.status = status
        self.most_recent_pic = most_recent_pic

    def jsonify(self):
        return {"cam_id": self.cam_id, "status": self.status, "most_recent_pic": self.most_recent_pic}


@app.route('/send_status', methods = ['POST'])
def cam_status():
    data = request.get_json()
    status = Status(data['cam_id'], data['status'], data['most_recent_pic'])
    db.session.add(status)
    db.session.commit()
    return status.jsonify()

class Event(db.Model):
    __tablename__ = 'Event'

    cam_id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.Integer)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, cam_id, event):
        self.cam_id = cam_id
        self.event = event

    def jsonify(self):
        return {"cam_id": self.cam_id, "event": self.event, "sent_at": self.sent_at}

class Image(db.Model):
    __tablename__ = 'Image'

    # ip =  db.Column(db.String(100), primary_key=True)
    # time = db.Column(db.String(100))
    ip =  db.Column(db.String(100))
    time = db.Column(db.String(100), primary_key=True)
    pic = db.Column(db.String(10000000))
    
    def __init__(self, ip, time, pic):
        self.ip = ip
        self.time = time
        self.pic = pic

    def jsonify(self):
        return {"ip": self.ip, "time": self.time, "pic": self.pic}

# database scheme for Image table
# ip     |   time     |   path
# string |   Datetime |   string
    
# json data to be sent to /save_img_db
# { "ip": ip, "time": datetime, "payload": payload} 

# steps you must take to fully implement /save_img_db:
# 1. retreieve json data using data = request.get_json()
# 2. convert payload(bytearray) into a .jpg image and save it to the uploadPictures folder(note:pic name should be time_ip.jpg 10:10:10_192.168.1.1.jpg)
# 3. save the time, path, and ip to the database

@app.route('/save_img_db', methods=['POST'])
# Function to save image data to the database
def save_img_db():
    # request_ip = "http://localhost:8081/get_picture"
    request_ip = "http://client:8081/get_picture"
    response = requests.post(request_ip)


    if response.status_code == 200:
        data = response.json()

        ip = data['ip']
        time = data['time']
        pic = data['picture']

        # print("IP:", ip)
        # print("Time:", time)
        # print("Picture:", pic)

        # Convert the time string to a datetime object
        time_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    
        # Extract the time component from the datetime object
        time_only = time_obj.time()
    
        # Decode the base64-encoded image data
        img_data = base64.b64decode(pic)

        # Save the image data to a file in the uploadPictures folder
        with open(f"uploadPictures/{time_only}_{ip}.jpg", "wb") as img_file:
            img_file.write(img_data)
        
        # Create an instance of the img class with the extracted data
        image = Image(ip, time, pic)
    
        # Add the image to the database session
        db.session.add(image)
    
        # Commit the changes to the database
        db.session.commit()
    
        # Return a success message
        return 'Image uploaded successfully'

@app.route('/get_img_for_cam/<string:ip>', methods=['POST'])
def get_img_for_cam(ip):
    data_db = Image.query.filter_by(ip=ip).order_by(Image.time.desc()).first()
    data_list = []

    # test code to prove that the data is latest image from db displayed in terminal
    # in order to use this code, you must first run the /save_img_db endpoint
    # then open the uploadPictures folder and check the latest image and your ip
    # finally, use curl -X POST http://localhost:8080/get_img_for_cam/__your_ip__ to see the latest image

    # if data_db:
    #     data_list = [{
    #         'pic': data_db.pic,
    #         'time': data_db.time
    #     }]
    # return jsonify({'data': data_list})

    # this is the code that should be used for production. 
    # no extra brackets are printed, so johnny will get the json formatted btye string

    # if data_db:
    #     data_list = data_db.pic
    # return jsonify(data_list)
    
#get image from volume then saving raw image to database
# primary key is ip
# time
@app.route('/upload_image', methods=['GET'])
def upload_image():
    image = Image(path=f'/app/uploadPictures/cam1.webp')
    db.session.add(image)
    db.session.commit()
    return 'Image uploaded successfully'

@app.route('/send_event', methods = ['POST'])
def cam_events():
    data = request.get_json()
    event = Event(data['cam_id'], data['event'])
    db.session.add(event)
    db.session.commit()
    return event.jsonify()

@app.route('/get_status_data', methods=['GET'])
def get_status_data():
    data_db = Status.query.all()
    data_list = []

    for status in data_db:
        data_list.append({
            'cam_id': status.cam_id,
            'status': status.status,
            'most_recent_pic': status.most_recent_pic
        })

    return jsonify({'data': data_list})

@app.route('/get_event_data', methods=['GET'])
def get_event_data():
    data_db = Event.query.all()
    data_list = []

    for event in data_db:
        data_list.append({
            'cam_id': event.cam_id,
            'event': event.event,
            'sent_at': event.sent_at
        })

    return jsonify({'data': data_list})

@app.route('/replace_row_data_for_status/<int:cam_id>/<int:status>/<string:most_recent_pic>', methods=['POST'])
def replace_row_data_for_status(cam_id, status, most_recent_pic):
    # Replace the row in the database using the received data
    status_to_replace = Status.query.get(cam_id)
    
    if status_to_replace:
        status_to_replace.status = status
        status_to_replace.most_recent_pic = most_recent_pic
        db.session.commit()
        return status_to_replace.jsonify()

    return jsonify({'message': 'Row not found'}), 404
    
@app.route('/replace_row_data_for_events/<int:cam_id>/<int:event>/<string:sent_at>', methods=['POST'])
def replace_row_data_for_events(cam_id, event, sent_at):
    # Replace the row in the database using the received data
    event_to_replace = Event.query.get(cam_id)
    
    if event_to_replace:
        event_to_replace.event = event
        event_to_replace.sent_at = sent_at
        db.session.commit()
        return event_to_replace.jsonify()

    return jsonify({'message': 'Row not found'}), 404

@app.route('/delete_data_in_row_for_status/<int:cam_id>', methods=['POST'])
def delete_data_in_row_for_status(cam_id):
    try:
        status_to_delete = Status.query.get(cam_id)

        if status_to_delete:
            db.session.delete(status_to_delete)
            db.session.commit()
            return jsonify({'message': f'Row {cam_id} deleted successfully'})

        return jsonify({'message': 'Row not found'}), 404
    except ValueError:
        return jsonify({'message': 'Invalid cam_id value'}), 400

@app.route('/delete_data_in_row_for_events/<int:cam_id>', methods=['POST'])
def delete_data_in_row_for_events(cam_id):
    try:
        event_to_delete = Event.query.get(cam_id)

        if event_to_delete:
            db.session.delete(event_to_delete)
            db.session.commit()
            return jsonify({'message': f'Row {cam_id} deleted successfully'})

        return jsonify({'message': 'Row not found'}), 404
    except ValueError:
        return jsonify({'message': 'Invalid cam_id value'}), 400


# @app.route('/server_request/<int:cam_id>/<Command:cmd>', methods=['POST'])
# def server_request(cam_id, cmd):
#     cam_ip = db.get_ip(cam_id)
#     request_ip = cam_ip + '/request'
#     response = requests.post(request_ip, cmd)
#     return jsonify({'message': 'Row not found'}), 404

@app.route('/test')
def test():
    return 'this is a test'

if __name__ == "__main__":
    # print(f"this is the sql address: {sql_address}")
    try:
        with app.app_context():
            db.create_all()
            # db.session.add(Event(1,2))
            # db.session.add(Event(3,4))
            # db.session.add(Status(5,6, "SEVEN"))
            # db.session.add(Status(8,9, "TEN"))
            # db.session.add(Camera(0, "192.168.1.254", False))
            # db.session.add(Camera(1, "192.168.1.253", False))
            db.session.commit()
            app.run(host='0.0.0.0', port=8080, debug=True)
    except: 
        pass      # work around: db needs to be fully initialized before network can run
