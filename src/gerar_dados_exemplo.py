"""
Gera tarefas SINTÉTICAS (inventadas) só para testar o pipeline de treino.

Cada tarefa recebe "origem": "sintetico" e a prioridade vem de uma regra com
um pouco de ruído. Portanto, a acurácia do modelo treinado nesses dados NÃO
representa o desempenho com tarefas reais.

Uso:
    python src/gerar_dados_exemplo.py                # 200 tarefas
    python src/gerar_dados_exemplo.py --n 500
"""
import argparse
import datetime
import json
import random
from pathlib import Path

import storage


def gerar(n, semente=42):
    rng = random.Random(semente)
    hoje = datetime.date.today()
    tarefas = []
    for i in range(1, n + 1):
        criada = hoje - datetime.timedelta(days=rng.randint(0, 90))
        dias = rng.randint(0, 30)
        esforco = rng.randint(1, 16)
        dependencias = rng.choice([0, 0, 0, 1, 1, 2, 3])
        limite = criada + datetime.timedelta(days=dias)

        urgencia = max(0, 14 - dias) / 14
        carga = esforco / 16
        bloqueio = min(dependencias, 3) / 3
        pontuacao = 0.6 * urgencia + 0.25 * carga + 0.15 * bloqueio + rng.gauss(0, 0.08)
        if pontuacao >= 0.5:
            prioridade = "Alta"
        elif pontuacao >= 0.28:
            prioridade = "Média"
        else:
            prioridade = "Baixa"

        concluida = rng.random() < 0.5
        tarefas.append({
            "titulo": f"Tarefa de exemplo {i}",
            "descricao": "(Dado sintético)",
            "data_limite": limite.strftime("%d/%m/%Y"),
            "esforco_horas": esforco,
            "n_dependencias": dependencias,
            "prioridade": prioridade,
            "prioridade_sugerida": None,
            "status": "Concluída" if concluida else "Pendente",
            "criada_em": criada.isoformat(),
            "concluida_em": (criada + datetime.timedelta(days=rng.randint(0, max(dias, 1)))).isoformat()
            if concluida else None,
            "origem": "sintetico",
        })
    return tarefas


def main():
    parser = argparse.ArgumentParser(description="Gera tarefas sintéticas de exemplo.")
    parser.add_argument("--n", type=int, default=200, help="quantidade de tarefas")
    parser.add_argument("--saida", help="arquivo de saída (padrão: data/tarefas_exemplo.json)")
    args = parser.parse_args()

    saida = Path(args.saida) if args.saida else storage.pasta_dados() / "tarefas_exemplo.json"
    tarefas = gerar(args.n)
    with open(saida, "w", encoding="utf-8") as arquivo:
        json.dump(tarefas, arquivo, ensure_ascii=False, indent=2)
    print(f"{len(tarefas)} tarefas SINTÉTICAS salvas em {saida}")


if __name__ == "__main__":
    main()
