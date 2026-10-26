# TaskTracker

É uma aplicação CLI (Interface de Linha de Comando) em Python para gerenciamento de tarefas, desenvolvida no Bootcamp II. Na Entrega Final, a aplicação foi **conteinerizada com Docker** e **orquestrada com Docker Compose**.

## Descrição do Projeto

O TaskTracker que resolvi criar se trata de uma ferramenta que permite cadastrar tarefas com título, descrição, prioridade e data limite, além de listar todas as tarefas cadastradas. Cada tarefa é criada automaticamente com status **Pendente** e pode ser alterada ao longo do tempo.

## Tecnologias utilizadas

- Python 3.11
- Docker (empacotamento da imagem)
- Docker Compose (orquestração da execução interativa)
- Git e GitHub (versionamento)
- Markdown (documentação)

## Estrutura do projeto

```text
tasktracker-projeto/
├── .gitignore
├── docs/
│   └── planejamento_logico.pdf
├── src/
│   └── main.py
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Como executar com Docker

**PARA RODAR O DOCKER É NECESSÁRIO:** Ter o [Docker](https://docs.docker.com/get-docker/) instalado na sua máquina e executar os comandos **NA RAIZ DO REPOSITÓRIO**.

### 1. Como construir a imagem

```bash
docker build -t tasktracker .
```

### 2. Como rodar o container em modo isolado

```bash
docker run -it --rm tasktracker
```

> `-it` é obrigatório: a aplicação usa `input()` e precisa de um terminal interativo.

### 3. Como rodar via orquestração (Recomendado)

```bash
docker compose run --rm tasktracker
```

O `docker-compose.yml` já configura `stdin_open: true` e `tty: true`, que mantêm a entrada de dados aberta e alocam um terminal virtual para o menu interativo.

## Decisões técnicas

| Arquivo | Papel |
|---|---|
| `Dockerfile` | **É A RECEITA**: Empacota a aplicação, define `WORKDIR /app`, `PYTHONUNBUFFERED=1` (logs imediatos), copia `src/` e executa `python src/main.py`. |
| `docker-compose.yml` | **É COMO SE FOSSE O MAESTRO**: Orquestra a execução interativa da CLI (`stdin_open` + `tty`). |
