from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from PIL import Image
import io, os, uuid, zipfile

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'tiff'}

def allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/convert', methods=['POST'])
def convert():
    files = request.files.getlist('images')
    action = request.form.get('action', 'convert')
    fmt = request.form.get('format', 'webp').lower()
    quality = int(request.form.get('quality', 85))
    width = request.form.get('width', '')
    height = request.form.get('height', '')

    results = []

    for f in files:
        if not f or not allowed(f.filename):
            continue
        try:
            img = Image.open(f.stream).convert('RGBA')
            uid = str(uuid.uuid4())[:8]
            base = os.path.splitext(f.filename)[0]

            # --- Resize ---
            if width or height:
                w = int(width) if width else None
                h = int(height) if height else None
                orig_w, orig_h = img.size
                if w and not h:
                    h = int(orig_h * w / orig_w)
                elif h and not w:
                    w = int(orig_w * h / orig_h)
                img = img.resize((w, h), Image.LANCZOS)

            # --- Remove background ---
            if action == 'rembg':
                try:
                    from rembg import remove
                    buf = io.BytesIO()
                    img.save(buf, format='PNG')
                    buf.seek(0)
                    out_bytes = remove(buf.read())
                    img = Image.open(io.BytesIO(out_bytes)).convert('RGBA')
                    fmt = 'png'
                except Exception as e:
                    results.append({'error': f'rembg error: {str(e)}', 'name': f.filename})
                    continue

            # --- Save ---
            out_name = f"{base}_{uid}.{fmt}"
            out_path = os.path.join(OUTPUT_FOLDER, out_name)

            save_fmt = fmt.upper()
            if save_fmt == 'JPG': save_fmt = 'JPEG'

            if save_fmt in ('JPEG',):
                img = img.convert('RGB')
                img.save(out_path, format=save_fmt, quality=quality, optimize=True)
            elif save_fmt == 'WEBP':
                img.save(out_path, format='WEBP', quality=quality, method=6)
            elif save_fmt == 'PNG':
                img.save(out_path, format='PNG', optimize=True)
            else:
                img.save(out_path, format=save_fmt)

            size_kb = round(os.path.getsize(out_path) / 1024, 1)
            results.append({
                'name': out_name,
                'url': f'/static/outputs/{out_name}',
                'size': size_kb
            })
        except Exception as e:
            results.append({'error': str(e), 'name': f.filename})

    return jsonify(results)

@app.route('/api/download-zip', methods=['POST'])
def download_zip():
    files = request.json.get('files', [])
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        for fname in files:
            path = os.path.join(OUTPUT_FOLDER, fname)
            if os.path.exists(path):
                zf.write(path, fname)
    buf.seek(0)
    return send_file(buf, mimetype='application/zip',
                     as_attachment=True, download_name='converted_images.zip')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
