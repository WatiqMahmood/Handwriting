from flask import Flask, render_template, request, send_from_directory
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import io
import base64
import time
import os

# Flask app setup
app = Flask(__name__)

# Create a lookup table with style numbers and corresponding font paths
font_lookup = {
    1: r"templates\Caveat-Bold.ttf",
    2: r"templates\Caveat-Regular.ttf",
    3: r"templates\CoveredByYourGrace.ttf",
    4: r"templates\JustMeAgainDownHere.ttf",
    5: r"templates\PatrickHand-Regular.ttf",
    6: r"templates\RockSalt.ttf",
    7: r"templates\Schoolbell.ttf",
    8: r"templates\ShadowsIntoLight.ttf"
}

# Set the directory for saving images
UPLOAD_FOLDER = 'ResultsImg'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Home route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        style_number = int(request.form['style'])
        speed = float(request.form['speed'])
        stroke_width = int(request.form['stroke_width'])
        # Legibility: It's affecting the contrast of the text (more legible = darker text)
        legibility = float(request.form['legibility'])

        font = get_font(style_number)

        # Create the handwriting image with the applied stroke width, speed, and legibility
        img = generate_handwriting_image(text, font, stroke_width, speed, legibility)

        # Save the image to the server
        image_filename = f"generated_image_{time.time()}.png"
        img_path = os.path.join(UPLOAD_FOLDER, image_filename)
        img.save(img_path)

        # Convert the image to base64 so it can be displayed in the HTML
        img_b64 = img_to_base64(img)

        return render_template('index.html', img_b64=img_b64, text=text, style_number=style_number, speed=speed, stroke_width=stroke_width, legibility=legibility, image_filename=image_filename)

    return render_template('index.html')

# Get font based on style number
def get_font(style_number):
    try:
        return ImageFont.truetype(font_lookup[style_number], size=48)
    except:
        return ImageFont.load_default()

# Generate handwriting image based on options (stroke width, speed, legibility)
def generate_handwriting_image(text, font, stroke_width, speed, legibility):
    img_width = max(600, len(text) * 30)
    img = Image.new("L", (img_width, 120), color=255)
    draw = ImageDraw.Draw(img)

    # Adjust legibility (contrast) by modifying the fill color
    fill_color = int(255 * (1 - legibility))  # More legibility = darker text
    fill_color = max(0, min(fill_color, 255))  # Ensure the color is within bounds

    # Draw text with the specified stroke width
    for i in range(1, len(text) + 1):
        partial_img = img.copy()
        partial_draw = ImageDraw.Draw(partial_img)
        partial_draw.text((10, 20), text[:i], font=font, fill=fill_color, stroke_width=stroke_width)

        # Simulate speed by adding a delay
        time.sleep(speed)

        if i == len(text):  # Last frame
            return partial_img

    return img

# Convert image to base64 string for embedding in HTML
def img_to_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_b64

# Route to download the generated image
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Run the app locally on port 5000
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
