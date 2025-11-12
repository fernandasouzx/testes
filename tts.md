# Documentação — Rota de Síntese de Fala (TTS)

## Visão Geral

O módulo `tts_routes.py` define e configura uma rota da **API FastAPI** responsável pela **síntese de fala (Text-to-Speech)**.  
Ele recebe um texto via requisição `POST`, aplica **pré-processamento linguístico**, tenta gerar o áudio com a **API da ElevenLabs**, e, em caso de falha, realiza **fallback automático para o TTS da OpenAI**.

Os áudios gerados são **temporários**, enviados ao cliente e **removidos após o envio**.

---

## Fluxo de Execução

1. **Entrada do texto:**  
   O cliente envia um formulário `multipart/form-data` com os campos:
   - `text` *(obrigatório)* — texto a ser convertido em fala.  
   - `replace_method` *(opcional, booleano)* — define o método de pré-processamento.

2. **Autenticação:**  
   A rota depende de `get_current_user`, exigindo autenticação válida para o uso.

3. **Pré-processamento:**  
   O texto é tratado pela função `preprocess_text()` (em `utils.tts_preprocess`), que normaliza e ajusta o conteúdo antes da síntese.

4. **Síntese de fala:**
   - **Tentativa 1 – ElevenLabs:**  
     Usa o modelo `eleven_multilingual_v2` com as configurações de voz definidas em `VOICE_ID`.  
     Se a requisição falhar ou retornar código diferente de 200, o sistema prossegue para o fallback.
   - **Tentativa 2 – OpenAI (Fallback):**  
     Utiliza o modelo `gpt-4o-mini` com voz `alloy` para gerar o áudio.

5. **Envio e limpeza:**  
   O arquivo `.mp3` é salvo em `tts/audios_tts/`, enviado como `FileResponse`, e depois **removido automaticamente** em background.

---

## Dependências

| Tipo | Biblioteca | Função |
|------|-------------|--------|
| **Core** | `os`, `uuid`, `pathlib.Path` | Manipulação de diretórios e criação de arquivos temporários |
| **HTTP** | `requests` | Comunicação com a API ElevenLabs |
| **Web** | `fastapi`, `BackgroundTasks`, `FileResponse` | Criação da rota, execução assíncrona e envio de arquivos |
| **Ambiente** | `dotenv` | Carregamento de variáveis de ambiente (.env) |
| **OpenAI** | `openai` | Cliente para o modelo de TTS da OpenAI |
| **Autenticação** | `api.auth.get_current_user` | Restringe o uso do endpoint a usuários autenticados |
| **Pré-processamento** | `utils.tts_preprocess.preprocess_text` | Limpeza e tratamento textual antes da síntese |

---

## Variáveis de Ambiente

| Nome | Descrição | Obrigatória | Exemplo |
|------|------------|--------------|----------|
| `OPENAI_API_KEY` | Chave da API da OpenAI | ✅ | `sk-xxxx` |
| `ELEVENLABS_API_KEY` | Chave da API da ElevenLabs | ❌ | `elev-xxxx` |
| `VOICE_ID` | ID da voz configurada na ElevenLabs | ❌ | `pNInz6obpgDQGcFmaJgB` |

> Se as variáveis `ELEVENLABS_API_KEY` e `VOICE_ID` não estiverem definidas, o sistema utilizará **somente o TTS da OpenAI**.

---

## Estrutura do Módulo
```text
tts_routes.py
├── create_tts_routes() # Função principal que cria o roteador FastAPI
│ └── /tts (POST) # Endpoint para geração de áudio TTS
│ ├── Pré-processa texto
│ ├── Tenta ElevenLabs
│ ├── Fallback para OpenAI
│ └── Retorna MP3 e limpa arquivo
```
---

## Endpoint `/tts`

**Método:** `POST`  
**Autenticação:** Obrigatória (`Bearer Token`)

### Parâmetros

| Nome | Tipo | Local | Obrigatório | Descrição |
|------|------|--------|--------------|------------|
| `text` | `string` | `form-data` | ✅ | Texto a ser convertido em áudio |
| `replace_method` | `boolean` | `form-data` | ❌ | Define modo alternativo de pré-processamento |

### Respostas

| Código | Tipo | Descrição |
|--------|------|------------|
| `200` | `audio/mp3` | Retorna o arquivo de áudio gerado |
| `400` | `application/json` | Texto inválido ou pré-processamento falhou |
| `401` | `application/json` | Falha na autenticação |
| `500` | `application/json` | Erro interno de síntese (TTS) |

---

## Exemplo de Requisição (cURL)

```bash
curl -X POST "http://localhost:8000/tts" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "text=Olá, este é um teste de voz!" \
  -o "voz.mp3"
```
## Limpeza de Arquivos Temporários
Os arquivos .mp3 gerados são armazenados em `tts/audios_tts/` e excluídos automaticamente após o envio ao cliente, utilizando BackgroundTasks do FastAPI.

## Tratamento de Erros

- Falha na ElevenLabs: o sistema exibe aviso no log e ativa o fallback da OpenAI.
- Erro de processamento ou API: é levantada uma exceção HTTPException(status_code=500, detail="TTS error: ...").
- Falha de pré-processamento: retorna erro 400 com mensagem "O pré-processamento do texto falhou e não retornou nada.".
