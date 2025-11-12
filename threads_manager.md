# Documentação — ThreadManager

## Visão Geral

A classe `ThreadManager` gerencia threads de conversação integradas com a API da OpenAI e o banco de dados Supabase.  
Ela verifica ou cria threads associadas a um `cliente_id` e `session_id`, armazena metadados no Supabase, recupera histórico de mensagens da OpenAI, adiciona novas mensagens e oferece métodos para deleção, listagem e estatísticas de threads.  
Todos os erros são logados via módulo `logging`, e a classe usa variáveis de ambiente para autenticação segura.

## Fluxo de Execução

- Carrega variáveis de ambiente via `dotenv` e inicializa clients para Supabase e OpenAI.
- No método `get_or_create_thread`, verifica existência de thread no Supabase; se não existir, cria uma nova via OpenAI e insere registro no Supabase.
- Para recuperação de histórico (`get_thread_history`), lista mensagens da OpenAI e converte para formato de dicionário compatível.
- Adição de mensagens (`add_message_to_thread`) cria entradas diretamente na thread da OpenAI.
- Métodos de deleção (`delete_thread_specific`, `delete_client_mapping`, `delete_user_mapping`) removem registros do Supabase após verificação de existência.
- Métodos de listagem e estatísticas (`get_all_threads`, `get_mapping_stats`, `get_user_threads`, `get_client_info_by_thread`) executam consultas no Supabase para agregação de dados.

## Dependências

| Pacote       | Versão | Descrição                          |
|--------------|--------|------------------------------------|
| uuid        | -     | Geração de IDs únicos              |
| os          | -     | Acesso a variáveis de sistema      |
| logging     | -     | Registro de logs e erros           |
| typing      | -     | Anotações de tipo para funções     |
| datetime    | -     | Manipulação de datas e fusos       |
| dotenv      | -     | Carregamento de .env               |
| supabase    | -     | Client para banco Supabase         |
| openai      | -     | Client para API OpenAI             |

## Instalação de Dependências

```bash
# Cria ambiente virtual
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instala dependências
pip install python-dotenv supabase openai

# Executa o módulo 
uvicorn main:app --reload  # Assumindo integração em app FastAPI; para script standalone, use python script.py
```

## Variáveis de Ambiente

| Variável      | Descrição                          | Obrigatória |
|---------------|------------------------------------|-------------|
| SUPABASE_URL | URL do projeto Supabase            | ✅        |
| SUPABASE_KEY | Chave de API do Supabase           | ✅        |
| OPENAI_KEY   | Chave de API da OpenAI             | ✅        |

## Estrutura do Módulo

```
ThreadManager/
├── __init__.py          # Inicialização (opcional)
├── thread_manager.py    # Classe principal com métodos
│   ├── __init__()       # Construtor e inicialização
│   ├── get_or_create_thread()  # Criação/verificação de thread
│   ├── get_thread_history()    # Recuperação de histórico
│   ├── add_message_to_thread() # Adição de mensagens
│   ├── delete_thread_specific()# Deleção de thread específica
│   ├── get_all_threads()       # Listagem de threads
│   ├── get_client_info_by_thread() # Info por thread
│   ├── get_mapping_stats()     # Estatísticas
│   ├── get_user_threads()      # Threads por user
│   ├── delete_client_mapping() # Deleção por client
│   └── delete_user_mapping()   # Deleção por user
└── .env                 # Arquivo de variáveis (não versionado)
```

## Tratamento de Erros

Erros são capturados em blocos `try-except` e logados via `logging.error` com mensagens descritivas, incluindo o contexto (ex.: thread_id ou cliente_id).  
Métodos retornam valores de fallback (ex.: listas vazias ou False) em caso de falha, sem propagar exceções para o chamador.  
Exemplos incluem erros na criação de threads, recuperação de histórico ou consultas ao Supabase.
