# Documentação — Processador de Texto com LLM

## Visão Geral

O módulo `TextProcessorLLM.py` define uma classe utilitária responsável pelo **processamento de textos utilizando LLMs (Anthropic e OpenAI)**.  
Ele recebe um texto via método `process_llm`, aplica **transformações específicas** em números, nomes de cultivares e unidades de medida, seguindo regras definidas para correção linguística e formatação.  

O processamento prioriza o **Anthropic (Claude)** e, em caso de falha, realiza **fallback automático para o OpenAI (GPT-4o Mini)**.  

As transformações incluem conversão de números extensos para forma textual, separação de caracteres em nomes de cultivares mistos, correção de concordância de gênero e substituição de abreviações como 'sacas/ha'.

## Fluxo de Execução

1. **Inicialização da Classe**: Cria uma instância de `TextProcessorLLM` com clientes Anthropic e OpenAI.
2. **Construção do Prompt**: Gera um prompt base com regras de processamento e incorpora o texto original.
3. **Tentativa com Anthropic**: Envia o prompt para o modelo "claude-3-haiku-20240307" via API.
4. **Fallback para OpenAI**: Se o Anthropic falhar, envia o mesmo prompt para o modelo "gpt-4o-mini".
5. **Retorno do Resultado**: Retorna o texto processado ou `None` em caso de falha em ambos.

## Dependências

| Dependência   | Versão Recomendada | Descrição |
|---------------|--------------------|-----------|
| anthropic    | Última            | Cliente para API da Anthropic (Claude). |
| openai       | Última            | Cliente para API da OpenAI (GPT). |
| pandas       | Última            | Manipulação de dados (não utilizada diretamente, mas importada). |
| os           | Padrão Python     | Operações de sistema (não utilizada diretamente). |
| uuid         | Padrão Python     | Geração de IDs únicos (não utilizada diretamente). |

## Instalação de Dependências

Crie e ative um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

Instale as dependências:

```bash
pip install anthropic openai pandas
```

## Variáveis de Ambiente

| Variável          | Descrição                          | Exemplo de Valor          | Obrigatória |
|-------------------|------------------------------------|---------------------------|-------------|
| ANTHROPIC_API_KEY | Chave de API para Anthropic.      | sk-ant-...               | ✅        |
| OPENAI_API_KEY    | Chave de API para OpenAI.         | sk-...                   | ✅        |

*Nota*: As chaves devem ser configuradas nos clientes Anthropic e OpenAI antes de instanciar a classe.

## Estrutura do Módulo

```
utils/
└── TextProcessorLLM.py
```

## Tratamento de Erros

- **Exceções na API Anthropic**: Capturadas e logadas com mensagem "Erro com Claude. Alternando para GPT-4o Mini da OpenAI...". Prossegue com fallback para OpenAI.
- **Exceções na API OpenAI**: Capturadas e logadas com detalhes do erro. Retorna `None` se ambos falharem.
- **Erros Gerais**: Não há validação explícita de entrada; assume texto válido. Erros de rede ou API resultam em fallback ou falha total.
