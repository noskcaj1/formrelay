# 1. Ponto de Partida: Usar uma imagem oficial e leve do Python
FROM python:3.11-slim

# 2. Preparar o Terreno: Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# 3. Trazer os Ingredientes: Copiar o arquivo de dependências
COPY requirements.txt .

# 4. Preparar a Massa: Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt


# 5. Trazer o Recheio: Copiar o resto do código da nossa aplicação
COPY . .

# 6. Ligar o Forno: Expor a porta 5000 para que possamos nos conectar
EXPOSE 5000

# 7. Servir o Prato: O comando que inicia a aplicação quando o contêiner roda
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]