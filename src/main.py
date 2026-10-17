"""
TaskTracker — Gerenciamento de tarefas.
Bootcamp II — Fase 2 (Entrega Intermediária)
"""
import datetime

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

def cadastrar_tarefa(tarefas):
    print("\n--- Cadastro de nova tarefa ---")
    titulo = ler_titulo()
    descricao = input("Descrição: ").strip()
    prioridade = ler_prioridade()
    data_limite = ler_data()

    tarefa = {
        "titulo": titulo,
        "descricao": descricao if descricao else "(Sem descrição)",
        "prioridade": prioridade,
        "data_limite": data_limite,
        "status": "Pendente",
    }
    tarefas.append(tarefa)
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
                print(f"\nSucesso! A tarefa ({tarefa['titulo']}) foi marcada como Concluída.\n")
        else:
            print("Erro! Número de tarefa inválido.\n")
    except ValueError:
        print("Erro! Por favor, digite um número inteiro.\n")

def exibir_menu():
    print("="*30)
    print("        TaskTracker — Menu")
    print("="*30)
    print("1.Cadastrar nova tarefa")
    print("2.Visualizar tarefas cadastradas")
    print("3.Concluir uma tarefa")
    print("4.Sair da aplicação")
    print("="*30)


def main():
    tarefas = []
    print("Bem-vindo ao TaskTracker!\n")

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            cadastrar_tarefa(tarefas)
        elif opcao == "2":
            listar_tarefas(tarefas)
        elif opcao == "3":
            concluir_tarefa(tarefas)
        elif opcao == "4":
            print("\nEncerrando a aplicação.")
            break
        else:
            print("Erro! Opção inválida. Digite os números 1, 2, 3 ou 4.\n")

if __name__ == "__main__":
    main()