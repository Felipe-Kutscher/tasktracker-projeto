"""
Resumo/notificação das tarefas: registradas, concluídas, pendentes, atrasadas
e prestes a vencer.

Uso:
    python src/notificar.py                    # imprime o resumo uma vez
    python src/notificar.py --intervalo 60     # repete a cada 60 segundos
"""
import argparse
import datetime
import time

import priorizacao
import storage

DIAS_ALERTA = 3


def gerar_resumo(tarefas, hoje=None):
    hoje = hoje or datetime.date.today()
    concluidas = [t for t in tarefas if t.get("status") == "Concluída"]
    pendentes = [t for t in tarefas if t.get("status") != "Concluída"]
    atrasadas, vencendo = [], []
    for tarefa in pendentes:
        try:
            dias = (priorizacao.parse_data_br(tarefa["data_limite"]) - hoje).days
        except (KeyError, ValueError):
            continue
        if dias < 0:
            atrasadas.append(tarefa)
        elif dias <= DIAS_ALERTA:
            vencendo.append(tarefa)
    aceitas, total_sugestoes = priorizacao.metricas_sugestoes(tarefas)
    return {
        "data": hoje,
        "registradas": len(tarefas),
        "concluidas": len(concluidas),
        "pendentes": len(pendentes),
        "atrasadas": atrasadas,
        "vencendo": vencendo,
        "sugestoes_aceitas": aceitas,
        "sugestoes_total": total_sugestoes,
    }


def formatar_resumo(resumo):
    linhas = [
        f"=== Resumo TaskTracker — {resumo['data'].strftime('%d/%m/%Y')} ===",
        f"Registradas: {resumo['registradas']} | Concluídas: {resumo['concluidas']} "
        f"| Pendentes: {resumo['pendentes']}",
    ]
    if resumo["atrasadas"]:
        linhas.append(f"ATRASADAS ({len(resumo['atrasadas'])}):")
        linhas += [f"  - {t['titulo']} (venceu em {t['data_limite']})" for t in resumo["atrasadas"]]
    if resumo["vencendo"]:
        linhas.append(f"Vencem em até {DIAS_ALERTA} dias ({len(resumo['vencendo'])}):")
        linhas += [f"  - {t['titulo']} (até {t['data_limite']})" for t in resumo["vencendo"]]
    if resumo["sugestoes_total"]:
        pct = 100 * resumo["sugestoes_aceitas"] / resumo["sugestoes_total"]
        linhas.append(f"Sugestões de prioridade aceitas: {resumo['sugestoes_aceitas']} "
                      f"de {resumo['sugestoes_total']} ({pct:.0f}%)")
    return "\n".join(linhas)


def main():
    parser = argparse.ArgumentParser(description="Resumo das tarefas do TaskTracker.")
    parser.add_argument("--intervalo", type=int, default=0,
                        help="repete o resumo a cada N segundos (0 = uma vez só)")
    args = parser.parse_args()

    try:
        while True:
            # Relê o arquivo a cada ciclo: enxerga o que a CLI salvou.
            print(formatar_resumo(gerar_resumo(storage.carregar_tarefas())), flush=True)
            if args.intervalo <= 0:
                break
            print(flush=True)
            time.sleep(args.intervalo)
    except KeyboardInterrupt:
        print("\nNotificador encerrado.")


if __name__ == "__main__":
    main()
