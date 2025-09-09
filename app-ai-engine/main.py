from fastapi import FastAPI
# Pydantic nos ajuda a definir a estrutura dos dados que esperamos receber
from pydantic import BaseModel

# Define que o request para /analyze deve ter um campo "text" do tipo string
class AnalysisRequest(BaseModel):
    text: str

# Cria a instância da nossa aplicação
app = FastAPI()

# Endpoint para verificar a saúde do serviço (já tínhamos)
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-engine"}

# NOVO ENDPOINT: para analisar o texto
# @app.post diz que este endpoint aceita requisições do tipo POST
@app.post("/analyze")
def analyze_text(request: AnalysisRequest):
    # --- A MÁGICA DA IA (FAKE POR ENQUANTO) ---
    # No futuro, aqui teremos o código de Machine Learning.
    # Por agora, vamos apenas devolver uma resposta fixa para testar.

    message_text = request.text

    analysis_result = {
        "text_received": message_text,
        "category": "Suporte Técnico",
        "sentiment": "Negativo",
        "entities": {
            "product": "Não identificado",
            "order_id": "Não identificado"
        },
        "summary": "Resumo gerado pela IA..."
    }

    print(f"Análise gerada para o texto: '{message_text}'")
    return analysis_result