import spacy
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

# --- CARREGANDO OS MODELOS DE IA ---
# Isso pode levar um tempo na primeira inicialização do contêiner.
print("Carregando modelo de análise de sentimento...")
sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-xlm-roberta-base-sentiment-v2")
print("Modelo de sentimento carregado.")

print("Carregando modelo de classificação de tópico...")
classifier_pipeline = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
print("Modelo de classificação carregado.")

print("Carregando modelo de sumarização...")
# Usamos um modelo focado em sumarização de textos em português.
summarizer_pipeline = pipeline("summarization", model="csebuetnlp/mT5_multilingual_XLSum")
print("Modelo de sumarização carregado.")

print("Carregando modelo de reconhecimento de entidades (NER)...")
# Carregamos um modelo em português do Spacy. Ele é menor e mais rápido.
# A linha abaixo vai baixar o modelo na primeira vez que o Dockerfile for construído.
try:
    ner_model = spacy.load("pt_core_news_lg")
except OSError:
    print("Baixando modelo NER do Spacy...")
    spacy.cli.download("pt_core_news_lg")
    ner_model = spacy.load("pt_core_news_lg")
print("Modelo NER carregado.")
# --- MODELOS CARREGADOS ---

class AnalysisRequest(BaseModel):
    text: str

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-engine"}

@app.post("/analyze")
def analyze_text(request: AnalysisRequest):
    message_text = request.text
    print(f"Iniciando análise completa para o texto: '{message_text}'")

    # 1. Análise de Sentimento
    sentiment_result = sentiment_pipeline(message_text)
    sentiment_label = sentiment_result[0]['label'].upper()

    # 2. Classificação de Tópico
    candidate_labels = ["suporte técnico", "venda", "feedback geral"]
    classifier_result = classifier_pipeline(message_text, candidate_labels)
    category_label = classifier_result['labels'][0]

    # 3. Sumarização
    # O modelo espera textos um pouco mais longos, mas vamos usar mesmo assim.
    summary_result = summarizer_pipeline(message_text, max_length=50, min_length=5, do_sample=False)
    summary_text = summary_result[0]['summary_text']

    # 4. Extração de Entidades (NER - Named Entity Recognition)
    doc = ner_model(message_text)
    entities = {ent.label_: ent.text for ent in doc.ents} # Extrai entidades como { 'ORG': 'Apple', 'LOC': 'Brasil' }

    # --- Montando a resposta final ---
    analysis_result = {
        "text_received": message_text,
        "category": category_label,
        "sentiment": sentiment_label,
        "summary": summary_text,
        "entities": entities # Agora as entidades são reais!
    }

    print(f"Análise completa concluída.")
    return analysis_result