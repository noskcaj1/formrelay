import os
import httpx
from fastapi import FastAPI, Depends
# IMPORTAÇÃO ADICIONAL para o CORS
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
import database

models.Base.metadata.create_all(bind=database.engine)

class FormSubmission(BaseModel):
    name: str
    email: str
    message: str

app = FastAPI()

# --- CONFIGURAÇÃO DO CORS (O PORTEIRO) ---
# Lista de "endereços" que têm permissão para falar com a nossa API.
# O asterisco "*" significa "qualquer um", o que é ótimo para um serviço público como o nosso.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos (GET, POST, etc)
    allow_headers=["*"], # Permite todos os cabeçalhos
)
# --- FIM DA CONFIGURAÇÃO DO CORS ---

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

AI_ENGINE_URL = os.getenv("AI_ENGINE_URL")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "formrelay"}

@app.post("/submit/{form_id}")
def submit_form(form_id: str, submission: FormSubmission, db: Session = Depends(get_db)):
    # O resto do código permanece exatamente o mesmo...
    print(f"Recebida submissão para o formulário ID: {form_id}")
    ai_analysis = {}
    try:
        response = httpx.post(f"{AI_ENGINE_URL}/analyze", json={"text": submission.message}, timeout=10.0)
        response.raise_for_status()
        ai_analysis = response.json()
        print("Análise da IA recebida com sucesso.")
    except httpx.RequestError as exc:
        print(f"ERRO: Falha ao comunicar com o Motor de IA: {exc}")

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