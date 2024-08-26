import os
import sqlite3
import hashlib

def limpar_tela():
    """Limpa a tela do terminal."""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def conectar_db():
    """Conecta ao banco de dados SQLite."""
    return sqlite3.connect('cinema.db')

def inicializar_db():
    """Cria as tabelas no banco de dados se não existirem e adiciona alimentos predefinidos."""
    conn = conectar_db()
    cursor = conn.cursor()

    # Tabela de usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    # Tabela de filmes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS filmes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        sessao TEXT NOT NULL
    )
    ''')

    # Tabela de alimentos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL NOT NULL
    )
    ''')

    # Tabela de compras
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        filme TEXT,
        sessao TEXT,
        fileira TEXT,
        acento TEXT,
        valor_ingresso REAL,
        valor_alimento REAL,
        total_pagar REAL,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    ''')

    # Adiciona alimentos predefinidos
    adicionar_alimentos_predefinidos(cursor)

    conn.commit()
    conn.close()

def adicionar_alimentos_predefinidos(cursor):
    """Adiciona alimentos predefinidos ao banco de dados."""
    alimentos_predefinidos = [
        ("Refrigerante", 7.0),
        ("Pipoca Doce", 10.0),
        ("Pipoca Salgada", 10.0),
        ("Chocolate", 5.0),
        ("Bala", 3.0)
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO alimentos (nome, preco) VALUES (?, ?)
    ''', alimentos_predefinidos)

def hash_senha(senha):
    """Criptografa a senha usando SHA-256."""
    return hashlib.sha256(senha.encode()).hexdigest()

def cadastrar_usuario(username, password):
    """Cadastra um novo usuário no banco de dados."""
    conn = conectar_db()
    cursor = conn.cursor()

    hashed_password = hash_senha(password)

    try:
        cursor.execute('''
        INSERT INTO usuarios (username, password) VALUES (?, ?)
        ''', (username, hashed_password))
        conn.commit()
        print(f"Usuário {username} cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("Erro: Nome de usuário já existente.")
    finally:
        conn.close()

def fazer_login(username, password):
    """Verifica as credenciais do usuário e retorna o ID se o login for bem-sucedido."""
    conn = conectar_db()
    cursor = conn.cursor()

    hashed_password = hash_senha(password)

    cursor.execute('''
    SELECT id FROM usuarios WHERE username = ? AND password = ?
    ''', (username, hashed_password))

    user = cursor.fetchone()
    conn.close()

    if user:
        return user[0]  # Retorna o ID do usuário
    else:
        print("Login falhou! Usuário ou senha incorretos.")
        return None

def registrar_compra(usuario_id, filme, sessao, fileira, acento, valor_ingresso, valor_alimento, total_pagar):
    """Registra a compra de um ingresso no banco de dados."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO compras (usuario_id, filme, sessao, fileira, acento, valor_ingresso, valor_alimento, total_pagar)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (usuario_id, filme, sessao, fileira, acento, valor_ingresso, valor_alimento, total_pagar))
    conn.commit()
    conn.close()

def exibir_historico(usuario_id):
    """Exibe o histórico de compras de um usuário."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT filme, sessao, fileira, acento, valor_ingresso, valor_alimento, total_pagar
    FROM compras WHERE usuario_id = ?
    ''', (usuario_id,))
    compras = cursor.fetchall()
    conn.close()

    if compras:
        print("\nHistórico de Compras:")
        for compra in compras:
            print(f"\nFilme: {compra[0]}")
            print(f"Sessão: {compra[1]}")
            print(f"Fileira: {compra[2]}")
            print(f"Assento: {compra[3]}")
            print(f"Valor do ingresso: R$ {compra[4]:.2f}")
            print(f"Valor do alimento: R$ {compra[5]:.2f}")
            print(f"Total a pagar: R$ {compra[6]:.2f}")
    else:
        print("Nenhuma compra registrada.")

def escolher_opcoes():
    """Permite ao usuário escolher filme, fileira e assento."""
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM filmes')
    filmes = cursor.fetchall()

    if not filmes:
        print("Nenhum filme cadastrado. Por favor, contate um administrador.")
        conn.close()
        return None, None, None, None
    
    print("\nFilmes disponíveis:")
    for i, filme in enumerate(filmes, start=1):
        print(f"{i}. {filme[1]} - Sessão: {filme[2]}")

    while True:
        try:
            escolha_filme = int(input("Escolha o número do filme que deseja assistir: "))
            if 1 <= escolha_filme <= len(filmes):
                filme_escolhido = filmes[escolha_filme - 1]
                break
            else:
                print("Escolha inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, insira um número.")

    fileiras = ["A", "B", "C", "D", "E"]
    acentos = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

    print("\nFileiras disponíveis:")
    for i, fileira in enumerate(fileiras, start=1):
        print(f"{i}. {fileira}")

    while True:
        try:
            escolha_fileira = int(input("Escolha a fileira: "))
            if 1 <= escolha_fileira <= len(fileiras):
                fileira_escolhida = fileiras[escolha_fileira - 1]
                break
            else:
                print("Escolha inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, insira um número.")

    print("\nAssentos disponíveis:")
    for i, acento in enumerate(acentos, start=1):
        print(f"{i}. {acento}")

    while True:
        try:
            escolha_acento = int(input("Escolha o assento: "))
            if 1 <= escolha_acento <= len(acentos):
                acento_escolhido = acentos[escolha_acento - 1]
                break
            else:
                print("Escolha inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, insira um número.")

    conn.close()
    return filme_escolhido[1], filme_escolhido[2], fileira_escolhida, acento_escolhido

def cadastrar_filme():
    """Permite que um administrador adicione novos filmes ao sistema."""
    filme = input("Digite o nome do filme: ")
    sessao = input("Digite o horário da sessão (ex: 14:00): ")
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO filmes (nome, sessao) VALUES (?, ?)
    ''', (filme, sessao))
    conn.commit()
    conn.close()
    print(f"Filme '{filme}' na sessão '{sessao}' cadastrado com sucesso!")

