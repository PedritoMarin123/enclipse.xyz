from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
import uuid

app = Flask(__name__)

# Ruta de almacenamiento de archivos
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Extensiones permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Página principal con formulario
@app.route('/')
def index():
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Subir Imagen</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 50px;
                text-align: center;
            }
            form {
                margin-top: 20px;
            }
            input[type="file"] {
                margin: 10px 0;
            }
            button {
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                cursor: pointer;
                font-size: 16px;
            }
            #link {
                margin-top: 20px;
                font-size: 18px;
                color: blue;
            }
        </style>
    </head>
    <body>
        <h1>Subir Imagen</h1>
        <form id="uploadForm" method="POST" enctype="multipart/form-data" action="/upload">
            <input type="file" name="file" accept="image/*" required>
            <br>
            <button type="submit">Subir</button>
        </form>
        <div id="link"></div>

        <script>
            const form = document.getElementById('uploadForm');
            form.onsubmit = async (e) => {
                e.preventDefault();
                const formData = new FormData(form);
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                const linkDiv = document.getElementById('link');
                if (result.url) {
                    linkDiv.innerHTML = `✅ Enlace generado: <a href="${result.url}" target="_blank">${result.url}</a>`;
                } else {
                    linkDiv.textContent = `❌ Error: ${result.error}`;
                }
            };
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_content)

# Endpoint para subir archivos
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se encontró el archivo'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Guardar el archivo
            file.save(file_path)
            
            # Generar URL para el archivo
            file_url = f"http://127.0.0.1:5000/file/{unique_filename}"
            return jsonify({'url': file_url})
        
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint para servir archivos
@app.route('/file/<filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
