import os
import mega
from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Mega.nz ga ulanish
mega_client = mega.Mega()
m = mega_client.login(os.getenv('MEGA_EMAIL'), os.getenv('MEGA_PASSWORD'))

@app.route('/mangas', methods=['GET'])
def get_mangas():
    """Barcha mangalar ro'yxatini olish"""
    try:
        mangas_folder = m.find('Mangas')
        if not mangas_folder:
            return jsonify([])
        
        mangas = []
        for folder in mangas_folder.children:
            if folder.is_dir:
                info_file = folder.find('info.json')
                if info_file:
                    info = m.download(info_file)
                    import json
                    with open(info, 'r') as f:
                        data = json.load(f)
                    mangas.append({
                        'id': folder.name,
                        'title': data.get('title'),
                        'author': data.get('author'),
                        'type': data.get('type'),
                        'cover': f'/cover/{folder.name}',
                        'chapters': data.get('chapters', 0)
                    })
        return jsonify(mangas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cover/<manga_id>', methods=['GET'])
def get_cover(manga_id):
    """Manga muqovasini olish"""
    try:
        manga = m.find(f'Mangas/{manga_id}')
        cover = manga.find('cover.jpg')
        if not cover:
            cover = manga.find('cover.png')
        file_path = m.download(cover)
        return send_file(file_path, mimetype='image/jpeg')
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/page/<manga_id>/<path:page_path>', methods=['GET'])
def get_page(manga_id, page_path):
    """Sahifani olish (jild/bob/rasm)"""
    try:
        full_path = f'Mangas/{manga_id}/{page_path}'
        file = m.find(full_path)
        file_path = m.download(file)
        return send_file(file_path, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/chapters/<manga_id>', methods=['GET'])
def get_chapters(manga_id):
    """Manga boblari ro'yxatini olish"""
    try:
        manga = m.find(f'Mangas/{manga_id}')
        chapters = []
        
        # Jild va boblarni qidirish
        for item in manga.children:
            if item.is_dir:
                if item.name.startswith('jild_'):
                    # Jild ichidagi boblarni olish
                    for subitem in item.children:
                        if subitem.is_dir and subitem.name.startswith('bob_'):
                            chapters.append({
                                'volume': item.name,
                                'chapter': subitem.name,
                                'number': int(subitem.name.split('_')[1]),
                                'pages': len(subitem.children)
                            })
                elif item.name.startswith('bob_'):
                    chapters.append({
                                'volume': None,
                                'chapter': item.name,
                                'number': int(item.name.split('_')[1]),
                                'pages': len(item.children)
                            })
        
        chapters.sort(key=lambda x: x['number'])
        return jsonify(chapters)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)