import os
import httpx
from fastapi import FastAPI, Depends
# ESTA É A CORREÇÃO PARA O ERRO "NameError: name 'BaseModel' is not defined"
from pydantic import BaseModel
from sqlalchemy.orm import Session

# ESTAS SÃO AS CORREÇÕES PARA O ERRO "ImportError"
import models
import database

# Esta linha usa as correções do "ImportError"
models.Base.metadata.create_all(bind=database.engine)

# --- Pydantic Models (Estrutura de Dados) ---
# Esta linha usa a correção do "NameError"
class FormSubmission(BaseModel):
    name: str
    email: str
    message: str

# --- FastAPI App ---
app = FastAPI()

# --- Funções de Dependência ---
# Esta função usa as correções do "ImportError"
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints da API ---
AI_ENGINE_URL = os.getenv("AI_ENGINE_URL")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "formrelay"}

@app.post("/submit/{form_id}")
def submit_form(form_id: str, submission: FormSubmission, db: Session = Depends(get_db)):
    print(f"Recebida submissão para o formulário ID: {form_id}")
    
    ai_analysis = {}
    try:
        response = httpx.post(f"{AI_ENGINE_URL}/analyze", json={"text": submission.message}, timeout=10.0)
        response.raise_for_status()
        ai_analysis = response.json()
        print("Análise da IA recebida com sucesso.")
    except httpx.RequestError as exc:
        print(f"ERRO: Falha ao comunicar com o Motor de IA: {exc}")

    # Esta linha usa as correções do "ImportError"
    new_submission = models.Submission(
        form_id=form_id,
        name=submission.name,
        email=submission.email,
        message=submission.message,
        ai_analysis=ai_analysis
    )
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    print(f"Submissão salva no banco de dados com ID: {new_submission.id}")

    return {
        "status": "success",
        "message": "Formulário recebido e salvo com sucesso!",
        "submission_id": new_submission.id
    }