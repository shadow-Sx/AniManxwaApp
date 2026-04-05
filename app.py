import os
import json
from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
CORS(app)

# Mega.nz login URL
MEGA_EMAIL = os.getenv('MEGA_EMAIL')
MEGA_PASSWORD = os.getenv('MEGA_PASSWORD')

# Mega.nz login funksiyasi
def mega_login():
    # megasdk kutubxonasi bilan ishlash
    # Hozircha public link orqali ishlaymiz
    pass

@app.route('/mangas', methods=['GET'])
def get_mangas():
    """Barcha mangalar ro'yxatini olish"""
    # Test ma'lumotlar
    test_mangas = [
        {
            'id': 'solo-leveling',
            'title': 'Solo Leveling',
            'author': 'Chugong',
            'type': 'bepul',
            'cover': '/cover/solo-leveling',
            'chapters': 179
        },
        {
            'id': 'naruto',
            'title': 'Naruto',
            'author': 'Masashi Kishimoto',
            'type': 'obuna',
            'cover': '/cover/naruto',
            'chapters': 700
        }
    ]
    return jsonify(test_mangas)

@app.route('/cover/<manga_id>', methods=['GET'])
def get_cover(manga_id):
    """Manga muqovasini olish"""
    # Test rasm
    return send_file('placeholder.jpg', mimetype='image/jpeg')

@app.route('/page/<manga_id>/<path:page_path>', methods=['GET'])
def get_page(manga_id, page_path):
    """Sahifani olish"""
    return send_file('placeholder.jpg', mimetype='image/jpeg')

@app.route('/chapters/<manga_id>', methods=['GET'])
def get_chapters(manga_id):
    """Manga boblari ro'yxatini olish"""
    test_chapters = [
        {'volume': None, 'chapter': 'bob_001', 'number': 1, 'pages': 30},
        {'volume': None, 'chapter': 'bob_002', 'number': 2, 'pages': 28}
    ]
    return jsonify(test_chapters)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
