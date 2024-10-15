import cv2
import pytesseract
import numpy as np
import os
import time
from picamera2 import Picamera2

# Define officer plates
officer_plates = ["CTN1111", "CTN202"]
output_directory = "detected_plates"
os.makedirs(output_directory, exist_ok=True)

# Dictionary to store detected plates and prevent duplicates
detected_plates = {}

# Initialize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

def pre_process_image(image):
    """Convert the image to grayscale and apply pre-processing."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 30, 200)
    return edged

def detect_plate_contour(edged, original_image):
    """Detect license plate contour."""
    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)
        if len(approx) == 4:
            return approx  # Return the plate contour
    return None

def save_image_with_text(cropped_image, plate_text, status):
    """Save the cropped image with status text below."""
    global detected_plates

    # Check if this plate has already been saved
    if plate_text in detected_plates:
        return  # Avoid duplicate saves
    
    # Add plate to the detected list
    detected_plates[plate_text] = True

    # Ensure the image has 3 channels (convert RGBA to RGB if necessary)
    if cropped_image.shape[2] == 4:
        cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGRA2BGR)

    # Add extra space below the image to insert text (reduce the extra height)
    height, width, _ = cropped_image.shape
    new_image = np.zeros((height + 30, width, 3), dtype=np.uint8)  # Adjusted to 30 pixels for text
    new_image[0:height, 0:width] = cropped_image  # Place the cropped image on top

    # Add the status text below the image, outside the main area
    cv2.putText(new_image, f"Status: {status}", (10, height + 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)  # Adjust the position for the text
    
    # Save the image
    timestamp = int(time.time())
    output_path = os.path.join(output_directory, f"plate_{plate_text}_{status}_{timestamp}.jpg")
    cv2.imwrite(output_path, new_image)


def perform_ocr(cropped_image):
    """Perform OCR and determine plate status."""
    
    # Threshold the image for better OCR accuracy
    _, thresh_cropped = cv2.threshold(cropped_image, 128, 255, cv2.THRESH_BINARY)
    
    # Run OCR
    text = pytesseract.image_to_string(thresh_cropped, config='--psm 8').strip()
    text = ''.join(filter(str.isalnum, text))  # Keep only alphanumeric characters

    if 6 <= len(text) <= 7:
        # Check if it's an officer or outsider
        status = "Staff" if text in officer_plates else "Outsider"
        print(f"Detected Plate: {text} | Status: {status}")

        # Save the cropped image with the plate number and status
        save_image_with_text(cropped_image, text, status)

def process_frame(frame):
    """Process each frame for license plate detection and OCR."""
    edged = pre_process_image(frame)
    plate_contour = detect_plate_contour(edged, frame)
    
    if plate_contour is not None:
        cv2.drawContours(frame, [plate_contour], -1, (0, 255, 0), 3)
        
        mask = np.zeros(edged.shape, np.uint8)
        new_image = cv2.drawContours(mask, [plate_contour], 0, 255, -1)
        new_image = cv2.bitwise_and(frame, frame, mask=mask)
        
        # Now crop the plate area
        (x, y) = np.where(mask == 255)
        (topx, topy) = (np.min(x), np.min(y))
        (bottomx, bottomy) = (np.max(x), np.max(y))
        cropped_image = frame[topx:bottomx+1, topy:bottomy+1]

        # Perform OCR on the cropped license plate area
        perform_ocr(cropped_image)

frame_count = 0

# Main loop to capture frames and process
while True:
    frame = picam2.capture_array()

    # Process every 3rd frame for license plate detection
    if frame_count % 3 == 0:
        process_frame(frame)

    cv2.imshow("Camera Preview", frame)
    frame_count += 1

    # Break the loop with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
