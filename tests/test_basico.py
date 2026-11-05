"""
Testes básicos. Rode na raiz do projeto:
    python -m unittest discover -s tests -v
"""
import datetime
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import gerar_dados_exemplo  # noqa: E402
import notificar  # noqa: E402
import priorizacao  # noqa: E402
import storage  # noqa: E402

try:
    import sklearn  # noqa: F401
    TEM_SKLEARN = True
except ImportError:
    TEM_SKLEARN = False


class TestFeaturesEBaseline(unittest.TestCase):
    def test_dias_contados_a_partir_da_criacao(self):
        tarefa = {"data_limite": "10/01/2026", "criada_em": "2026-01-05",
                  "esforco_horas": 3, "n_dependencias": 1}
        self.assertEqual(priorizacao.extrair_features(tarefa), [5, 3.0, 1])

    def test_sem_criada_em_usa_hoje_informado(self):
        tarefa = {"data_limite": "10/01/2026"}
        feats = priorizacao.extrair_features(tarefa, hoje=datetime.date(2026, 1, 8))
        self.assertEqual(feats[0], 2)

    def test_baseline(self):
        self.assertEqual(priorizacao.baseline_regras([1, 1, 0]), "Alta")
        self.assertEqual(priorizacao.baseline_regras([5, 1, 0]), "Média")
        self.assertEqual(priorizacao.baseline_regras([20, 1, 0]), "Baixa")


class TestStorage(unittest.TestCase):
    def test_ida_e_volta(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "t.json"
            tarefas = [{"titulo": "Estudar Docker", "prioridade": "Alta"}]
            storage.salvar_tarefas(tarefas, caminho)
            self.assertEqual(storage.carregar_tarefas(caminho), tarefas)

    def test_arquivo_inexistente_devolve_lista_vazia(self):
        with tempfile.TemporaryDirectory() as pasta:
            self.assertEqual(storage.carregar_tarefas(Path(pasta) / "nao_existe.json"), [])

    def test_arquivo_corrompido_vira_backup(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "t.json"
            caminho.write_text("{ isto não é json", encoding="utf-8")
            self.assertEqual(storage.carregar_tarefas(caminho), [])
            self.assertTrue((Path(pasta) / "t.corrompido.json").exists())


class TestResumo(unittest.TestCase):
    def test_contagens(self):
        hoje = datetime.date(2026, 11, 3)
        tarefas = [
            {"titulo": "A", "status": "Concluída", "data_limite": "01/11/2026"},
            {"titulo": "B", "status": "Pendente", "data_limite": "01/11/2026"},   # atrasada
            {"titulo": "C", "status": "Pendente", "data_limite": "05/11/2026"},   # vence logo
            {"titulo": "D", "status": "Pendente", "data_limite": "30/11/2026"},
            {"titulo": "E", "status": "Pendente", "data_limite": "30/11/2026",
             "prioridade": "Alta", "prioridade_sugerida": "Alta"},
        ]
        r = notificar.gerar_resumo(tarefas, hoje)
        self.assertEqual((r["registradas"], r["concluidas"], r["pendentes"]), (5, 1, 4))
        self.assertEqual([t["titulo"] for t in r["atrasadas"]], ["B"])
        self.assertEqual([t["titulo"] for t in r["vencendo"]], ["C"])
        self.assertEqual((r["sugestoes_aceitas"], r["sugestoes_total"]), (1, 1))


class TestTreino(unittest.TestCase):
    def test_poucas_tarefas_nao_treina(self):
        tarefas = gerar_dados_exemplo.gerar(10)
        with self.assertRaises(priorizacao.DadosInsuficientes):
            priorizacao.treinar(tarefas)

    @unittest.skipUnless(TEM_SKLEARN, "scikit-learn não instalado")
    def test_treino_e_sugestao(self):
        tarefas = gerar_dados_exemplo.gerar(200)
        with tempfile.TemporaryDirectory() as pasta:
            destino = Path(pasta) / "m.joblib"
            r = priorizacao.treinar(tarefas, destino)
            self.assertEqual(r["n_tarefas"], 200)
            self.assertEqual(r["n_sinteticas"], 200)
            self.assertEqual(r["n_treino"] + r["n_teste"], 200)
            self.assertTrue(0 <= r["acuracia_rf_teste"] <= 1)
            modelo = priorizacao.carregar_modelo(destino)
            self.assertIsNotNone(modelo)
            urgente = {"data_limite": "04/11/2026", "esforco_horas": 10, "n_dependencias": 2}
            sugestao = priorizacao.sugerir_prioridade(modelo, urgente, datetime.date(2026, 11, 3))
            self.assertIn(sugestao, priorizacao.PRIORIDADES)


if __name__ == "__main__":
    unittest.main()
