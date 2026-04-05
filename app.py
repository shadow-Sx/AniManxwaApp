import os
import json
from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
import requests
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

# Mega.nz public linklarni shu yerga qo'shing
# Format: 'manga_id': {'cover': 'link', 'pages': ['link1', 'link2', ...]}
MANGA_DB = {
    'solo-leveling': {
        'title': 'Solo Leveling',
        'author': 'Chugong',
        'type': 'bepul',
        'cover': 'https://mega.nz/embed/XXXXX#YYYYY',  # Public link
        'chapters': 179,
        'pages': {
            1: ['https://mega.nz/embed/XXXXX#YYYYY']  # 1-bob sahifalari
        }
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
            'cover': f'/cover/{manga_id}',
            'chapters': data['chapters']
        })
    return jsonify(mangas)

@app.route('/cover/<manga_id>', methods=['GET'])
def get_cover(manga_id):
    """Manga muqovasini olish"""
    if manga_id in MANGA_DB and 'cover' in MANGA_DB[manga_id]:
        # Redirect to Mega.nz public link
        return jsonify({'url': MANGA_DB[manga_id]['cover']})
    return jsonify({'error': 'Cover not found'}), 404

@app.route('/page/<manga_id>/<int:chapter>/<int:page>', methods=['GET'])
def get_page(manga_id, chapter, page):
    """Sahifani olish"""
    if manga_id in MANGA_DB and 'pages' in MANGA_DB[manga_id]:
        pages = MANGA_DB[manga_id]['pages']
        if chapter in pages and page <= len(pages[chapter]):
            return jsonify({'url': pages[chapter][page-1]})
    return jsonify({'error': 'Page not found'}), 404

@app.route('/chapters/<manga_id>', methods=['GET'])
def get_chapters(manga_id):
    """Manga boblari ro'yxatini olish"""
    if manga_id in MANGA_DB and 'pages' in MANGA_DB[manga_id]:
        chapters = []
        for chapter_num, pages in MANGA_DB[manga_id]['pages'].items():
            chapters.append({
                'volume': None,
                'chapter': f'bob_{chapter_num:03d}',
                'number': chapter_num,
                'pages': len(pages)
            })
        return jsonify(chapters)
    return jsonify([])

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
