"""
Treina e AVALIA o modelo de sugestão de prioridade com as suas tarefas.

Uso:
    python src/treinar.py                                  # usa data/tarefas.json
    python src/treinar.py --dados data/tarefas_exemplo.json  # dados sintéticos (demo)

Imprime as métricas e salva data/metricas.json. O modelo só é salvo no caminho
que a CLI usa (modelo_prioridade.joblib) quando os dados são REAIS; com dados
sintéticos ele vai para modelo_exemplo.joblib, para não contaminar o uso real.
"""
import argparse
import json
import sys
from pathlib import Path

import priorizacao
import storage


def pct(valor):
    return f"{100 * valor:.1f}%"


def imprimir_relatorio(r):
    print("\n=== Avaliação do modelo de prioridade ===")
    print(f"Tarefas usadas: {r['n_tarefas']}  distribuição: {r['distribuicao']}")
    if r["n_sinteticas"]:
        print(f"\n!! ATENÇÃO: {r['n_sinteticas']} de {r['n_tarefas']} tarefas são SINTÉTICAS "
              "(geradas por uma regra).\n"
              "!! A acurácia abaixo mede se o modelo reaprende a regra do gerador.\n"
              "!! NÃO é resultado de uso real e não deve ser apresentada como tal.\n")
    print(f"Treino/teste: {r['n_treino']} / {r['n_teste']} (80/20, estratificado)")
    print(f"  Baseline (regra por prazo) no teste: {pct(r['acuracia_baseline_teste'])}")
    print(f"  Random Forest no teste:              {pct(r['acuracia_rf_teste'])}")
    if r["acuracia_rf_cv_media"] is not None:
        print(f"Validação cruzada ({r['cv_folds']} folds):")
        print(f"  Random Forest: {pct(r['acuracia_rf_cv_media'])} "
              f"(± {pct(r['acuracia_rf_cv_desvio'])})")
        print(f"  Baseline em todos os dados: {pct(r['acuracia_baseline_total'])}")
    print(f"\nMatriz de confusão no teste (linhas = real, colunas = previsto; "
          f"ordem {r['ordem_classes']}):")
    for classe, linha in zip(r["ordem_classes"], r["matriz_confusao"]):
        print(f"  {classe:<6} {linha}")
    if r["n_tarefas"] < 100:
        print("\nObs.: com menos de 100 tarefas o teste tem poucos exemplos; "
              "prefira o resultado da validação cruzada e cite a margem de erro.")


def main():
    parser = argparse.ArgumentParser(description="Treina e avalia o modelo de prioridade.")
    parser.add_argument("--dados", help="JSON de tarefas (padrão: data/tarefas.json)")
    parser.add_argument("--modelo", help="onde salvar o modelo (padrão automático)")
    args = parser.parse_args()

    origem = Path(args.dados) if args.dados else storage.caminho_tarefas()
    if not origem.exists():
        print(f"Arquivo não encontrado: {origem}")
        print("Cadastre tarefas no TaskTracker (ou gere dados de exemplo com "
              "src/gerar_dados_exemplo.py).")
        sys.exit(1)
    tarefas = storage.carregar_tarefas(origem)

    tem_sinteticas = any(t.get("origem") == "sintetico" for t in tarefas)
    if args.modelo:
        destino = Path(args.modelo)
    elif tem_sinteticas:
        destino = storage.pasta_dados() / "modelo_exemplo.joblib"
    else:
        destino = priorizacao.caminho_modelo_padrao()

    try:
        resultado = priorizacao.treinar(tarefas, destino)
    except priorizacao.DadosInsuficientes as erro:
        print(f"Não foi possível treinar: {erro}")
        print("Use o TaskTracker por mais tempo (ou gere dados de exemplo com "
              "src/gerar_dados_exemplo.py para testar o pipeline).")
        sys.exit(1)

    imprimir_relatorio(resultado)
    with open(storage.pasta_dados() / "metricas.json", "w", encoding="utf-8") as arquivo:
        json.dump(resultado, arquivo, ensure_ascii=False, indent=2)
    print(f"\nModelo salvo em: {destino}")
    if tem_sinteticas and not args.modelo:
        print("(modelo de EXEMPLO: a CLI não o carrega automaticamente)")


if __name__ == "__main__":
    main()
