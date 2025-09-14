from fastapi import FastAPI
from pydantic import BaseModel
# Importa a ferramenta mais importante da biblioteca "transformers"
from transformers import pipeline

# --- CARREGANDO OS MODELOS DE IA (A MÁGICA ACONTECE AQUI) ---
# Isso é feito apenas uma vez, quando a aplicação inicia, para ser rápido.
print("Carregando modelo de análise de sentimento...")
# Usamos um modelo treinado para análise de sentimento em múltiplas línguas.
sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-xlm-roberta-base-sentiment-v2")
print("Modelo de sentimento carregado.")

print("Carregando modelo de classificação de tópico...")
# Usamos um modelo de "Zero-Shot Classification", que pode classificar textos
# em categorias que ele nunca viu antes, é extremamente flexível.
classifier_pipeline = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
print("Modelo de classificação carregado.")
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
    print(f"Iniciando análise para o texto: '{message_text}'")

    # --- EXECUTANDO A ANÁLISE REAL ---

    # 1. Análise de Sentimento
    sentiment_result = sentiment_pipeline(message_text)
    # O resultado é uma lista, então pegamos o primeiro item. Ex: {'label': 'negative', 'score': 0.8}
    sentiment_label = sentiment_result[0]['label'].upper() # ex: NEGATIVE

    # 2. Classificação de Tópico
    candidate_labels = ["suporte técnico", "venda", "feedback geral"]
    classifier_result = classifier_pipeline(message_text, candidate_labels)
    # O resultado vem ordenado por pontuação, pegamos o primeiro. Ex: {'sequence': '...', 'labels': ['suporte técnico', ...], 'scores': [0.9, ...]}
    category_label = classifier_result['labels'][0] # ex: suporte técnico

    # --- Montando a resposta final ---
    analysis_result = {
        "text_received": message_text,
        "category": category_label,
        "sentiment": sentiment_label,
        "details": {
            "sentiment_details": sentiment_result,
            "category_details": {
                "labels": classifier_result['labels'],
                "scores": classifier_result['scores']
            }
        }
    }

    print(f"Análise concluída.")
    return analysis_result