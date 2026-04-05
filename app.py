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

def create_mega_public_link(file_id):
    """Mega.nz da public link yaratish"""
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
        
        # Yangi mangani ma'lumotlar bazasiga qo'shish
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

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
