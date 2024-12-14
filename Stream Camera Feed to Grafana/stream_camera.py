import io
import time
from flask import Flask, Response
from picamera2 import Picamera2, Preview
import libcamera
from PIL import Image, ImageDraw, ImageFont
import datetime
import pytz

app = Flask(__name__)

# Initialize Picamera2 and apply rotation
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(main={"size": (2304, 1296)})
##preview_config["transform"] = libcamera.Transform(hflip=1, vflip=1)  # Rotate 180 degrees
#picam2.configure(preview_config)
picam2.start()

def generate_frames():
    # Path to a .ttf font file
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, size=30)  # Adjust the size as needed

    while True:
        frame = picam2.capture_array()
        img = Image.fromarray(frame).convert("RGB")
        
        # Add timestamp overlay with larger font
        draw = ImageDraw.Draw(img)
        local_timezone = pytz.timezone("Asia/Kuala_Lumpur")
        timestamp = datetime.datetime.now(local_timezone).strftime('%Y-%m-%d %H:%M:%S')
        draw.text((10, 10), f"Cam - {timestamp}", fill="green", font=font)
        
        # Convert to JPEG
        stream = io.BytesIO()
        img.save(stream, format="JPEG")
        stream.seek(0)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + stream.read() + b"\r\n")
        stream.close()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/')
def index():
    return "<html><body><h1>Raspberry Pi Camera Stream</h1><img src='/video_feed'></body></html>"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)

