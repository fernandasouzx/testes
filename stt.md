# Documentação - Rota de Transcrição de Áudio (STT)

# Visão Geral
Este módulo implementa uma rota de transcrição de áudio usando FastAPI, integrando as APIs da AssemblyAI e OpenAI Whisper.
Ele recebe um arquivo de áudio via upload, realiza pré-processamento opcional, tenta a transcrição com a AssemblyAI e, caso falhe, faz fallback automático para o modelo Whisper da OpenAI.

O sistema realiza as seguintes etapas:
1. **Armazena o áudio temporariamente.**  
2. **Executa pré-processamento** (opcional) via `preprocess_audio()`.  
3. **Tenta a transcrição com a AssemblyAI.**  
4. Se falhar, **usa o Whisper (OpenAI)** como fallback.  
5. **Retorna o texto transcrito** em formato `text/plain`.  
6. **Remove arquivos temporários** automaticamente.
---
# Dependências
- FastAPI
- AssemblyAI
- OpenAI Python SDK
- python-dotenv
- uuid
- pathlib
---
# Instalação das dependencias
```bash
pip install fastapi assemblyai openai python-dotenv
```

# Autenticação
A rota requer autenticação via dependencia **get_current_user**, importada de **api.auth**.
O token do usuário é validado antes do processamento do áudio.

# Variáveis Ambientes (.env)
No (.env) adicione as variaveis ambiente
```bash
ASSEMBLYAI_API_KEY="sua_chave_api_aqui"
OPENAI_API_KEY="sua_chave_api_aqui"
```
# Pré-requisitos

# Como executar

# Estrutura 
stt/
