import os
import json
import base64
import urllib.parse
import io
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
CORS(app)

# Mega.nz API (public link yaratish uchun)
MEGA_EMAIL = os.getenv('MEGA_EMAIL')
MEGA_PASSWORD = os.getenv('MEGA_PASSWORD')

# Ma'lumotlar bazasi
MANGA_DB = {
    'solo-leveling': {
        'title': 'Solo Leveling',
        'author': 'Chugong',
        'type': 'bepul',
        'cover': 'https://mega.nz/embed/uK5mXYAK#aLtTAa30aJUxtYcB5EszmB2pk3i_rR2yVaHQRjfrD_s',
        'chapters': 179
    }
}

@app.route('/mangas', methods=['GET'])
def get_mangas():
    """Barcha mangalar ro'yxatini olish"""
    mangas = []
    for manga_id, data in MANGA_DB.items():
        mangas.append({
            'id': manga_id,
            'title': data['title'],
            'author': data['author'],
            'type': data['type'],
            'cover': data['cover'],
            'chapters': data['chapters']
        })
    return jsonify(mangas)

@app.route('/image/<path:url>', methods=['GET'])
def get_image(url):
    """Mega.nz dan rasmni qaytarish"""
    try:
        decoded_url = urllib.parse.unquote(url)
        response = requests.get(decoded_url)
        return send_file(
            io.BytesIO(response.content),
            mimetype='image/png'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/upload', methods=['POST'])
def upload_manga():
    """Yangi manga yuklash"""
    try:
        data = request.json
        manga_id = data['manga_id']
        
        MANGA_DB[manga_id] = {
            'title': data['title'],
            'author': data['author'],
            'type': data['type'],
            'cover': data.get('cover', 'https://via.placeholder.com/200x300'),
            'chapters': len(data.get('chapters', []))
        }
        
        return jsonify({'success': True, 'message': 'Manga yuklandi!', 'manga_id': manga_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/chapters/<manga_id>', methods=['GET'])
def get_chapters(manga_id):
    """Manga boblari ro'yxatini olish"""
    if manga_id in MANGA_DB:
        chapters = []
        for i in range(1, MANGA_DB[manga_id]['chapters'] + 1):
            chapters.append({
                'number': i,
                'pages': 30  # Test uchun
            })
        return jsonify(chapters)
    return jsonify([])

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
