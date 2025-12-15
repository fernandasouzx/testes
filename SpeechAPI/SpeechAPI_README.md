# Documentação - Rotas STT & TTS

## Visão Geral

Este documento detalha os passos necessários para configurar o ambiente de desenvolvimento e as variáveis de ambiente necessárias para executar os módulos de **Speech-to-Text (STT)** e **Text-to-Speech (TTS)**.

## Instalação Geral

Siga os passos abaixo para configurar seu ambiente e instalar todas as dependências necessárias.

### 1\. Crie e Ative um Ambiente Virtual

É altamente recomendado usar um ambiente virtual para gerenciar as dependências do projeto.

```bash
# Crie o ambiente virtual
python3 -m venv venv

# Ative o ambiente virtual
# No Linux/Mac:
source venv/bin/activate

# No Windows:
venv\Scripts\activate
```

### 2\. Instale as Dependências

Você pode instalar todas as dependências de uma vez usando o arquivo `requirements.txt` abaixo.

#### `requirements.txt`

Salve o conteúdo abaixo em um arquivo chamado `requirements.txt` na raiz do seu projeto:

```text
# Framework e Servidor
fastapi
uvicorn

# APIs de IA
openai
assemblyai
elevenlabs

# Utilitários
python-dotenv
requests
```

#### Comando de Instalação

Após criar o arquivo, execute o seguinte comando no seu terminal (com o ambiente virtual ativado):

```bash
pip install -r requirements.txt
```

### 3\. Execute o Servidor

Após a instalação, você pode iniciar o servidor:

```bash
uvicorn app:app --reload
```

-----

## Variáveis de Ambiente

Este projeto utiliza diversas chaves de API que devem ser configuradas através de um arquivo `.env` na raiz do projeto.

Crie um arquivo chamado `.env` e adicione as seguintes variáveis:

| Variável | Descrição | Módulo(s) Relevante(s) | Obrigatória |
| :--- | :--- | :--- | :--- |
| `OPENAI_API_KEY` | Chave da API da OpenAI | STT & TTS | ✅ |
| `ASSEMBLYAI_API_KEY` | Chave da API da AssemblyAI | STT | ✅ |
| `ELEVENLABS_API_KEY` | Chave da API da ElevenLabs | TTS | ❌ |
| `VOICE_ID` | ID da voz da ElevenLabs | TTS | ❌ |

> **Nota (TTS):** Se `ELEVENLABS_API_KEY` ou `VOICE_ID` não forem definidos, o módulo `tts_routes.py` usará **automaticamente o TTS da OpenAI** como serviço principal.

-----

## Configuração da ElevenLabs(TTS)

Para utilizar o TTS da ElevenLabs, é necessário obter o **ID da voz** desejada no painel da plataforma.

1. Acesse o dashboard da ElevenLabs e vá até a seção de vozes.
2. No painel lateral direito, utilize o campo de busca para encontrar a voz desejada.
![Menu de vozes da ElevenLabs](imagens/image.jpeg)

3. Após selecionar a voz, clique nos **três pontos** ao lado do nome da voz.
![Busca de voz na ElevenLabs](imagens/image2.jpeg)
4. Copie o **Voice ID** exibido no menu.
5. Defina o ID copiado no arquivo `.env`:
```bash
VOICE_ID=xxxxxxxxxxxxxxxx
VOICE_ID_2=xxxxxxxxxxxxxxxx
VOICE_ID_3=xxxxxxxxxxxxxxxx
```
> Os campos `VOICE_ID_2` e `VOICE_ID_3` são opcionais e utilizados como fallback automático.

## Detalhamento dos Módulos

### `stt_routes.py`

**Propósito:** Define a rota `/stt` (POST) para transcrição de áudio (Speech-to-Text). O endpoint requer autenticação.

**Fluxo Principal:**

1.  Recebe um arquivo de áudio (`file`) via `form-data`.
2.  Salva e pré-processa o áudio temporariamente.
3.  **Tentativa 1:** Tenta transcrever com a **AssemblyAI**.
4.  **Tentativa 2 (Fallback):** Se a AssemblyAI falhar, utiliza o **OpenAI (Whisper)**.
5.  Retorna o texto puro e limpa os arquivos temporários.

-----

### `tts_routes.py`

**Propósito:** Define a rota `/tts` (POST) para síntese de fala (Text-to-Speech). O endpoint requer autenticação.

**Fluxo Principal:**

1.  Recebe um texto (`text`) e um booleano (`replace_method`) via `form-data`.
2.  O texto passa por pré-processamento usando preprocess_text() para corrigir caracteres, pontuação e melhorar a prosódia.
3.  **Tentativa 1:** Tenta gerar áudio usando a **ElevenLabs**.
    - O sistema testa até 3 IDs de voz: `VOICE_ID`, `VOICE_ID_2`, `VOICE_ID_3`.
    - Se qualquer uma das vozes funcionar, o áudio gerado é salvo temporariamente e retornado ao cliente.

4.  **Tentativa 2 (Fallback):** Se a **ElevenLabs** não estiver configurada ou todas as tentativas falharem, o sistema utiliza o **OpenAI TTS** `(gpt-4o-mini-tts, voz alloy)` para gerar o áudio.
5.  O arquivo MP3 final é salvo em `/tmp/audios_tts` e enviado como resposta.
6. Após o envio, uma tarefa em background remove o arquivo temporário.
7. Em caso de erro durante o processo, o logger registra a falha e uma resposta HTTP 500 é retornada.
