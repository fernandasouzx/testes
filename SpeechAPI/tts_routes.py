# tts_routes.py
# ---
# Rotas FastAPI para Text-to-Speech (TTS)
# Faz pré-processamento do texto, tenta sintetizar com ElevenLabs,
# e em caso de falha, faz fallback para OpenAI TTS.
# Arquivos de áudio são temporários e removidos após envio.
# ---

import os
import uuid
import requests
from pathlib import Path
from fastapi import APIRouter, Form, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from openai import OpenAI

# utils centraliza pré-processamento de texto
from utils.tts_preprocess import preprocess_text

# Importa autenticação
from api.auth import get_current_user

# --- Carrega variáveis de ambiente ---
load_dotenv()

API_KEY_ELEVENLABS = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")
API_KEY_OPENAI = os.getenv("OPENAI_API_KEY")

if not API_KEY_OPENAI:
    raise RuntimeError("OPENAI_API_KEY environment variable not set.")

# --- Inicializa cliente OpenAI ---
openai_client = OpenAI(api_key=API_KEY_OPENAI)

# --- Diretório temporário para arquivos TTS ---
TEMP_DIR = Path("tts/audios_tts")
TEMP_DIR.mkdir(parents=True, exist_ok=True)


def create_tts_routes() -> APIRouter:
    """
    Cria o roteador FastAPI com endpoint /tts.
    Workflow:
    1. Pré-processamento do texto
    2. Primeira tentativa: ElevenLabs TTS
    3. Fallback: OpenAI TTS
    4. Retorna arquivo de áudio
    5. Limpeza do arquivo temporário
    """
    tts_router = APIRouter()

    @tts_router.post("/tts", response_class=FileResponse)
    async def synthesize_text(
        background_tasks: BackgroundTasks,
        text: str = Form(...),
        replace_method: bool = Form(False),
        current_user: dict = Depends(get_current_user)
    ):
        """
        Recebe texto, aplica pré-processamento, gera áudio TTS e retorna arquivo MP3.
        A limpeza do arquivo temporário é feita em background após o envio da resposta.
        """
        temp_file_path = None
        try:
            # --- 1. Pré-processamento do texto ---
            preprocessed_text = preprocess_text(text, replace_method)
            if not preprocessed_text:
                raise ValueError("O pré-processamento do texto falhou e não retornou nada.")

            # --- 2. Primeira tentativa → ElevenLabs ---
            if API_KEY_ELEVENLABS and VOICE_ID:
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
                headers = {
                    "xi-api-key": API_KEY_ELEVENLABS,
                    "Content-Type": "application/json"
                }
                payload = {
                    "text": preprocessed_text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.5
                    }
                }

                response = requests.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    temp_file_path = TEMP_DIR / f"temp_{uuid.uuid4()}.mp3"
                    with open(temp_file_path, "wb") as f:
                        f.write(response.content)
                else:
                    # Se ElevenLabs falhar, não levanta erro, apenas permite o fallback
                    print(f"ElevenLabs TTS falhou (status {response.status_code}), usando fallback.")

            # --- 3. Fallback → OpenAI TTS ---
            if not temp_file_path:
                temp_file_path = TEMP_DIR / f"temp_{uuid.uuid4()}.mp3"
                response = openai_client.audio.speech.create(
                    model="gpt-4o-mini",
                    voice="alloy",
                    input=preprocessed_text
                )
                response.stream_to_file(temp_file_path)

            # --- 4. Adiciona a tarefa de limpeza e retorna o arquivo ---
            background_tasks.add_task(os.unlink, temp_file_path)
            return FileResponse(
                temp_file_path,
                media_type="audio/mp3",
                filename=os.path.basename(temp_file_path)
            )

        except Exception as e:
            # Se um arquivo foi criado antes do erro, agende sua remoção
            if temp_file_path and os.path.exists(temp_file_path):
                background_tasks.add_task(os.unlink, temp_file_path)
            # Captura exceções gerais e retorna como HTTP 500
            raise HTTPException(
                status_code=500,
                detail=f"TTS error: {e}"
            )

    return tts_router
