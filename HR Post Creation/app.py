from flask import Flask, render_template, request, redirect
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def insert_image(background_path, overlay_path, output_path, transparency=0, margin_bottom=20):
    # Open the background and overlay images
    background = Image.open(background_path)
    overlay = Image.open(overlay_path)

    # Resize overlay image to fit the right-bottom portion
    overlay = overlay.resize((500, 700))  # You may adjust the size accordingly

    # Calculate the position for the right-bottom insertion with margin
    position = (background.width - overlay.width, background.height - overlay.height - margin_bottom)

    # Prepare the overlay image with transparency
    overlay = overlay.convert("RGBA")
    overlay_with_transparency = Image.new("RGBA", overlay.size)
    for x in range(overlay.width):
        for y in range(overlay.height):
            r, g, b, a = overlay.getpixel((x, y))
            overlay_with_transparency.putpixel((x, y), (r, g, b, int(a * transparency)))

    # Paste the overlay image onto the background
    background.paste(overlay_with_transparency, position, overlay_with_transparency)

    # Save the result
    background.save(output_path, "PNG")



def add_text(image_path, output_path, text_positions, text_styles):
    # Open the image
    image = Image.open(image_path)

    # Create a drawing object
    draw = ImageDraw.Draw(image)

    for (variable_name, position), (font_size, font_family, text_color, bold) in zip(text_positions, text_styles):
        # Load the specified font
        if bold:
            # Simulate boldness by using a larger font size
            font = ImageFont.truetype(font_family, font_size + 5)
        else:
            font = ImageFont.truetype(font_family, font_size)

        # Add text to the image using font parameters
        text = request.form.get(f"text_{variable_name.lower()}")
        draw.text(position, text, font=font, fill=text_color)

    # Save the result
    image.save(output_path)


@app.route('/')
def index():
    return render_template('upload_form.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files or 'overlay_image' not in request.files:
        return redirect(request.url)

    background_image = request.files['image']
    overlay_image = request.files['overlay_image']

    if background_image.filename == '' or overlay_image.filename == '' or not allowed_file(background_image.filename) or not allowed_file(overlay_image.filename):
        return redirect(request.url)

    # Save the uploaded background image
    background_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input_image.png')
    background_image.save(background_image_path)

    # Save the uploaded overlay image
    overlay_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'overlay_image.png')
    overlay_image.save(overlay_image_path)

    # Get user input for text and positions
    text_positions = [
        ('Designation', (100, 515)),
        ('Domain', (100, 580)),
        ('Department', (100, 615)),
        ('Date', (100, 870))
    ]

    # Define text styles (font size, font family, text color, bold) for each variable
    text_styles = [
        (30, 'RobotoSlab-VariableFont_wght.ttf', (0, 0, 0), True),    # Designation
        (20, 'Roboto-MediumItalic.ttf', (0, 0, 0), False),       # Domain
        (30, 'Roboto-Bold.ttf', (0,102,166), False),     # Department
        (20, 'Roboto-Bold.ttf', (0, 0, 0), True)       # Date
    ]

    # Generate a unique output filename based on the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_format = request.form.get('file_format')
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'result_image_{timestamp}.{file_format}')

    # Add text to the image with different font styles
    add_text(background_image_path, output_path, text_positions, text_styles)

    # Insert the overlay image
    insert_image(output_path, overlay_image_path, output_path, transparency=1.0, margin_bottom=65)

    return render_template('result.html', result_image=output_path)

if __name__ == '__main__':
    app.run(debug=True)
