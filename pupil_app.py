from flask import Flask, render_template, request
import os
import cv2
import numpy as np

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('pupil.html')

def calculate_pupil_size(image_path, pixel_to_mm_conversion_factor):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        print("Error: Unable to load the image. Please check the file path.")
        return None

    blurred_image = cv2.GaussianBlur(image, (7, 7), 0)

    circles = cv2.HoughCircles(blurred_image, cv2.HOUGH_GRADIENT, dp=1.2, minDist=100,
                               param1=50, param2=30, minRadius=10, maxRadius=50)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")

        for (x, y, r) in circles:
            pupil_size_mm = r * pixel_to_mm_conversion_factor

            cv2.circle(image, (x, y), r, (255, 255, 255), 2)
            cv2.circle(image, (x, y), 2, (255, 255, 255), 3)

            print(f"Pupil size: {pupil_size_mm:.2f} mm")

            if pupil_size_mm < 2.5:
                print("Warning: The person may be abusing opioids (pupil size < 2.5 mm).")

            return pupil_size_mm
    else:
        print("Pupil not detected.")
        return None

@app.route('/predict', methods=['POST'])
def predict():
    try:
        imagefile = request.files['imagefile']
        image_path = os.path.join("./data", imagefile.filename)
        imagefile.save(image_path)

        print(f"Image saved at: {image_path}")

        pixel_to_mm_conversion_factor = 0.1  

        pupil_size_mm = calculate_pupil_size(image_path, pixel_to_mm_conversion_factor)

        if pupil_size_mm is not None:
            prediction_message = f"Pupil size: {pupil_size_mm:.2f} mm"
            if pupil_size_mm < 2.5:
                prediction_message += " - Warning: The person may be abusing opioids (pupil size < 2.5 mm)."
        else:
            prediction_message = "Pupil not detected."

        return render_template('pupil.html', pred=prediction_message)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return render_template('pupil.html', pred="An error occurred during processing. Please try again.")

if __name__ == '__main__':
    app.run(port=3000, debug=True)
