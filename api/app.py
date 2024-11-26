import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

# Crear carpeta de uploads si no existe
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Subir Imagen</title>
        <style>
            body { 
                font-family: Arial; 
                padding: 20px; 
                max-width: 600px; 
                margin: 0 auto; 
                text-align: center;
            }
            .upload-box { 
                border: 2px dashed #ccc; 
                padding: 20px; 
                margin: 20px 0;
            }
            #preview { 
                max-width: 300px; 
                margin-top: 10px; 
                max-height: 300px;
                object-fit: contain;
            }
            button { 
                margin: 10px; 
                padding: 10px 20px; 
                background: #4CAF50; 
                color: white; 
                border: none; 
                cursor: pointer; 
            }
            #result { 
                margin-top: 20px; 
                padding: 10px; 
                word-break: break-all;
            }
        </style>
    </head>
    <body>
        <div class="upload-box">
            <h2>📸 Subir Imagen</h2>
            <input type="file" id="fileInput" accept="image/*">
            <br>
            <img id="preview" style="display: none;">
            <br>
            <button onclick="uploadFile()">Subir</button>
        </div>
        <div id="result"></div>

        <script>
            document.getElementById('fileInput').onchange = function(e) {
                let preview = document.getElementById('preview');
                let file = e.target.files[0];
                
                if (file) {
                    let reader = new FileReader();
                    reader.onload = function(e) {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    }
                    reader.readAsDataURL(file);
                }
            };

            function uploadFile() {
                let fileInput = document.getElementById('fileInput');
                let file = fileInput.files[0];
                let resultDiv = document.getElementById('result');
                
                if (!file) {
                    resultDiv.innerHTML = '❌ Selecciona una imagen primero';
                    return;
                }

                let formData = new FormData();
                formData.append('file', file);

                fetch('/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.url) {
                        resultDiv.innerHTML = `✅ Imagen subida! <br>URL: <a href="${data.url}" target="_blank">${data.url}</a>`;
                    } else {
                        resultDiv.innerHTML = '❌ Error: ' + (data.error || 'Error desconocido');
                    }
                })
                .catch(error => {
                    resultDiv.innerHTML = '❌ Error al subir: ' + error;
                });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Verificar si hay archivo
        if 'file' not in request.files:
            return jsonify({'error': 'No hay archivo'})
        
        file = request.files['file']
        
        # Verificar si el nombre del archivo está vacío
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'})
        
        # Verificar extensión del archivo
        if file and allowed_file(file.filename):
            # Generar nombre único 
            ext = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{ext}"
            
            # Ruta completa donde guardar
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Guardar archivo
            file.save(file_path)
            
            # Devolver URL para acceder al archivo
            return jsonify({
                'url': f"/file/{unique_filename}",
                'filename': unique_filename
            })
        
        return jsonify({'error': 'Tipo de archivo no permitido'})
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/file/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    print(f"📁 Carpeta de uploads creada en: {os.path.abspath(UPLOAD_FOLDER)}")
    app.run(debug=True)
