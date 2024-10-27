import os
from flask import Flask, render_template, request, redirect, url_for,send_file
from PyPDF2 import PdfReader,PdfWriter
from werkzeug.utils import secure_filename
import fitz

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
OUTPUT_FOLDER = 'output/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'],filename)
        file.save(filepath)
        return redirect(url_for('edit_pdf', filename=filename))
    return redirect(request.url)

@app.route('/edit/<filename>', methods=['GET','POST'])
def edit_pdf(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if request.method == 'POST':
        edited_text = request.form.get('content')
        output_filename = f"editted_{filename}"
        output_filepath = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        pdf_document = fitz.open()
        page = pdf_document.new_page()
        
        # Define font size and initial text position
        font_size = 12
        text_position = (72, 72)  # Starting position
        max_width = page.rect.width - 72 * 2  # Allow 72px margin on both sides
        avg_char_width = font_size * 0.6  # Estimate width of a character (adjust if necessary)
        
        # Split the content into lines that fit within page width
        for line in edited_text.splitlines():
            while line:
                # Calculate max number of characters that can fit within max_width
                max_chars_per_line = int(max_width / avg_char_width)
                # If line fits within max width, print it; otherwise split it
                if len(line) <= max_chars_per_line:
                    page.insert_text(text_position, line, fontsize=font_size)
                    text_position = (text_position[0], text_position[1] + font_size + 5)
                    line = ""
                else:
                    # Insert the portion that fits and continue with the rest
                    page.insert_text(text_position, line[:max_chars_per_line], fontsize=font_size)
                    text_position = (text_position[0], text_position[1] + font_size + 5)
                    line = line[max_chars_per_line:]
                
                # Start a new page if text overflows
                if text_position[1] > page.rect.height - 72:
                    page = pdf_document.new_page()
                    text_position = (72, 72)
        
        pdf_document.save(output_filepath)
        pdf_document.close()
        
        return send_file(output_filepath, as_attachment=True)

    text_content = """"""
    with fitz.open(filepath) as pdf_document:
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text_content += page.get_text() + "\n"
            
    return render_template('edit.html', content=text_content, filename=filename)
    
if __name__ == '__main__':
    app.run(debug=True)
    

