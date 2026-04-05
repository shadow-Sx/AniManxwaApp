import os
import json
from flask import Flask, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from mega import Mega

load_dotenv()

app = Flask(__name__)
CORS(app)

# Mega.nz ga ulanish
mega = Mega()
m = mega.login(os.getenv('MEGA_EMAIL'), os.getenv('MEGA_PASSWORD'))

def get_manga_list():
    """Mega.nz dan mangalar ro'yxatini olish"""
    mangas = []
    mangas_folder = m.find('Mangas')
    
    if mangas_folder:
        for folder in mangas_folder.children:
            if folder.is_dir:
                info_file = folder.find('info.json')
                if info_file:
                    info = json.loads(m.download(info_file))
                    mangas.append({
                        'id': folder.name,
                        'title': info['title'],
                        'author': info['author'],
                        'type': info['type'],
                        'cover': f'/cover/{folder.name}',
                        'chapters': len([f for f in folder.children if f.is_dir and f.name.startswith('bob_')])
                    })
    return mangas

@app.route('/mangas', methods=['GET'])
def get_mangas():
    return jsonify(get_manga_list())

@app.route('/cover/<manga_id>', methods=['GET'])
def get_cover(manga_id):
    """Muqovani olish"""
    manga = m.find(f'Mangas/{manga_id}')
    cover = manga.find('cover.jpg') or manga.find('cover.png')
    if cover:
        return send_file(m.download(cover), mimetype='image/jpeg')
    return '', 404

@app.route('/page/<manga_id>/<path:page_path>', methods=['GET'])
def get_page(manga_id, page_path):
    """Sahifani olish (bob/rasm)"""
    full_path = f'Mangas/{manga_id}/{page_path}'
    file = m.find(full_path)
    if file:
        return send_file(m.download(file), mimetype='image/png')
    return '', 404

@app.route('/chapters/<manga_id>', methods=['GET'])
def get_chapters(manga_id):
    """Boblar ro'yxatini olish"""
    manga = m.find(f'Mangas/{manga_id}')
    chapters = []
    for folder in manga.children:
        if folder.is_dir and folder.name.startswith('bob_'):
            chapters.append({
                'number': int(folder.name.split('_')[1]),
                'pages': len(folder.children)
            })
    return jsonify(sorted(chapters, key=lambda x: x['number']))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
