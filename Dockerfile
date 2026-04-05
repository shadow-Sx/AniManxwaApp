# Python 3.11 versiyasini ishlatamiz
FROM python:3.11-slim

# Ishchi papkani belgilaymiz
WORKDIR /app

# Kerakli kutubxonalarni o‘rnatamiz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Barcha fayllarni nusxalaymiz
COPY . .

# Portni ochamiz
EXPOSE 10000

# Serverni ishga tushiramiz
CMD ["gunicorn", "app:app"]
