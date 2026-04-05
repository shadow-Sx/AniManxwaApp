const express = require('express');
const cors = require('cors');
const Mega = require('megajs');
const multer = require('multer');
require('dotenv').config();

const app = express();
const upload = multer({ dest: 'uploads/' });

app.use(cors());
app.use(express.json());

let mega = null;

async function connectMega() {
  try {
    console.log('🔌 Mega.nz ga ulanish...');
    console.log('Email:', process.env.MEGA_EMAIL ? '✅ Bor' : '❌ Yo‘q');
    console.log('Password:', process.env.MEGA_PASSWORD ? '✅ Bor' : '❌ Yo‘q');

    mega = new Mega({
      email: process.env.MEGA_EMAIL,
      password: process.env.MEGA_PASSWORD
    });
    await mega.login();
    console.log('✅ Mega.nz ga ulandi');
  } catch (err) {
    console.error('❌ Mega ulanish xatosi:', err.message);
    process.exit(1);
  }
}

app.get('/mangas', async (req, res) => {
  try {
    if (!mega) {
      return res.status(503).json({ error: 'Mega ulanishi tayyor emas' });
    }
    const root = await mega.root;
    const mangasFolder = root.children.find(f => f.name === 'Mangas');
    if (!mangasFolder) return res.json([]);
    
    const mangas = [];
    for (const folder of mangasFolder.children) {
      if (folder.directory) {
        const infoFile = folder.children.find(f => f.name === 'info.json');
        if (infoFile) {
          const buffer = await infoFile.downloadBuffer();
          const info = JSON.parse(buffer.toString());
          mangas.push({
            id: folder.name,
            title: info.title,
            author: info.author,
            type: info.type,
            cover: `/cover/${folder.name}`,
            chapters: info.chapters
          });
        }
      }
    }
    res.json(mangas);
  } catch (err) {
    console.error('/mangas xatosi:', err);
    res.status(500).json({ error: err.message });
  }
});

app.get('/cover/:mangaId', async (req, res) => {
  try {
    if (!mega) {
      return res.status(503).json({ error: 'Mega ulanishi tayyor emas' });
    }
    const root = await mega.root;
    const manga = root.children.find(f => f.name === 'Mangas').children.find(f => f.name === req.params.mangaId);
    const cover = manga.children.find(f => f.name === 'cover.jpg');
    if (cover) {
      const buffer = await cover.downloadBuffer();
      res.set('Content-Type', 'image/jpeg');
      res.send(buffer);
    } else {
      res.status(404).send('Cover not found');
    }
  } catch (err) {
    console.error('/cover xatosi:', err);
    res.status(404).send('Cover not found');
  }
});

connectMega().then(() => {
  const port = process.env.PORT || 5000;
  app.listen(port, () => {
    console.log(`🚀 Server running on port ${port}`);
  });
});
