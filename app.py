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

# Ma'lumotlar bazasi (vaqtincha)
MANGA_DB = {}

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
        
        # Ma'lumotlarni saqlash
        MANGA_DB[manga_id] = {
            'title': data['title'],
            'author': data['author'],
            'type': data['type'],
            'cover': data['cover'],
            'chapters': len(data['chapters'])
        }
        
        return jsonify({'success': True, 'message': 'Manga yuklandi!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
