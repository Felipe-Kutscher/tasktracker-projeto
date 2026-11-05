# TaskTracker

Aplicação **CLI (Interface de Linha de Comando)** em Python para gerenciamento de tarefas, desenvolvida no **Bootcamp II**.
Na Entrega Final, a aplicação foi **conteinerizada com Docker** e **orquestrada com Docker Compose**. Em uma evolução posterior, ganhou **persistência em disco**, um **resumo automático** das tarefas e uma **sugestão de prioridade com Random Forest**.

## Descrição do Projeto

O TaskTracker permite cadastrar tarefas com título, descrição, data limite, esforço estimado, dependências e prioridade, além de listar, concluir e resumir as tarefas cadastradas. Cada tarefa é criada com status **Pendente**. As tarefas ficam salvas em `data/tarefas.json` e continuam disponíveis quando a aplicação é reaberta.

## Funcionalidades

- Cadastro, listagem e conclusão de tarefas, com validação das entradas.
- **Persistência** em JSON (`data/tarefas.json`).
- **Resumo/notificação**: registradas, concluídas, pendentes, atrasadas e vencendo em até 3 dias (menu da CLI ou serviço `notificador`).
- **Sugestão de prioridade** (Alta/Média/Baixa) a partir de prazo, esforço e dependências. A decisão final é sempre do usuário: `Enter` aceita a sugestão, ou digita-se outra prioridade.

## Tecnologias utilizadas

- Python 3.11
- scikit-learn (Random Forest)
- Docker (empacotamento da imagem)
- Docker Compose (orquestração da CLI, do notificador e do treino)
- Git e GitHub (versionamento)
- Markdown (documentação)

## Estrutura do projeto

```text
tasktracker-projeto/
├── .gitignore
├── data/                     
├── docs/
│   └── planejamento_logico.pdf
├── src/
│   ├── main.py               
│   ├── storage.py            
│   ├── notificar.py           
│   ├── priorizacao.py         
│   ├── treinar.py             
│   └── gerar_dados_exemplo.py 
├── tests/
│   └── test_basico.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Como executar com Docker

**Pré-requisito:** ter o [Docker](https://docs.docker.com/get-docker/) instalado (o Docker Compose já vem incluído nas versões atuais).
Execute todos os comandos **na raiz do repositório**.

### 1. Como construir a imagem

```bash
docker build -t tasktracker .
```

### 2. Como rodar o container em modo isolado

```bash
docker run -it --rm -v "$(pwd)/data:/app/data" tasktracker
```

> `-it` é obrigatório: a aplicação usa `input()` e precisa de um terminal interativo.
> `-v` guarda as tarefas na pasta `data/` do seu computador; sem ele, os dados somem quando o container é removido.

### 3. Como rodar via orquestração (Recomendado)

```bash
docker compose run --rm tasktracker
```

O `docker-compose.yml` configura `stdin_open: true` e `tty: true` (menu interativo) e monta `./data` como volume (persistência).

### 4. Resumo automático (notificador)

```bash
docker compose up -d notificador
docker compose logs -f notificador
docker compose stop notificador
```

O notificador relê `data/tarefas.json` a cada ciclo, então enxerga o que foi cadastrado na CLI.

## Sugestão de prioridade com Random Forest

### Como funciona

Para cada tarefa, o modelo recebe três números: **dias até o prazo** (contados a partir da criação da tarefa), **esforço em horas** e **número de dependências**. Ele devolve Alta, Média ou Baixa. Como ponto de comparação existe um **baseline** simples por regra (só pelo prazo: até 2 dias = Alta, até 7 = Média, acima disso = Baixa). O modelo só vale a pena se superar esse baseline.

O rótulo usado no treino é **a prioridade que o próprio usuário atribuiu** às tarefas. Ou seja, o modelo aprende a imitar as decisões de quem usa o app.

### Como treinar e avaliar

Depois de cadastrar pelo menos 20 tarefas com prioridades variadas:

```bash
docker compose run --rm treino
```

O script faz uma divisão treino/teste (80/20, estratificada) e uma validação cruzada, compara o Random Forest com o baseline e mostra a matriz de confusão. O modelo final é salvo em `data/modelo_prioridade.joblib` e passa a ser carregado automaticamente pela CLI. Se houver menos de 20 tarefas, o treino é recusado.

### Testando sem dados reais

```bash
docker compose run --rm treino python src/gerar_dados_exemplo.py
docker compose run --rm treino python src/treinar.py --dados data/tarefas_exemplo.json
```

Esses dados são **sintéticos**, gerados por uma regra com ruído. Servem apenas para verificar que o pipeline funciona. A acurácia obtida com eles mede se o modelo reaprende a regra do gerador e **não deve ser citada como resultado do projeto**. O modelo gerado fica em `modelo_exemplo.joblib` e não é carregado pela CLI.

### Resultados medidos

Resultado do `treinar.py` sobre 20 tarefas reais cadastradas no app (7 Alta, 7 Baixa e 6 Média):

| Métrica | Valor |
|---|---|
| Nº de tarefas reais usadas | 20 |
| Baseline por prazo | 25,0% |
| Random Forest (validação cruzada, média ± desvio) | 35,0% (± 25,5%) |
| Random Forest (teste 20%) | 75,0% (3 acertos em 4 tarefas) |
| Sugestões aceitas no uso real (menu "Resumo") | ainda não medido |

Resultado preliminar. Com 20 tarefas, o conjunto de teste tem apenas 4 exemplos, então os 75% (3 acertos em 4) não são tão confiáveis. Na validação cruzada, o Random Forest (35,0% - 25,5%) não se distingue do acaso nem do baseline por prazo (25,0%) dentro da margem de erro. As tarefas foram cadastradas no mesmo período, e prazo, esforço e dependências não foram suficientes para prever as prioridades atribuídas. Próximos passos: mais tarefas e novos atributos, como o tipo da tarefa.

### Limitações conhecidas

- O modelo tenta imitar as decisões do usuário; não existe "prioridade correta" objetiva.
- Com poucas tarefas, as métricas variam bastante. Por isso são reportadas com margem de erro.
- Aceitar a sugestão com `Enter` reforça o próprio modelo: a taxa de aceitação tende a superestimar o acerto.
- "Dependências" é apenas a quantidade informada pelo usuário, sem vínculo real entre tarefas.
- O ganho de tempo na triagem **não foi medido**; exigiria um experimento (tempo para priorizar com e sem sugestão).
- Os dados ficam em um arquivo local, sem login ou criptografia.

## Testes

```bash
python -m unittest discover -s tests -v
```

## Decisões técnicas

| Arquivo | Papel |
|---|---|
| `Dockerfile` | **A receita**: empacota a aplicação sobre `python:3.11-slim`, define `WORKDIR /app`, `PYTHONUNBUFFERED=1` (logs imediatos), instala `requirements.txt` (camada em cache), copia `src/` e executa `python src/main.py`. |
| `docker-compose.yml` | **O maestro**: orquestra a CLI interativa (`stdin_open` + `tty`), o `notificador` (perfil `notificacao`) e o `treino` (perfil `treino`), todos compartilhando o volume `./data`. |
| `requirements.txt` | Dependência de ML (scikit-learn). |

## Observações

- `docker compose up` não é indicado para a CLI interativa: use sempre `docker compose run`.
- Para sair da aplicação, use a opção de saída do menu (ou `Ctrl+C`).