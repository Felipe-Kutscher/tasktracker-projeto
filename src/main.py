"""
TaskTracker — Gerenciamento de tarefas.
Bootcamp II — Entrega Final
"""
import datetime

import notificar
import priorizacao
import storage


def ler_titulo():
    while True:
        titulo = input("Título da tarefa: ").strip()
        if titulo:
            return titulo
        print("Erro! O título é obrigatório e não pode ser vazio.\n")


def ler_data():
    while True:
        data_limite = input("Data limite (DD/MM/AAAA): ").strip()
        try:
            dia, mes, ano = data_limite.split('/')
            if len(dia) == 2 and len(mes) == 2 and len(ano) == 4:
                datetime.datetime(int(ano), int(mes), int(dia))
                return data_limite
            else:
                print("Erro! Use o formato exato: DD/MM/AAAA (ex: 05/12/2025).\n")
        except ValueError:
            print("Erro! Data inválida ou formato incorreto. Use DD/MM/AAAA.\n")


def ler_inteiro(mensagem, minimo, maximo):
    while True:
        try:
            numero = int(input(mensagem).strip())
        except ValueError:
            print("Erro! Digite um número inteiro.\n")
            continue
        if minimo <= numero <= maximo:
            return numero
        print(f"Erro! Digite um valor entre {minimo} e {maximo}.\n")


def ler_prioridade(sugestao=None):
    if sugestao:
        mensagem = f"Prioridade (Alta / Média / Baixa) [Enter = aceitar sugestão: {sugestao}]: "
    else:
        mensagem = "Prioridade (Alta / Média / Baixa): "
    opcoes = {"alta": "Alta", "média": "Média", "media": "Média", "baixa": "Baixa"}
    while True:
        entrada = input(mensagem).strip().lower()
        if not entrada and sugestao:
            return sugestao
        if entrada in opcoes:
            return opcoes[entrada]
        print("Erro! Prioridade inválida. Use apenas: Alta, Média ou Baixa.\n")


def cadastrar_tarefa(tarefas, modelo=None):
    print("\n--- Cadastro de nova tarefa ---")
    titulo = ler_titulo()
    descricao = input("Descrição: ").strip()
    data_limite = ler_data()
    esforco = ler_inteiro("Esforço estimado em horas (1 a 200): ", 1, 200)
    dependencias = ler_inteiro(
        "Quantas tarefas precisam ficar prontas antes desta? (0 a 20): ", 0, 20
    )

    hoje = datetime.date.today()
    tarefa = {
        "titulo": titulo,
        "descricao": descricao if descricao else "(Sem descrição)",
        "data_limite": data_limite,
        "esforco_horas": esforco,
        "n_dependencias": dependencias,
    }

    # A sugestão usa só prazo, esforço e dependências; a decisão final é sua.
    sugestao = None
    if modelo:
        try:
            sugestao = priorizacao.sugerir_prioridade(modelo, tarefa, hoje)
        except Exception:
            print("Aviso: não foi possível gerar a sugestão de prioridade.\n")

    prioridade = ler_prioridade(sugestao)

    tarefa.update({
        "prioridade": prioridade,
        "prioridade_sugerida": sugestao,
        "status": "Pendente",
        "criada_em": hoje.isoformat(),
        "concluida_em": None,
    })
    tarefas.append(tarefa)
    storage.salvar_tarefas(tarefas)
    print(f"\nTarefa ({titulo}) registrada com sucesso!\n")


def listar_tarefas(tarefas):
    print("\n--- Tarefas cadastradas ---")
    if not tarefas:
        print("Nenhuma tarefa cadastrada no momento.\n")
        return

    for indice, tarefa in enumerate(tarefas, start=1):
        print(f"\nTarefa #{indice}")
        print(f"Título:      {tarefa['titulo']}")
        print(f"Descrição:   {tarefa['descricao']}")
        print(f"Prioridade:  {tarefa['prioridade']}")
        print(f"Data Limite: {tarefa['data_limite']}")
        print(f"Esforço:     {tarefa.get('esforco_horas', '-')} h")
        print(f"Dependências: {tarefa.get('n_dependencias', '-')}")
        print(f"Status:      {tarefa['status']}")
    print()


def concluir_tarefa(tarefas):
    print("\n--- Concluir Tarefa ---")
    if not tarefas:
        print("Nenhuma tarefa cadastrada para concluir.\n")
        return
    try:
        numero = int(input("Digite o número da tarefa que deseja concluir: "))
        if 1 <= numero <= len(tarefas):
            tarefa = tarefas[numero - 1]
            if tarefa["status"] == "Concluída":
                print(f"\nA tarefa ({tarefa['titulo']}) já está concluída!\n")
            else:
                tarefa["status"] = "Concluída"
                tarefa["concluida_em"] = datetime.date.today().isoformat()
                storage.salvar_tarefas(tarefas)
                print(f"\nSucesso! A tarefa ({tarefa['titulo']}) foi marcada como Concluída.\n")
        else:
            print("Erro! Número de tarefa inválido.\n")
    except ValueError:
        print("Erro! Por favor, digite um número inteiro.\n")


def exibir_resumo(tarefas):
    print()
    print(notificar.formatar_resumo(notificar.gerar_resumo(tarefas)))
    print()


def exibir_menu():
    print("="*30)
    print("        TaskTracker — Menu")
    print("="*30)
    print("1.Cadastrar nova tarefa")
    print("2.Visualizar tarefas cadastradas")
    print("3.Concluir uma tarefa")
    print("4.Resumo das tarefas")
    print("5.Sair da aplicação")
    print("="*30)


def main():
    tarefas = storage.carregar_tarefas()
    modelo = priorizacao.carregar_modelo()

    print("Bem-vindo ao TaskTracker!")
    if tarefas:
        print(f"{len(tarefas)} tarefa(s) carregada(s).")
    if modelo:
        print("Modelo de sugestão de prioridade carregado.")
    print()

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            cadastrar_tarefa(tarefas, modelo)
        elif opcao == "2":
            listar_tarefas(tarefas)
        elif opcao == "3":
            concluir_tarefa(tarefas)
        elif opcao == "4":
            exibir_resumo(tarefas)
        elif opcao == "5":
            print("\nEncerrando a aplicação.")
            break
        else:
            print("Erro! Opção inválida. Digite os números 1, 2, 3, 4 ou 5.\n")


if __name__ == "__main__":
    main()
