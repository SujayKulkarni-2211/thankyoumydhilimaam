from flask import Flask, render_template, request, redirect, url_for, send_file, send_from_directory
from db import init_db, add_image, get_images
from werkzeug.utils import secure_filename
import os
import random
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from db import get_images


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def light_random_color():
    """Generate a random light color."""
    return tuple(random.randint(200, 255) for _ in range(3))

from PIL import Image as PILImage, ImageDraw, ImageFont

def generate_image_from_message(name, message):
    font_path = "Lobster/Lobster-Regular.ttf"
    font_size = 50
    margin = 40
    padding = 20

    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    full_message = f"{name}: {message}"
    
    # Create a dummy image to get text size
    dummy_image = PILImage.new('RGB', (1, 1))
    draw = ImageDraw.Draw(dummy_image)

    # Define maximum width for text wrapping
    max_width = 700  # Adjust as needed
    
    # Wrap text if it's too wide
    lines = []
    words = full_message.split()
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width - 2 * padding:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    # Measure total height of text
    total_text_height = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]
        total_text_height += line_height
    
    # Calculate width and height of the image
    text_width = max(draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0] for line in lines)
    width = min(max(text_width + 2 * margin, 400), 800)
    height = total_text_height + 2 * margin + 2 * padding  # Adding margin and padding

    # Create the image with calculated size
    background_color = light_random_color()
    text_color = (0, 0, 0)  # Use black for text
    image = PILImage.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(image)

    # Draw the text on the image
    y_position = margin + padding
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        text_x = (width - line_width) / 2
        draw.text((text_x, y_position), line, fill=text_color, font=font)
        y_position += bbox[3] - bbox[1] + padding  # Adding padding between lines

    # Generate a unique filename
    unique_filename = f"message_image_{random.randint(1000, 9999)}.jpg"
    output_path = os.path.join('static/uploads', unique_filename)
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


@app.route('/generate_pdf')
def generate_pdf():
    images = get_images()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    style = styles['BodyText']
    style.alignment = 1  # Center alignment

    margin = 50
    padding = 20

    for filename, name, message in images:
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Draw the image
        if os.path.exists(img_path):
            img = Image(img_path, width=400, height=200)
            img.hAlign = 'CENTER'
            elements.append(img)
            elements.append(Spacer(1, padding))  # Add space below the image
        
        # Draw the name
        name_paragraph = Paragraph(name, styles['Heading2'])
        name_paragraph.alignment = 1  # Center alignment
        elements.append(name_paragraph)
        elements.append(Spacer(1, padding))
        
        # Draw the message
        message_paragraph = Paragraph(message, style)
        elements.append(message_paragraph)
        elements.append(Spacer(1, 2 * padding))  # Add extra space between entries

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="gallery.pdf", mimetype='application/pdf')


def background():
    # Ensure the path to your GIF is correct
    return send_from_directory('static/images', 'shootingstar.gif')

