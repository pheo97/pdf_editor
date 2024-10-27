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
        for line in edited_text.splitlines():
            page = pdf_document.new_page()
            page.insert_text((72,72), line, fontsize=12)
        
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
    

