Introduction 

This project involves building a License Plate Recognition System using Raspberry Pi 5, OpenCV, and Tesseract OCR. The system captures live video feed from a camera, detects vehicle license plates in real time, and uses Optical Character Recognition (OCR) to read the plate numbers. It classifies the detected plates into two categories: Staff or Outsider, based on a predefined list of officer plate numbers. The detected plates are saved with status labels for further processing or documentation. This project is ideal for parking management or office security systems.

Tutorial 

Required Libraries:
OpenCV: For image processing and contour detection.
sudo apt install python3-opencv

Remove Restrictions : to rename a file that restricts how Python packages are managed. While it allows you to use pip, be careful because it can cause conflicts with your system's package management.
sudo mv /usr/lib/python3.11/EXTERNALLY-MANAGED /usr/lib/python3.11/EXTERNALLY-MANAGED.old


Pytesseract: For Optical Character Recognition (OCR).
sudo apt install tesseract-ocr
pip3 install pytesseract


Picamera2: To interact with Raspberry Pi’s camera.
sudo apt install python3-picamera2


Numpy: For array manipulations.
pip3 install numpy
