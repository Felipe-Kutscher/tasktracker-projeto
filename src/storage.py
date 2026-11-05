"""
Persistência simples das tarefas em um arquivo JSON.

A pasta de dados é, por padrão, <raiz do projeto>/data. Dentro do container
ela é /app/data (montada como volume pelo docker-compose.yml). Pode ser
trocada com a variável de ambiente TASKTRACKER_DATA_DIR.
"""
import json
import os
from pathlib import Path


def pasta_dados():
    env = os.environ.get("TASKTRACKER_DATA_DIR")
    base = Path(env) if env else Path(__file__).resolve().parent.parent / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base


def caminho_tarefas():
    return pasta_dados() / "tarefas.json"


def carregar_tarefas(caminho=None):
    caminho = Path(caminho) if caminho else caminho_tarefas()
    if not caminho.exists():
        return []
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        if isinstance(dados, list):
            return dados
        raise ValueError("o arquivo não contém uma lista de tarefas")
    except (json.JSONDecodeError, ValueError, OSError) as erro:
        # Preserva o arquivo problemático para não sobrescrevê-lo sem querer.
        backup = caminho.with_name(caminho.stem + ".corrompido.json")
        try:
            os.replace(caminho, backup)
            print(f"Aviso: não consegui ler {caminho.name} ({erro}). "
                  f"Salvei uma cópia em {backup.name} e comecei do zero.\n")
        except OSError:
            print(f"Aviso: não consegui ler {caminho.name} ({erro}).\n")
        return []


def salvar_tarefas(tarefas, caminho=None):
    caminho = Path(caminho) if caminho else caminho_tarefas()
    temporario = caminho.with_name(caminho.name + ".tmp")
    with open(temporario, "w", encoding="utf-8") as arquivo:
        json.dump(tarefas, arquivo, ensure_ascii=False, indent=2)
    os.replace(temporario, caminho)  # troca atômica: evita arquivo pela metade
