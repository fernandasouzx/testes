# Documentação — Substituição de Texto

## Visão Geral

O módulo `replace_text.py` define a classe **ReplaceText**, uma utilitária para **substituição de palavras em textos** baseada em um arquivo CSV com pares de mapeamento (find, replace).  
Ele utiliza expressões regulares para substituições precisas de palavras inteiras, evitando alterações em substrings. O módulo é projetado para integração com pré-processadores de texto, como em pipelines de TTS ou processamento linguístico.

O processamento é eficiente, removendo temporariamente caracteres especiais para identificação de palavras e aplicando substituições de forma segura.

---

## Fluxo de Execução

1. **Inicialização da classe (`__init__`):**  
   - Lê o arquivo CSV especificado.  
   - Verifica a presença das colunas 'find' e 'replace'.  
   - Cria um dicionário de mapeamentos.  
   - Registra o carregamento via logging.

2. **Substituição de palavras (`replace_word`):**  
   - Remove caracteres especiais do texto para extrair palavras.  
   - Itera pelas palavras, buscando substituições no dicionário.  
   - Aplica substituições apenas em palavras inteiras usando regex.  
   - Registra o texto modificado em nível debug.

3. **Métodos auxiliares:**  
   - `remove_special_characters`: Limpa o texto de símbolos para facilitar a identificação de palavras.  
   - `replace_whole_word`: Realiza a substituição regex com limites de palavra (\b).  
   - `change_dict`: Atualiza dinamicamente o dicionário de mapeamentos.

---

## Dependências

| Tipo | Biblioteca | Função |
|------|-------------|--------|
| **Dados** | `pandas` | Leitura e manipulação do arquivo CSV |
| **Regex** | `re` | Expressões regulares para substituições e limpeza |
| **Logging** | `logging` | Registro de eventos e depuração |
| **Tipagem** | `typing.Dict` | Anotações de tipos para dicionários |

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
pip install pandas
```
> Ou, se preferir usar um arquivo requirements.txt:
```bash
pip install -r requirements.txt
```

---

## Variáveis de Ambiente

Nenhuma variável de ambiente é requerida para este módulo.

---

## Estrutura do Módulo
```text
replace_text.py
├── ReplaceText # Classe principal
│ ├── __init__() # Inicializa com CSV e cria mapeamento
│ ├── replace_word() # Substitui palavras no texto
│ ├── remove_special_characters() # Limpa caracteres especiais
│ ├── replace_whole_word() # Substitui palavra inteira via regex
│ └── change_dict() # Atualiza dicionário dinamicamente
```

---

## Classe `ReplaceText`

### Método `__init__`

**Assinatura:** `__init__(self, file_path: str)`

#### Parâmetros

| Nome | Tipo | Obrigatório | Descrição |
|------|------|--------------|------------|
| `file_path` | `str` | ✅ | Caminho para o arquivo CSV de mapeamentos |

### Método `replace_word`

**Assinatura:** `replace_word(self, text: str) -> str`

#### Parâmetros

| Nome | Tipo | Obrigatório | Descrição |
|------|------|--------------|------------|
| `text` | `str` | ✅ | Texto a ser processado |

#### Retorno

- `str`: Texto com substituições aplicadas.

### Método `change_dict`

**Assinatura:** `change_dict(self, find: str, replace: str) -> Dict[str, str]`

#### Parâmetros

| Nome | Tipo | Obrigatório | Descrição |
|------|------|--------------|------------|
| `find` | `str` | ✅ | Palavra a ser substituída |
| `replace` | `str` | ✅ | Palavra substituta |

#### Retorno

- `Dict[str, str]`: Dicionário de mapeamentos atualizado.


## Tratamento de Erros

- **Erro ao carregar CSV:** Registra erro via logging e levanta exceção.
- **Colunas ausentes no CSV:** Levanta `ValueError` com mensagem "O CSV precisa conter as colunas 'find' e 'replace'.".
- **Substituições não encontradas:** Palavras sem mapeamento são ignoradas, mantendo o texto original.
