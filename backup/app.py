from flask import Flask, render_template, request, redirect, url_for
from db import init_db, add_image, get_images
from werkzeug.utils import secure_filename
import os
import random
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def light_random_color():
    """Generate a random light color."""
    return tuple(random.randint(200, 255) for _ in range(3))

def generate_image_from_message(name, message):
    # Font settings
    font_path = "arialbd.ttf"
    font_size = 50
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    full_message = f"{name}: {message}"
    
    # Create a dummy image to get text size
    dummy_image = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(dummy_image)
    
    # Calculate text size using textbbox
    bbox = draw.textbbox((0, 0), full_message, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Ensure the width is within limits
    min_width, max_width = 400, 800
    width = min(max(text_width + 20, min_width), max_width)
    height = text_height + 20

    # Create the actual image with calculated size
    background_color = light_random_color()
    text_color = (0, 0, 0)  # Use black for text
    image = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(image)

    # Calculate text position
    text_x = (width - text_width) / 2
    text_y = (height - text_height) / 2
    
    draw.text((text_x, text_y), full_message, fill=text_color, font=font)
    
    # Generate a unique filename
    unique_filename = f"message_image_{random.randint(1000, 9999)}.jpg"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    image.save(output_path)
    return unique_filename


@app.route('/')
def index():
    images = get_images()
    return render_template('index.html', images=images)

@app.route('/contribute')
def contribute():
    return render_template('contribute.html')

@app.route('/upload', methods=['POST'])
def upload():
    name = request.form['name']
    message = request.form['message']
    image_file = request.files.get('image')

    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(file_path)
        image_src = filename
    else:
        image_src = generate_image_from_message(name, message)

    add_image(image_src, name, message)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
