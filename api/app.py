from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
import uuid

app = Flask(__name__)

# Carpeta de almacenamiento de archivos
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Extensiones permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Página HTML para subir archivos
@app.route('/')
def index():
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Subir Imagen</title>
    </head>
    <body>
        <h1>Subir Imagen</h1>
        <form id="uploadForm" method="POST" enctype="multipart/form-data" action="/upload">
            <input type="file" name="file" accept="image/*" required>
            <button type="submit">Subir</button>
        </form>
    </body>
    </html>
    '''
    return render_template_string(html_content)

# Endpoint para subida de archivos
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se encontró el archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        if file and allowed_file(file.filename):
            # Generar nombre único para el archivo
            ext = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Guardar archivo
            file.save(file_path)
            
            # Devolver URL del archivo
            file_url = f"http://127.0.0.1:5000/file/{unique_filename}"
            return jsonify({'url': file_url})
        
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint para servir los archivos
@app.route('/file/<filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
