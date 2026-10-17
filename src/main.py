"""
TaskTracker — Gerenciamento de tarefas.
Bootcamp II — Fase 2 (Entrega Intermediária)
"""

def ler_titulo():
    while True:
        titulo = input("Título da tarefa: ").strip()
        if titulo:
            return titulo
        print("Erro! O título é obrigatório e não pode ser vazio.\n")


def ler_prioridade():
    while True:
        prioridade = input("Prioridade (Alta / Média / Baixa): ").strip()
        prioridade_normalizada = prioridade.lower()
        if prioridade_normalizada in ("alta", "média", "media", "baixa"):
            if prioridade_normalizada == "alta":
                return "Alta"
            if prioridade_normalizada == "baixa":
                return "Baixa"
            return "Média"
        print("Erro! Prioridade inválida. Use apenas: Alta, Média ou Baixa.\n")


def cadastrar_tarefa(tarefas):
    print("\n--- Cadastro de nova tarefa ---")
    titulo = ler_titulo()
    descricao = input("Descrição: ").strip()
    prioridade = ler_prioridade()
    data_limite = input("Data limite (DD/MM/AAAA ou livre): ").strip()

    tarefa = {
        "titulo": titulo,
        "descricao": descricao if descricao else "(Sem descrição)",
        "prioridade": prioridade,
        "data_limite": data_limite if data_limite else "(Não informada)",
        "status": "Pendente",
    }
    tarefas.append(tarefa)
    print(f"\n[OK] Tarefa '{titulo}' cadastrada com sucesso!\n")


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
        print(f"Status:      {tarefa['status']}")
    print()


def exibir_menu():
    print("="*30)
    print("        TaskTracker — Menu")
    print("="*30)
    print("1.Cadastrar nova tarefa: ")
    print("2.Visualizar tarefas cadastradas: ")
    print("3.Sair da aplicação: ")
    print("="*30)


def main():
    tarefas = []
    print("Bem-vindo(a) ao TaskTracker!\n")

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            cadastrar_tarefa(tarefas)
        elif opcao == "2":
            listar_tarefas(tarefas)
        elif opcao == "3":
            print("\nEncerrando a aplicação.")
            break
        else:
            print("Erro! Opção inválida. Digite os números 1, 2 ou 3.\n")


if __name__ == "__main__":
    main()