def cadastrar_alimento():
    """Permite que um administrador adicione novos alimentos ao sistema."""
    nome = input("Digite o nome do alimento: ")
    preco = float(input("Digite o preço do alimento (em R$): "))
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO alimentos (nome, preco) VALUES (?, ?)
    ''', (nome, preco))
    conn.commit()
    conn.close()
    print(f"Alimento '{nome}' cadastrado com sucesso!")

def exibir_alimentos():
    """Exibe os alimentos disponíveis."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM alimentos')
    alimentos = cursor.fetchall()
    conn.close()

    if alimentos:
        print("\nAlimentos disponíveis:")
        for i, alimento in enumerate(alimentos, start=1):
            print(f"{i}. {alimento[1]} - R$ {alimento[2]:.2f}")
    else:
        print("Nenhum alimento cadastrado.")

def remover_filme():
    """Permite que um administrador remova um filme do sistema."""
    exibir_filmes()
    conn = conectar_db()
    cursor = conn.cursor()

    while True:
        try:
            escolha_filme = int(input("Escolha o número do filme que deseja remover (0 para cancelar): "))
            if escolha_filme == 0:
                break
            cursor.execute('SELECT * FROM filmes WHERE id = ?', (escolha_filme,))
            filme = cursor.fetchone()
            if filme:
                cursor.execute('DELETE FROM filmes WHERE id = ?', (escolha_filme,))
                conn.commit()
                print(f"Filme '{filme[1]}' removido com sucesso!")
                break
            else:
                print("Escolha inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, insira um número.")
    
    conn.close()

def remover_alimento():
    """Permite que um administrador remova um alimento do sistema."""
    exibir_alimentos()
    conn = conectar_db()
    cursor = conn.cursor()

    while True:
        try:
            escolha_alimento = int(input("Escolha o número do alimento que deseja remover (0 para cancelar): "))
            if escolha_alimento == 0:
                break
            cursor.execute('SELECT * FROM alimentos WHERE id = ?', (escolha_alimento,))
            alimento = cursor.fetchone()
            if alimento:
                cursor.execute('DELETE FROM alimentos WHERE id = ?', (escolha_alimento,))
                conn.commit()
                print(f"Alimento '{alimento[1]}' removido com sucesso!")
                break
            else:
                print("Escolha inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, insira um número.")
    
    conn.close()

def exibir_filmes():
    """Exibe os filmes disponíveis."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM filmes')
    filmes = cursor.fetchall()
    conn.close()

    if filmes:
        print("\nFilmes disponíveis:")
        for i, filme in enumerate(filmes, start=1):
            print(f"{i}. {filme[1]} - Sessão: {filme[2]}")
    else:
        print("Nenhum filme cadastrado.")

def escolher_alimentos():
    """Permite ao usuário escolher alimentos e calcular o valor total."""
    exibir_alimentos()
    conn = conectar_db()
    cursor = conn.cursor()
    alimentos_selecionados = []
    total_alimentos = 0.0

    while True:
        try:
            escolha_alimento = int(input("Escolha o número do alimento que deseja adicionar ao carrinho (0 para finalizar): "))
            if escolha_alimento == 0:
                break
            cursor.execute('SELECT * FROM alimentos WHERE id = ?', (escolha_alimento,))
            alimento = cursor.fetchone()
            if alimento:
                quantidade = int(input(f"Quantas unidades de {alimento[1]} você deseja? "))
                total_alimentos += alimento[2] * quantidade
                alimentos_selecionados.append((alimento[1], quantidade, alimento[2]))
            else:
                print("Escolha inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, insira um número.")

    conn.close()
    return alimentos_selecionados, total_alimentos

def main():
    """Função principal do programa."""
    inicializar_db()
    
    while True:
        limpar_tela()
        print("Bem-vindo ao sistema de cinema!")
        print("1. Cadastrar novo usuário")
        print("2. Fazer login")
        print("3. Cadastrar filme (Admin)")
        print("4. Cadastrar alimento (Admin)")
        print("5. Remover filme (Admin)")
        print("6. Remover alimento (Admin[Há repetição de alimentos.])")
        print("7. Sair")
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            username = input("Digite o nome de usuário: ")
            password = input("Digite a senha: ")
            cadastrar_usuario(username, password)
            input("Pressione Enter para continuar...")
        elif escolha == '2':
            username = input("Digite o nome de usuário: ")
            password = input("Digite a senha: ")
            usuario_id = fazer_login(username, password)
            
            if usuario_id:
                while True:
                    limpar_tela()
                    print("1. Escolher filme e comprar ingresso")
                    print("2. Ver histórico de compras")
                    print("3. Sair")
                    escolha_usuario = input("Escolha uma opção: ")

                    if escolha_usuario == '1':
                        filme, sessao, fileira, acento = escolher_opcoes()

                        if filme is None:
                            continue

                        carteira = int(input("Escolha o tipo de carteira (1: Estudante, 2: Inteira): "))
                        desconto = 30 if carteira == 1 else 0
                        valor_ingresso = 20.0 - (20.0 * desconto / 100)

                        alimentos_selecionados, total_alimentos = escolher_alimentos()

                        total_pagar = valor_ingresso + total_alimentos

                        print(f"\nDetalhes da compra:")
                        print(f"Filme: {filme}")
                        print(f"Sessão: {sessao}")
                        print(f"Fileira: {fileira}")
                        print(f"Assento: {acento}")
                        print(f"Valor do ingresso: R$ {valor_ingresso:.2f}")
                        print(f"Valor dos alimentos:")
                        for alimento in alimentos_selecionados:
                            print(f"{alimento[1]}x {alimento[0]}: R$ {alimento[1] * alimento[2]:.2f}")
                        print(f"Total a pagar: R$ {total_pagar:.2f}")

                        registrar_compra(usuario_id, filme, sessao, fileira, acento, valor_ingresso, total_alimentos, total_pagar)
                        input("\nPressione Enter para continuar...")
                    elif escolha_usuario == '2':
                        exibir_historico(usuario_id)
                        input("\nPressione Enter para continuar...")
                    elif escolha_usuario == '3':
                        break
            else:
                input("Pressione Enter para continuar...")
        elif escolha == '3':
            cadastrar_filme()
            input("Pressione Enter para continuar...")
        elif escolha == '4':
            cadastrar_alimento()
            input("Pressione Enter para continuar...")
        elif escolha == '5':
            remover_filme()
            input("Pressione Enter para continuar...")
        elif escolha == '6':
            remover_alimento()
            input("Pressione Enter para continuar...")
        elif escolha == '7':
            break
        else:
            print("Opção inválida. Tente novamente.")
            input("Pressione Enter para continuar...")

if __name__ == "__main__":
    main()