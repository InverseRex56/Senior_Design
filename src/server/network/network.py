import json
import os
import base64
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/db'
# ip_address=os.environ.get("IP_ADDRESS", "127.0.0.1")
# sql_address = f"postgresql://postgres:postgres:@{ip_address}:5432/db"
# app.config['SQLALCHEMY_DATABASE_URI'] = sql_address
CORS(app)
db = SQLAlchemy(app)


class Camera(db.Model):
    __tablename__ = 'Camera'

    cam_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ip = db.Column(db.String(100))

    def __init__(self, ip):
        self.ip = ip

    def jsonify(self):
       return {"cam_id": self.cam_id, "ip": self.ip}
    

class Event(db.Model):
    __tablename__ = 'Image'
    id = db.Column(db.Integer)
    ip =  db.Column(db.String(100))
    time = db.Column(db.String(100), primary_key=True)
    pic = db.Column(db.String(10000000))
    
    def __init__(self, id, ip, time, pic):
        self.id = id
        self.ip = ip
        self.time = time
        self.pic = pic

    def jsonify(self):
        return {"id": self.id, "ip": self.ip, "time": self.time, "pic": self.pic}


@app.route('/client_init_handle', methods=['GET', 'POST'])
def client_init_handle():
    try:
        data = request.get_json()
        ip = data['ip']

        # checks if there is an already existing client with the same ip address
        existing_cam = Camera.query.filter_by(ip=ip).first()
        if existing_cam:
            return jsonify({'message': 'Camera with this IP already exists.'}), 404
        
        cam = Camera(ip)
        db.session.add(cam)
        db.session.commit()
        print(f"ip is {ip}")
        return cam.jsonify()
    except Exception as e: 
        print(f"Exception: {e}")
        return jsonify({'message': f"{e}"}), 400

@app.route('/get_ip/<int:cam_id>', methods=['GET', 'POST'])
def get_ip_from_id(cam_id):
    try:
        # Query the Camera table for the IP address corresponding to the given cam_id
        camera = Camera.query.filter_by(cam_id=cam_id).first()
        
        # If a Camera instance with the given cam_id exists, return its IP address
        if camera:
            return jsonify({'ip': camera.ip}), 200
        else:
            return jsonify({'error': f"No camera found with the provided id {cam_id}"}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_id/<string:ip>', methods=['GET'])
def get_id(ip):
    try:
        # Query the Camera table to find the cam_id associated with the given IP address
        camera = Camera.query.filter_by(ip=ip).first()

        if camera:
            return jsonify({'cam_id': camera.cam_id})
        else:
            return jsonify({'error': f'No camera found with the provided IP address {ip}'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/n_sec_pic_handle', methods=['POST', 'GET'])
def n_sec_pic_handle():
    try:
        data = request.get_json()

        # extract json elements
        ip = data.get('ip')
        time = data.get('time')
        picture = data.get('picture')
        request_ip = f"http://network:8080/get_id/{ip}"
        response = requests.post(request_ip)
        if response.status_code == 200:
            id = response.json()['id']
        elif response.status_code == 404:
            return jsonify({'message': 'Error occured'}), 404

        # Convert the time string to a datetime object
        time_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        time_only = time_obj.time()

        # Decode the base64-encoded image data
        img_data = base64.b64decode(picture)

        # Save the image data to a file in the uploadPictures folder
        with open(f"uploadPictures/{time_only}_{ip}.jpg", "wb") as img_file:
            img_file.write(img_data)

        # Save into events data
        image = Event(id, ip, time, picture)
        db.session.add(image)  
        db.session.commit()
       
        return jsonify({'message': f'event occured sucesfully'})
    except ValueError:
        return jsonify({'message': 'Error occured'}), 404

@app.route('/ui_capture/<int:cam_id>', methods=['POST'])
def ui_capture(cam_id):

    request_ip = f"http://network:8080/get_ip/{cam_id}"
    try:
        response = requests.post(request_ip)
        client_ip = response.json()['ip']
        client_url = "http://" + str(client_ip) + ":8081/ui_capture_handle"

        response = requests.post(client_url)

        if response.status_code == 200:
            data = response.json()

            ip = data['ip']
            time = data['time']
            pic = data['picture']
            request_ip = f"http://network:8080/get_id/{ip}"
            response = requests.post(request_ip)
            if response.status_code == 200:
                id = response.json()['id']
            elif response.status_code == 404:
                return jsonify({'message': 'Error occured'}), 404

            # Convert the time string to a datetime object
            time_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            time_only = time_obj.time()
    
            # Decode the base64-encoded image data
            img_data = base64.b64decode(pic)

            # Save the image data to a file in the uploadPictures folder
            with open(f"ui_capture/{time_only}_{ip}.jpg", "wb") as img_file:
                img_file.write(img_data)
        
            # Create an instance of the img class with the extracted data
            image = Event(id, ip, time, pic)
    
            # Add the image to the database session
            db.session.add(image)
            db.session.commit()
    
            return 'Image uploaded successfully\n'
    except ValueError:
        return jsonify({'message': 'Error occured'}), 404
    
    
@app.route('/get_img_for_cam/<string:ip>', methods=['POST'])
def get_img_for_cam(ip):
    data_db = Event.query.filter_by(ip=ip).order_by(Event.time.desc()).first()
    data_list = []

    # if data_db:
    #     data_list = data_db.pic
    # return jsonify(data_list)

    if data_db:
        data_list = [{
            'pic': data_db.pic,
            'time': data_db.time
        }]
    return jsonify({'data': data_list})
    

#get image from volume then saving raw image to database
# primary key is ip
# time
@app.route('/upload_image', methods=['GET'])
def upload_image():
    image = Image(path=f'/app/uploadPictures/cam1.webp')
    db.session.add(image)
    db.session.commit()
    return 'Image uploaded successfully'

@app.route('/test', methods=['POST', 'GET'])
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