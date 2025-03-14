import sqlite3
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Criar banco de dados (caso não exista)
def criar_banco():
    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            descricao TEXT,
            quantidade INTEGER NOT NULL,
            data_entrada TEXT,
            data_saida TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Função para exportar para CSV
def exportar_para_csv():
    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM estoque")
    dados = cursor.fetchall()
    conn.close()

    if not dados:
        messagebox.showwarning("Aviso", "Não há dados para exportar!")
        return

    # Definir local para salvar o arquivo
    arquivo = filedialog.asksaveasfilename(defaultextension=".csv",
                                           filetypes=[("Arquivos CSV", "*.csv")],
                                           title="Salvar arquivo CSV")

    if not arquivo:
        return  # Usuário cancelou

    # Escrever os dados no arquivo CSV
    with open(arquivo, mode="w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["ID", "Tipo", "Descrição", "Quantidade", "Data Entrada", "Data Saída"])  # Cabeçalhos
        escritor.writerows(dados)

    messagebox.showinfo("Sucesso", f"Dados exportados com sucesso para {arquivo}!")

# Função para registrar entrada de itens
def registrar_entrada():
    tipo = tipo_entry.get()
    descricao = descricao_entry.get()
    try:
        quantidade = int(quantidade_entry.get())
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser positiva.")
    except ValueError:
        messagebox.showerror("Erro", "Digite uma quantidade válida!")
        return

    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, quantidade FROM estoque WHERE tipo = ? AND descricao = ?", (tipo, descricao))
    resultado = cursor.fetchone()

    if resultado:
        id_item = resultado[0]
        nova_quantidade = resultado[1] + quantidade
        cursor.execute("UPDATE estoque SET quantidade = ?, data_entrada = datetime('now') WHERE id = ?", 
                       (nova_quantidade, id_item))
    else:
        cursor.execute("INSERT INTO estoque (tipo, descricao, quantidade, data_entrada) VALUES (?, ?, ?, datetime('now'))",
                       (tipo, descricao, quantidade))

    conn.commit()
    conn.close()

    messagebox.showinfo("Sucesso", "Entrada registrada com sucesso!")
    atualizar_lista()

# Função para registrar saída de itens
def registrar_saida():
    try:
        id_item = int(id_saida_entry.get())
        quantidade = int(quantidade_saida_entry.get())
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser positiva.")
    except ValueError:
        messagebox.showerror("Erro", "Digite valores numéricos válidos!")
        return

    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT quantidade FROM estoque WHERE id = ?", (id_item,))
    resultado = cursor.fetchone()
    
    if resultado and resultado[0] >= quantidade:
        nova_quantidade = resultado[0] - quantidade
        if nova_quantidade > 0:
            cursor.execute("UPDATE estoque SET quantidade = ?, data_saida = datetime('now') WHERE id = ?", 
                           (nova_quantidade, id_item))
        else:
            cursor.execute("DELETE FROM estoque WHERE id = ?", (id_item,))
        
        conn.commit()
        messagebox.showinfo("Sucesso", "Saída registrada com sucesso!")
    else:
        messagebox.showerror("Erro", "Quantidade insuficiente ou item não encontrado.")

    conn.close()
    atualizar_lista()

# Função para listar estoque na interface
def atualizar_lista():
    # Limpar a lista antes de atualizar
    for row in estoque_tree.get_children():
        estoque_tree.delete(row)

    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM estoque")
    itens = cursor.fetchall()
    
    # Adicionar os itens ao Treeview
    for item in itens:
        estoque_tree.insert("", "end", values=(item[0], item[1], item[2], item[3], item[4], item[5]))

    conn.close()

# Criar banco de dados
criar_banco()

# Criando a interface principal
root = tk.Tk()
root.title("Controle de Estoque")
root.geometry("800x600")


# Seção de Entrada de Itens

frame_entrada = tk.LabelFrame(root, text="Registrar Entrada", padx=10, pady=10)
frame_entrada.pack(padx=10, pady=5, fill="x")

tk.Label(frame_entrada, text="Tipo:").grid(row=0, column=0)
tipo_entry = tk.Entry(frame_entrada)
tipo_entry.grid(row=0, column=1)

tk.Label(frame_entrada, text="Descrição:").grid(row=1, column=0)
descricao_entry = tk.Entry(frame_entrada)
descricao_entry.grid(row=1, column=1)

tk.Label(frame_entrada, text="Quantidade:").grid(row=2, column=0)
quantidade_entry = tk.Entry(frame_entrada)
quantidade_entry.grid(row=2, column=1)

tk.Button(frame_entrada, text="Registrar Entrada", command=registrar_entrada).grid(row=3, column=0, columnspan=2, pady=5)

# Seção de Saida de Itens

frame_saida = tk.LabelFrame(root, text="Registrar Saída", padx=10, pady=10)
frame_saida.pack(padx=10, pady=5, fill="x")

tk.Label(frame_saida, text="ID do Item:").grid(row=0, column=0)
id_saida_entry = tk.Entry(frame_saida)
id_saida_entry.grid(row=0, column=1)

tk.Label(frame_saida, text="Quantidade:").grid(row=1, column=0)
quantidade_saida_entry = tk.Entry(frame_saida)
quantidade_saida_entry.grid(row=1, column=1)

tk.Button(frame_saida, text="Registrar Saída", command=registrar_saida).grid(row=3, column=0, columnspan=2, pady=5)

# Seção de Estoque
frame_estoque = tk.LabelFrame(root, text="Estoque Atual", padx=10, pady=10)
frame_estoque.pack(padx=10, pady=5, fill="x")

# Criando Treeview para exibir o estoque
estoque_tree = ttk.Treeview(frame_estoque, columns=("ID", "Tipo", "Descrição", "Quantidade", "Data Entrada", "Data Saída"), show="headings")
estoque_tree.heading("ID", text="ID")
estoque_tree.heading("Tipo", text="Tipo")
estoque_tree.heading("Descrição", text="Descrição")
estoque_tree.heading("Quantidade", text="Quantidade")
estoque_tree.heading("Data Entrada", text="Data Entrada")
estoque_tree.heading("Data Saída", text="Data Saída")
estoque_tree.pack(fill="both", expand=True)

# Botão para exportar os dados para CSV
tk.Button(frame_estoque, text="Exportar para CSV", command=exportar_para_csv).pack(pady=5)

# Atualizar lista de estoque quando iniciar
atualizar_lista()

# Inicializar a interface gráfica
root.mainloop()