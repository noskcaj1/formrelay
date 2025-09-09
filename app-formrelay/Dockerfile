# 1. Ponto de Partida
FROM python:3.11-slim

# 2. Preparar o Terreno
WORKDIR /app

# 3. Trazer os Ingredientes
COPY requirements.txt .

# 4. Preparar a Massa
RUN pip install --no-cache-dir -r requirements.txt

# 5. Trazer o Recheio
COPY . .

# 6. Ligar o Forno (porta diferente)
EXPOSE 8080

# 7. Servir o Prato (porta diferente)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]