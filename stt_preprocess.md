# Documentação - Pré-processamento STT

## Visão Geral
O módulo `preprocess_speech.py` define funções utilitárias para o **pré-processamento de arquivos de áudio**.
Ele recebe um caminho de arquivo de áudio, aplica **conversão para MP3** se necessário, **normaliza a taxa de amostragem para 16kHz**, garante que o arquivo final seja **menor que 25MB**, e, em caso de falha na conversão, realiza **fallback para o arquivo WAV original**.
Os arquivos processados são **temporários**, salvos em um diretório específico e podem ser **removidos periodicamente** por uma função de limpeza.

## Fluxo de Execução
1. **Verificação inicial do arquivo**: Verifica o formato e tamanho do arquivo de entrada. Se já for MP3 e menor que 25MB, retorna o caminho original sem alterações.
2. **Criação de arquivo temporário**: Gera um novo caminho para o arquivo MP3 processado no diretório temporário.
3. **Processamento para WAV**: Abre o arquivo WAV, lê os frames, aplica reamostragem para 16kHz se necessário, codifica para MP3 usando lameenc e salva o resultado.
4. **Verificação de tamanho final**: Confere se o MP3 gerado é menor que 25MB; caso contrário, remove e levanta exceção.
5. **Fallback em erro**: Em caso de falha, loga o erro e retorna o WAV original se aplicável, ou levanta exceção para formatos não suportados.
6. **Limpeza periódica**: Função separada remove arquivos MP3 temporários mais antigos que o tempo especificado (default: 5 minutos).

## Dependências
| Dependência       | Versão Recomendada | Descrição |
|-------------------|--------------------|-----------|
| numpy             | Última             | Manipulação de arrays para dados de áudio. |
| scipy             | Última             | Funções de sinal para reamostragem. |
| fastapi           | Última             | Para exceções HTTP. |
| wave              | Padrão Python      | Leitura de arquivos WAV. |
| lameenc           | Última             | Codificação para MP3. |
| pathlib           | Padrão Python      | Manipulação de caminhos de arquivos. |
| typing            | Padrão Python      | Anotações de tipo. |
| datetime          | Padrão Python      | Manipulação de datas para limpeza. |
| uuid              | Padrão Python      | Geração de IDs únicos. |
| logging           | Padrão Python      | Registro de logs. |
| os                | Padrão Python      | Operações de sistema. |
| io                | Padrão Python      | Manipulação de I/O. |

## Instalação de Dependências
```bash
# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install numpy scipy fastapi wave lameenc

# Rode a aplicação (exemplo para FastAPI, se integrado)
uvicorn main:app --reload  # Substitua 'main' pelo arquivo principal da app
```

## Variáveis de Ambiente
| Variável | Descrição | Valor Padrão | Obrigatória |
|----------|-----------|--------------|-------------|
| N/A      | Nenhuma variável de ambiente é utilizada neste módulo. | N/A | N/A |

## Estrutura do Módulo
```
utils/
└── preprocess_speech.py
temp_audio/  # Diretório temporário criado em runtime
```

## Tratamento de Erros
- **Exceções HTTP**: Levantadas para formatos não suportados (status 400), arquivos maiores que 25MB após processamento (status 400) ou erros genéricos no processamento.
- **Logs**: Erros são logados com `logging.error` para depuração, incluindo detalhes do arquivo e exceção.
- **Fallback**: Para arquivos WAV, em caso de erro na conversão, retorna o arquivo original com um warning logado.
- **Limpeza**: Erros durante remoção de arquivos são logados, mas não interrompem a execução.

## Limpeza de Arquivos Temporários
A função `cleanup_temp_files` remove arquivos MP3 do diretório `temp_audio/` que sejam mais antigos que o tempo especificado (default: 5 minutos).
- **Execução**: Pode ser chamada periodicamente em background ou após processamentos.
- **Retorno**: Quantidade de arquivos removidos.
- **Logs**: Registra remoções bem-sucedidas e erros.
