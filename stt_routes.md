# Documentação — Rota de Transcrição de Áudio (STT)

## Visão Geral

O módulo `stt_routes.py` define e configura uma rota da **API FastAPI** responsável pela **transcrição de áudio (Speech-to-Text)**.  
Ele recebe um arquivo de áudio via requisição `POST`, aplica **pré-processamento de áudio** opcional, tenta transcrever com a **API da AssemblyAI**, e, em caso de falha, realiza **fallback automático para o STT da OpenAI (Whisper)**.

Os arquivos de áudio recebidos são **temporários**, processados e **removidos após a transcrição**.

---

## Fluxo de Execução

1. **Entrada do áudio:**  
   O cliente envia um formulário `multipart/form-data` com o campo:
   - `file` *(obrigatório)* — arquivo de áudio a ser transcrito.

2. **Autenticação:**  
   A rota depende de `get_current_user`, exigindo autenticação válida para o uso.

3. **Pré-processamento:**  
   O áudio é tratado pela função `preprocess_audio()` (em `utils.stt_preprocess`), que normaliza e ajusta o conteúdo antes da transcrição.

4. **Transcrição de áudio:**
   - **Tentativa 1 – AssemblyAI:**  
     Usa o modelo `best` com configuração de linguagem `pt` (português).  
     Se a transcrição falhar ou retornar erro, o sistema prossegue para o fallback.
   - **Tentativa 2 – OpenAI (Fallback):**  
     Utiliza o modelo `whisper-1` para gerar a transcrição.

5. **Envio e limpeza:**  
   A transcrição é retornada como texto simples (`PlainTextResponse`), e os arquivos temporários são **removidos automaticamente** após o processamento.

---

## Dependências

| Tipo | Biblioteca | Função |
|------|-------------|--------|
| **Core** | `os`, `uuid`, `pathlib.Path` | Manipulação de diretórios e criação de arquivos temporários |
| **Web** | `fastapi`, `UploadFile`, `HTTPException`, `PlainTextResponse` | Criação da rota, upload de arquivos e respostas |
| **Ambiente** | `dotenv` | Carregamento de variáveis de ambiente (.env) |
| **AssemblyAI** | `assemblyai` | Cliente para o modelo de STT da AssemblyAI |
| **OpenAI** | `openai` | Cliente para o modelo de STT da OpenAI (Whisper) |
| **Autenticação** | `api.auth.get_current_user` | Restringe o uso do endpoint a usuários autenticados |
| **Pré-processamento** | `utils.stt_preprocess.preprocess_audio` | Limpeza e tratamento de áudio antes da transcrição |

---

# Instalação de Dependências
## 1. Criar e Ativar Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
## 2. Instalar Dependências
```bash
pip install fastapi uvicorn openai assemblyai python-dotenv
```
> Ou, se preferir usar um arquivo requirements.txt:
```bash
pip install -r requirements.txt
```

3. Executar o Servidor
```bash
uvicorn app:app --reload
```

## Variáveis de Ambiente

| Nome | Descrição | Obrigatória | Exemplo |
|------|------------|--------------|----------|
| `ASSEMBLYAI_API_KEY` | Chave da API da AssemblyAI | ✅ | `assemb-xxxx` |
| `OPENAI_API_KEY` | Chave da API da OpenAI | ✅ | `sk-xxxx` |

> Se as variáveis não estiverem definidas, o módulo levanta uma `RuntimeError` durante a inicialização.

---

## Estrutura do Módulo
```text
stt_routes.py
├── create_stt_routes() # Função principal que cria o roteador FastAPI
│ └── /stt (POST) # Endpoint para transcrição de áudio STT
│ ├── Salva arquivo temporário
│ ├── Pré-processa áudio
│ ├── Tenta AssemblyAI
│ ├── Fallback para OpenAI
│ └── Retorna texto e limpa arquivos
```

---

## Endpoint `/stt`

**Método:** `POST`  
**Autenticação:** Obrigatória (`Bearer Token`)

### Parâmetros

| Nome | Tipo | Local | Obrigatório | Descrição |
|------|------|--------|--------------|------------|
| `file` | `file` | `form-data` | ✅ | Arquivo de áudio a ser transcrito |

### Respostas

| Código | Tipo | Descrição |
|--------|------|------------|
| `200` | `text/plain` | Retorna o texto transcrito |
| `400` | `application/json` | Áudio inválido ou transcrição vazia |
| `401` | `application/json` | Falha na autenticação |
| `500` | `application/json` | Erro interno de transcrição (STT) |

---

## Exemplo de Requisição (cURL)

```bash
curl -X POST "http://localhost:8000/stt" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@caminho/para/audio.mp3"
```

## Limpeza de Arquivos Temporários
Os arquivos de áudio são armazenados em `stt/audios_stt/` e excluídos automaticamente após o processamento, com uma pequena pausa para evitar erros de permissão.

## Tratamento de Erros

- Falha na AssemblyAI: o sistema ativa o fallback da OpenAI.
- Erro de processamento ou API: é levantada uma exceção HTTPException(status_code=500, detail="Both AssemblyAI and OpenAI transcription failed: ...").
- Transcrição vazia: retorna erro 400 com mensagem "AssemblyAI/OpenAI Transcription returned no text.".
