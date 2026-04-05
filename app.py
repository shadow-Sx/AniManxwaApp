import os
import json
import base64
from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
CORS(app)

# Mega.nz login
MEGA_EMAIL = os.getenv('MEGA_EMAIL')
MEGA_PASSWORD = os.getenv('MEGA_PASSWORD')

# ==================== MANGA DATABASE (TEST) ====================
# Keyin Mega.nz dan o'qishga o'tkazamiz
MANGA_DB = {
    'solo-leveling': {
        'title': 'Solo Leveling',
        'author': 'Chugong',
        'type': 'bepul',
        'cover': '/cover/solo-leveling',
        'chapters': 179,
        'pages': {
            1: ['/page/solo-leveling/1/1', '/page/solo-leveling/1/2']
        }
    }
}

# ==================== MANGA O'QISH ENDPOINTS ====================

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

@app.route('/cover/<manga_id>', methods=['GET'])
def get_cover(manga_id):
    """Manga muqovasini olish"""
    # Test rasm (keyin Mega.nz dan olinadi)
    return jsonify({'url': f'/static/placeholder.jpg'})

@app.route('/page/<manga_id>/<int:chapter>/<int:page>', methods=['GET'])
def get_page(manga_id, chapter, page):
    """Sahifani olish"""
    return jsonify({'url': f'/static/placeholder.jpg'})

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

# ==================== MANGA YUKLASH ENDPOINT ====================

@app.route('/upload', methods=['POST'])
def upload_manga():
    """Telefondan manga yuklash (Mega.nz ga)"""
    try:
        data = request.json
        
        manga_id = data.get('manga_id')
        title = data.get('title')
        author = data.get('author')
        manga_type = data.get('type')
        cover_base64 = data.get('cover')
        chapters = data.get('chapters', [])
        
        if not all([manga_id, title, author, cover_base64]):
            return jsonify({'success': False, 'error': 'Ma\'lumotlar to\'liq emas'}), 400
        
        # 1. Mega.nz ga ulanish
        try:
            from mega import Mega
            mega = Mega()
            m = mega.login(MEGA_EMAIL, MEGA_PASSWORD)
        except Exception as e:
            return jsonify({'success': False, 'error': f'Mega login: {str(e)}'}), 500
        
        # 2. Papka yaratish
        try:
            # Mangas papkasini topish yoki yaratish
            root = m.get_files()
            mangas_folder = None
            for node in root:
                if root[node]['t'] == 1 and root[node]['n'] == 'Mangas':
                    mangas_folder = node
                    break
            
            if not mangas_folder:
                mangas_folder = m.create_folder('Mangas')
            
            # Manga papkasini yaratish
            manga_folder = m.create_folder(title, mangas_folder)
        except Exception as e:
            return jsonify({'success': False, 'error': f'Papka yaratish: {str(e)}'}), 500
        
        # 3. info.json yuklash
        info = {
            'title': title,
            'author': author,
            'type': manga_type,
            'cover': 'cover.jpg',
            'chapters': len(chapters),
            'uploadedAt': str(__import__('datetime').datetime.now())
        }
        info_json = json.dumps(info, indent=2)
        m.upload_data(info_json.encode(), manga_folder, 'info.json')
        
        # 4. Muqova yuklash
        if cover_base64.startswith('data:image'):
            cover_base64 = cover_base64.split(',')[1]
        cover_data = base64.b64decode(cover_base64)
        m.upload_data(cover_data, manga_folder, 'cover.jpg')
        
        # 5. Boblarni yuklash
        for chapter in chapters:
            chapter_num = chapter.get('number')
            pages = chapter.get('pages', [])
            
            if not chapter_num or not pages:
                continue
            
            chapter_name = f'bob_{chapter_num:03d}'
            chapter_folder = m.create_folder(chapter_name, manga_folder)
            
            for i, page_base64 in enumerate(pages):
                if page_base64.startswith('data:image'):
                    page_base64 = page_base64.split(',')[1]
                page_data = base64.b64decode(page_base64)
                page_name = f'{i+1:03d}.png'
                m.upload_data(page_data, chapter_folder, page_name)
        
        # 6. MANGA_DB ni yangilash
        MANGA_DB[manga_id] = {
            'title': title,
            'author': author,
            'type': manga_type,
            'cover': f'/cover/{manga_id}',
            'chapters': len(chapters),
            'pages': {}
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
