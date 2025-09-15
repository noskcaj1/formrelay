import os
import httpx
from fastapi import FastAPI
from pydantic import BaseModel

# --- CONFIGURAÇÃO DA API HUGGING FACE ---
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

class AnalysisRequest(BaseModel):
    text: str

app = FastAPI()

# Função auxiliar para chamar a API da Hugging Face
def query_hf_api(payload, model_url):
    response = httpx.post(model_url, headers=HEADERS, json=payload, timeout=20.0)
    response.raise_for_status() # Lança um erro se a API falhar
    return response.json()

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-engine-v2-api"}

@app.post("/analyze")
def analyze_text(request: AnalysisRequest):
    message_text = request.text
    print(f"Iniciando análise de alta precisão para: '{message_text}'")

    try:
        # 1. Análise de Sentimento com o modelo BERTimbau
        sentiment_model = "ruanchaves/bert-large-portuguese-cased-sentiment-analysis"
        sentiment_payload = {"inputs": message_text}
        sentiment_result = query_hf_api(sentiment_payload, HF_API_URL + sentiment_model)

        # --- Lógica de Tradução para o novo modelo ---
        raw_label = sentiment_result[0][0]['label'] # Ex: '5 stars'
        score = sentiment_result[0][0]['score']
        sentiment_label = "NEUTRAL" # Padrão
        if '5 stars' in raw_label or '4 stars' in raw_label:
            sentiment_label = "POSITIVE"
        elif '1 star' in raw_label or '2 stars' in raw_label:
            sentiment_label = "NEGATIVE"
        # --- Fim da Lógica de Tradução ---

        # 2. Classificação de Tópico (mantemos o modelo flexível)
        classifier_model = "facebook/bart-large-mnli"
        classifier_payload = {
            "inputs": message_text,
            "parameters": {"candidate_labels": ["suporte técnico", "venda", "feedback geral"]},
        }
        classifier_result = query_hf_api(classifier_payload, HF_API_URL + classifier_model)
        category_label = classifier_result['labels'][0]

        analysis_result = {
            "text_received": message_text,
            "category": category_label,
            "sentiment": sentiment_label,
            "details": {
                "raw_sentiment_label": raw_label,
                "sentiment_score": score
            }
        }
        print("Análise de alta precisão concluída.")
        return analysis_result

    except Exception as e:
        print(f"ERRO ao chamar a API da Hugging Face: {e}")
        return {"error": f"Falha ao processar a análise de IA: {e}"}