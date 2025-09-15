from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# --- CARREGANDO O MODELO LOCALMENTE ---
print("Carregando modelo de análise de sentimento otimizado...")
# Este modelo é multilíngue, otimizado e leve.
model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
print("Modelo carregado com sucesso.")
# --- FIM DO CARREGAMENTO ---

class AnalysisRequest(BaseModel):
    text: str

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-engine-v3-local"}

@app.post("/analyze")
def analyze_text(request: AnalysisRequest):
    message_text = request.text
    print(f"Iniciando análise local para: '{message_text}'")
    try:
        # Análise de Sentimento com o modelo local
        sentiment_result = sentiment_pipeline(message_text)
        raw_label = sentiment_result[0]['label'] # Ex: '5 stars'

        # Lógica de tradução para POSITIVE, NEGATIVE, NEUTRAL
        sentiment_label = "NEUTRAL"
        if '5 stars' in raw_label or '4 stars' in raw_label:
            sentiment_label = "POSITIVE"
        elif '1 star' in raw_label or '2 stars' in raw_label:
            sentiment_label = "NEGATIVE"

        analysis_result = {
            "text_received": message_text,
            "category": "A ser implementado", # A classificação agora pode ser outro modelo leve
            "sentiment": sentiment_label,
            "details": { "raw_sentiment": sentiment_result }
        }
        print("Análise local concluída.")
        return analysis_result
    except Exception as e:
        print(f"ERRO durante a análise de IA local: {e}")
        return {"error": f"Falha ao processar a análise de IA: {e}"}