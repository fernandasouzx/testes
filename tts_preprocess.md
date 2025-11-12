# Documentação — Pré-processamento de Texto para TTS

## Visão Geral

O módulo `preprocess_tts.py` define funções e configurações para o **pré-processamento de texto** destinado à **síntese de fala (Text-to-Speech - TTS)**.  
Ele utiliza **modelos de linguagem grandes (LLMs)** da OpenAI e Anthropic para corrigir e ajustar o texto, além de aplicar substituições opcionais baseadas em um arquivo CSV (`replace_tts.csv`).  

O pré-processamento visa melhorar a qualidade da fala sintetizada, corrigindo erros gramaticais, ajustando pronúncias e substituindo termos específicos.  
O módulo é projetado para integração com APIs de TTS, como em rotas FastAPI.

---

## Fluxo de Execução

1. **Inicialização de dependências:**  
   - Carrega o caminho absoluto para o arquivo CSV de substituições (`replace_tts.csv`).  
   - Cria uma instância de `ReplaceText` para manipulação de substituições.  
   - Verifica e carrega chaves de API das variáveis de ambiente (`OPENAI_API_KEY` e `CLAUDE_API_KEY`).  
   - Inicializa clientes para as APIs da OpenAI e Anthropic.  
   - Cria uma instância de `TextProcessorLLM` para processamento via LLM.

2. **Pré-processamento do texto (função `preprocess_text`):**  
   - Valida se o texto de entrada não está vazio.  
   - Aplica correções e ajustes usando LLM via `TextProcessorLLM`.  
   - Opcionalmente, aplica substituições de palavras do CSV se `replace_method` for `True`.  
   - Retorna o texto processado pronto para TTS.

---

## Dependências

| Tipo | Biblioteca | Função |
|------|-------------|--------|
| **Core** | `os` | Manipulação de caminhos de arquivos e diretórios |
| **HTTP** | `fastapi.HTTPException` | Levantamento de exceções para validação de entrada |
| **LLM** | `openai` | Cliente para API da OpenAI (correções de texto) |
| **LLM** | `anthropic` | Cliente para API da Anthropic (correções de texto) |
| **Pré-processamento** | `utils.replace_text.ReplaceText` | Substituições baseadas em CSV |
| **Pré-processamento** | `utils.TextProcessorLLM` | Processamento avançado via LLM |

---

## Instalação de Dependências

## 1. Criar e Ativar Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

## 2. Instalar Dependências

```bash
pip install fastapi openai anthropic
```

> Ou, se preferir usar um arquivo `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## Variáveis de Ambiente

| Nome | Descrição | Obrigatória | Exemplo |
|------|------------|--------------|----------|
| `OPENAI_API_KEY` | Chave da API da OpenAI | ✅ | `sk-xxxx` |
| `CLAUDE_API_KEY` | Chave da API da Anthropic (Claude) | ✅ | `claude-xxxx` |

> Se as variáveis não estiverem definidas, o módulo levanta uma `ValueError` durante a inicialização.

---

## Estrutura do Módulo

```text
preprocess_tts.py
├── Inicialização global
│ ├── Carrega caminho do CSV (replace_tts.csv)
│ ├── Cria ReplaceText
│ ├── Verifica e carrega API keys (OpenAI e Anthropic)
│ ├── Cria clientes OpenAI e Anthropic
│ └── Cria TextProcessorLLM
└── preprocess_text() # Função principal de pré-processamento
   ├── Valida texto de entrada
   ├── Processa com LLM
   ├── Aplica substituições (opcional)
   └── Retorna texto corrigido
```

---

## Função `preprocess_text`

**Assinatura:** `preprocess_text(text: str, replace_method: bool = False) -> str`

### Parâmetros

| Nome | Tipo | Obrigatório | Descrição |
|------|------|--------------|------------|
| `text` | `str` | ✅ | Texto de entrada para pré-processamento |
| `replace_method` | `bool` | ❌ (padrão: False) | Se True, aplica substituições adicionais via CSV |

### Retorno

- `str`: Texto pré-processado e pronto para síntese de fala.

### Exceções

| Tipo | Descrição |
|------|------------|
| `HTTPException(400)` | Texto de entrada vazio ou inválido |
| `ValueError` | Chaves de API não definidas durante inicialização |


## Tratamento de Erros

- **Texto vazio:** Levanta `HTTPException(400)` com mensagem "Texto de entrada vazio.".
- **Falha em API keys:** Levanta `ValueError` na inicialização do módulo.
- **Erros no processamento LLM:** Dependem da implementação de `TextProcessorLLM`; o módulo assume que o processador retorna um texto válido.
