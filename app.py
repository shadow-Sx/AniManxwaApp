import os
import json
import base64
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
CORS(app)

# Mega.nz API (public link yaratish uchun)
MEGA_EMAIL = os.getenv('MEGA_EMAIL')
MEGA_PASSWORD = os.getenv('MEGA_PASSWORD')

# Vaqtincha ma'lumotlar bazasi
MANGA_DB = {}

def create_mega_public_link(file_id):
    """Mega.nz da public link yaratish"""
    # Mega.nz API orqali public link yaratish
    # Hozircha test
    return f"https://mega.nz/embed/{file_id}"

@app.route('/mangas', methods=['GET'])
def get_mangas():
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

@app.route('/upload', methods=['POST'])
def upload_manga():
    try:
        data = request.json
        manga_id = data['manga_id']
        
        # Yuklangan rasmlarni saqlash
        # Mega.nz ga yuklash va public link olish
        
        # Test uchun placeholder link
        MANGA_DB = {
    'solo-leveling': {
        'title': 'Solo Leveling',
        'author': 'Chugong',
        'type': 'bepul',
        'cover': 'https://mega.nz/file/uK5mXYAK#aLtTAa30aJUxtYcB5EszmB2pk3i_rR2yVaHQRjfrD_s',  # cover link
        'chapters': 179,
        'pages': {
            1: [
                'https://mega.nz/file/iComSZQT#SbjDi-BxxOdrBas9J1zQM1PuiiGjHd4i2Y0kEuGIQ68',  # 001.png
                'https://mega.nz/file/LK4xBQCT#2paCYkJni7s3KyModH4BjxNcvwdnmvnlxbe9T16dsV0',  # 002.png
                # ... barcha sahifalar
            ]
        }
    }
}
        
        return jsonify({'success': True, 'message': 'Manga yuklandi!', 'cover': cover_link})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
