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
    print(f"Iniciando análise via API externa para: '{message_text}'")

    try:
        # 1. Análise de Sentimento
        sentiment_model = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
        sentiment_payload = {"inputs": message_text}
        sentiment_result = query_hf_api(sentiment_payload, HF_API_URL + sentiment_model)
        sentiment_label = sentiment_result[0][0]['label'].upper()

        # 2. Classificação de Tópico
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
            "summary": "Sumarização via API a ser implementada.",
            "entities": {}
        }
        print("Análise via API externa concluída.")
        return analysis_result

    except Exception as e:
        print(f"ERRO ao chamar a API da Hugging Face: {e}")
        return {"error": f"Falha ao processar a análise de IA: {e}"}