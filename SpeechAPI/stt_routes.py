import assemblyai as aai
import os
import uuid
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
import openai

# Se você tiver pré-processamento em utils
from utils.stt_preprocess import preprocess_audio

# Importa autenticação
from api.auth import get_current_user


# Load environment variables
load_dotenv()

# --- AssemblyAI Configuration ---
API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
if not API_KEY:
    raise RuntimeError("ASSEMBLYAI_API_KEY environment variable not set.")
aai.settings.api_key = API_KEY

# --- OpenAI Configuration ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set.")
openai.api_key = OPENAI_API_KEY

# --- Temporary File Storage ---
TEMP_DIR = Path("stt/audios_stt")
TEMP_DIR.mkdir(parents=True, exist_ok=True)


def create_stt_routes() -> APIRouter:
    stt_router = APIRouter()

    @stt_router.post("/stt", response_class=PlainTextResponse)
    async def transcribe_audio(
        file: UploadFile = File(...), 
        current_user: dict = Depends(get_current_user)
    ) -> str:
        """
        Receives an audio file, optionally pre-processes it, transcribes it using AssemblyAI, 
        and returns the text. If AssemblyAI fails, falls back to OpenAI transcription.
        """
        # Garante um nome de arquivo único para evitar conflitos
        # Usa o sufixo do arquivo original se disponível, senão usa .tmp
        suffix = Path(file.filename).suffix if file.filename else '.tmp'
        temp_file_path = TEMP_DIR / f"{uuid.uuid4()}{suffix}"

        processed_file_path = None
        try:
            # 1. Salva o arquivo recebido no disco
            with open(temp_file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            # 2. Pré-processa o áudio (a função deve retornar o caminho do arquivo processado)
            processed_file_path = preprocess_audio(temp_file_path)

            # 3. Transcrição usando o AssemblyAI
            config = aai.TranscriptionConfig(speech_model="best", language_code="pt")
            transcriber = aai.Transcriber(config=config)
            transcript = transcriber.transcribe(str(processed_file_path))

            if transcript.status == aai.TranscriptStatus.error:
                raise HTTPException(status_code=500, detail=f"AssemblyAI Transcription failed: {transcript.error}")

            if not transcript.text:
                raise HTTPException(status_code=400, detail="AssemblyAI Transcription returned no text.")

            return transcript.text

        except HTTPException as e:
            raise e  # Deixa o FastAPI lidar com HTTPExceptions
        except Exception as e:
            # Caso AssemblyAI falhe, tenta com OpenAI
            try:
                # 4. Fallback para OpenAI API para transcrição
                audio_file = open(str(processed_file_path), "rb")
                openai_audio = openai.Audio.create(file=audio_file, model="whisper-1")
                openai_transcript = openai_audio["text"]

                if not openai_transcript:
                    raise HTTPException(status_code=400, detail="OpenAI Transcription returned no text.")
                
                return openai_transcript

            except Exception as fallback_error:
                raise HTTPException(status_code=500, detail=f"Both AssemblyAI and OpenAI transcription failed: {fallback_error}")

        finally:
            # Garante que os arquivos temporários sejam removidos de forma segura
            import time
            time.sleep(0.1)  # Pequena pausa para garantir que o arquivo não está em uso
            
            # Remove arquivo original se ainda existir
            if temp_file_path and temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                except PermissionError:
                    pass  # Ignora se o arquivo ainda estiver em uso
            
            # Remove arquivo processado se for diferente do original
            if processed_file_path and processed_file_path != str(temp_file_path):
                try:
                    Path(processed_file_path).unlink()
                except (PermissionError, FileNotFoundError):
                    pass  # Ignora erros de permissão ou arquivo não encontrado

    return stt_router
