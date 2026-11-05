"""
Priorização de tarefas: baseline por regras + Random Forest (scikit-learn).

O scikit-learn só é importado dentro das funções que precisam dele, então a
CLI continua funcionando mesmo que ele não esteja instalado (apenas sem
sugestão de prioridade).
"""
import datetime
from collections import Counter
from pathlib import Path

PRIORIDADES = ("Baixa", "Média", "Alta")
FEATURES = ("dias_ate_prazo", "esforco_horas", "n_dependencias")
MIN_TAREFAS = 20  # abaixo disso a avaliação não é confiável


class DadosInsuficientes(Exception):
    """Poucas tarefas (ou pouca variedade de prioridades) para treinar."""


# ---------------------------------------------------------------- utilidades
def parse_data_br(texto):
    return datetime.datetime.strptime(texto, "%d/%m/%Y").date()


def extrair_features(tarefa, hoje=None):
    """
    Converte uma tarefa em [dias_ate_prazo, esforco_horas, n_dependencias].

    Os dias até o prazo são contados a partir de quando a tarefa foi CRIADA
    (criada_em), que é o momento em que a prioridade foi decidida. Se a tarefa
    ainda não tem criada_em (caso de uma sugestão para tarefa nova), usa hoje.
    """
    referencia = None
    if tarefa.get("criada_em"):
        try:
            referencia = datetime.date.fromisoformat(tarefa["criada_em"])
        except ValueError:
            referencia = None
    if referencia is None:
        referencia = hoje or datetime.date.today()
    dias = (parse_data_br(tarefa["data_limite"]) - referencia).days
    return [dias, float(tarefa.get("esforco_horas", 1)), int(tarefa.get("n_dependencias", 0))]


def baseline_regras(features):
    """Regra simples só pelo prazo. É o 'piso' que o modelo precisa superar."""
    dias = features[0]
    if dias <= 2:
        return "Alta"
    if dias <= 7:
        return "Média"
    return "Baixa"


def metricas_sugestoes(tarefas):
    """(sugestões aceitas, total de sugestões feitas) — medido no uso real."""
    com_sugestao = [t for t in tarefas if t.get("prioridade_sugerida")]
    aceitas = sum(1 for t in com_sugestao if t.get("prioridade") == t["prioridade_sugerida"])
    return aceitas, len(com_sugestao)


# ------------------------------------------------------------------- modelo
def caminho_modelo_padrao():
    from storage import pasta_dados
    return pasta_dados() / "modelo_prioridade.joblib"


def treinar(tarefas, caminho_modelo=None, semente=42):
    """
    Avalia e treina o Random Forest. Devolve um dicionário com as métricas.

    Avaliação:
      1. divisão treino/teste (80/20, estratificada) — RF vs. baseline;
      2. validação cruzada estratificada — mais estável com poucos dados.
    O modelo salvo é treinado com todas as tarefas após a avaliação.
    """
    import joblib
    import numpy as np
    import sklearn
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, confusion_matrix
    from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

    validas = [t for t in tarefas if t.get("prioridade") in PRIORIDADES and t.get("data_limite")]
    if len(validas) < MIN_TAREFAS:
        raise DadosInsuficientes(
            f"Há {len(validas)} tarefa(s) com prioridade; são necessárias pelo menos "
            f"{MIN_TAREFAS} para uma avaliação minimamente confiável."
        )

    X = np.array([extrair_features(t) for t in validas], dtype=float)
    y = np.array([t["prioridade"] for t in validas])
    contagem = Counter(y.tolist())
    if len(contagem) < 2 or min(contagem.values()) < 2:
        raise DadosInsuficientes(
            "Cada prioridade presente precisa ter ao menos 2 exemplos "
            f"(distribuição atual: {dict(contagem)})."
        )

    def novo_rf():
        return RandomForestClassifier(n_estimators=200, random_state=semente)

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=semente
    )
    rf = novo_rf().fit(X_tr, y_tr)
    acc_rf = accuracy_score(y_te, rf.predict(X_te))
    acc_base = accuracy_score(y_te, [baseline_regras(x) for x in X_te])
    matriz = confusion_matrix(y_te, rf.predict(X_te), labels=list(PRIORIDADES)).tolist()

    cv_media = cv_desvio = None
    n_splits = min(5, min(contagem.values()))
    if n_splits >= 2:
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=semente)
        notas = cross_val_score(novo_rf(), X, y, cv=cv)
        cv_media, cv_desvio = float(notas.mean()), float(notas.std())

    acc_base_total = accuracy_score(y, [baseline_regras(x) for x in X])

    if caminho_modelo is not None:
        final = novo_rf().fit(X, y)
        joblib.dump(
            {"modelo": final, "features": list(FEATURES), "n_tarefas": len(validas),
             "versao_sklearn": sklearn.__version__},
            caminho_modelo,
        )

    return {
        "n_tarefas": len(validas),
        "n_sinteticas": sum(1 for t in validas if t.get("origem") == "sintetico"),
        "distribuicao": dict(contagem),
        "n_treino": len(y_tr),
        "n_teste": len(y_te),
        "acuracia_rf_teste": float(acc_rf),
        "acuracia_baseline_teste": float(acc_base),
        "acuracia_baseline_total": float(acc_base_total),
        "acuracia_rf_cv_media": cv_media,
        "acuracia_rf_cv_desvio": cv_desvio,
        "cv_folds": n_splits if cv_media is not None else None,
        "matriz_confusao": matriz,
        "ordem_classes": list(PRIORIDADES),
    }


def carregar_modelo(caminho=None):
    """Devolve o modelo salvo ou None (sem arquivo, sem sklearn ou ilegível)."""
    caminho = Path(caminho) if caminho else caminho_modelo_padrao()
    if not caminho.exists():
        return None
    try:
        import joblib
        info = joblib.load(caminho)
        return info if "modelo" in info else None
    except Exception:  # sklearn ausente, versão incompatível, arquivo ruim...
        return None


def sugerir_prioridade(modelo_info, tarefa, hoje=None):
    features = [extrair_features(tarefa, hoje)]
    return str(modelo_info["modelo"].predict(features)[0])
