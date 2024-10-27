import os
from flask import Flask, render_template, request, redirect, url_for,send_file
from PyPDF2 import PdfReader,PdfWriter
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'pdf'}

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
        return redirect(url_for('process_pdf', filename=filename))
    return redirect(request.url)

@app.route('/process/<filename>')
def process_pdf(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    reader = PdfReader(filepath)
    writer = PdfWriter()
    
    for page_num in range(len(reader.pages)):
        writer.add_page(reader.pages[page_num])
        
        output_filename = f"{filename}_page_{page_num + 1}.pdf"
        output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        with open(output_filepath, "wb") as output_file:
            writer.write(output_file)
            
    return send_file(output_filepath, as_attachment=True)


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
    

