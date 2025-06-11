import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import os
import datetime

import sys

def conectar_db():
    if getattr(sys, 'frozen', False):  # Se for .exe
        base_path = sys._MEIPASS
    else:  # Se for .py
        base_path = os.getcwd()
    caminho = os.path.join(base_path, 'tarefas.db')
    return sqlite3.connect(caminho)


def inicializar_db():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            horario TEXT
        )
    """)
    conn.commit()
    conn.close()


def carregar_tarefas():
    lista_tarefas.delete(0, tk.END)
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo FROM tarefas")
    for tarefa in cursor.fetchall():
        lista_tarefas.insert(tk.END, f"{tarefa[0]} - {tarefa[1]}")
    conn.close()

def adicionar_tarefa():
    titulo = entrada_tarefa.get()
    descricao = entrada_descricao.get()
    horario = entrada_horario.get()
    if titulo.strip() == "":
        messagebox.showwarning("Aviso", "Digite um título para a tarefa.")
        return
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tarefas (titulo, descricao, horario) VALUES (?, ?, ?)",
                   (titulo, descricao, horario))
    conn.commit()
    conn.close()
    entrada_tarefa.delete(0, tk.END)
    entrada_descricao.delete(0, tk.END)
    entrada_horario.delete(0, tk.END)
    carregar_tarefas()

def excluir_tarefa():
    try:
        selecionado = lista_tarefas.get(lista_tarefas.curselection())
    except tk.TclError:
        messagebox.showwarning("Aviso", "Selecione uma tarefa para excluir.")
        return
    tarefa_id = int(selecionado.split(" - ")[0])
    resposta = messagebox.askyesno("Confirmar", "Tem certeza que quer excluir essa tarefa?")
    if resposta:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
        conn.commit()
        conn.close()
        carregar_tarefas()

def editar_tarefa():
    try:
        selecionado = lista_tarefas.get(lista_tarefas.curselection())
    except tk.TclError:
        messagebox.showwarning("Aviso", "Selecione uma tarefa para editar.")
        return
    tarefa_id, titulo_atual = selecionado.split(" - ", 1)
    novo_titulo = simpledialog.askstring("Editar tarefa", "Digite o novo título:", initialvalue=titulo_atual)
    if novo_titulo and novo_titulo.strip():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE tarefas SET titulo = ? WHERE id = ?", (novo_titulo.strip(), tarefa_id))
        conn.commit()
        conn.close()
        carregar_tarefas()

def mostrar_detalhes(event):
    selecao = lista_tarefas.curselection()
    if not selecao:
        return
    indice = selecao[0]
    item = lista_tarefas.get(indice)
    tarefa_id = item.split(" - ")[0]
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT titulo, descricao, horario FROM tarefas WHERE id=?", (tarefa_id,))
    tarefa = cursor.fetchone()
    conn.close()
    if tarefa:
        janela_editar = tk.Toplevel()
        janela_editar.title("Editar Tarefa")
        janela_editar.configure(bg='#2b2b2b')

        ttk.Label(janela_editar, text="Título:").pack()
        entrada_titulo = ttk.Entry(janela_editar, width=40)
        entrada_titulo.insert(0, tarefa[0])
        entrada_titulo.pack()

        ttk.Label(janela_editar, text="Descrição:").pack()
        entrada_descricao = ttk.Entry(janela_editar, width=40)
        entrada_descricao.insert(0, tarefa[1])
        entrada_descricao.pack()

        ttk.Label(janela_editar, text="Horário:").pack()
        entrada_horario = ttk.Entry(janela_editar, width=40)
        entrada_horario.insert(0, tarefa[2])
        entrada_horario.pack()

        def salvar_alteracoes():
            novo_titulo = entrada_titulo.get()
            nova_descricao = entrada_descricao.get()
            novo_horario = entrada_horario.get()
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tarefas SET titulo=?, descricao=?, horario=?
                WHERE id=?
            """, (novo_titulo, nova_descricao, novo_horario, tarefa_id))
            conn.commit()
            conn.close()
            janela_editar.destroy()
            carregar_tarefas()

        ttk.Button(janela_editar, text="Salvar alterações", command=salvar_alteracoes).pack(pady=10)

def checar_avisos():
    agora = datetime.datetime.now()
    limite = agora + datetime.timedelta(hours=1)  # mudou para 1 hora

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT titulo, horario FROM tarefas")
    tarefas = cursor.fetchall()
    conn.close()

    for titulo, horario_str in tarefas:
        try:
            horario = datetime.datetime.strptime(horario_str, "%Y-%m-%d %H:%M")
        except:
            continue

        if agora < horario <= limite:
            messagebox.showinfo("Aviso de tarefa", f"A tarefa '{titulo}' está marcada para {horario_str} (menos de 1 hora).")

    janela.after(60000, checar_avisos)


    # chama essa função de novo após 1 minuto (60000 ms)
    janela.after(60000, checar_avisos)

# ==== Janela principal ====
janela = tk.Tk()
janela.title("Lista de Tarefas")
janela.configure(bg='#2b2b2b')

style = ttk.Style()
style.theme_use('clam')

style.configure("TLabel", background="#2b2b2b", foreground="white")
style.configure("TButton", background="#3c3f41", foreground="white", padding=6)
style.configure("TEntry", fieldbackground="#3c3f41", foreground="white")

ttk.Label(janela, text="Título:").pack()
entrada_tarefa = ttk.Entry(janela, width=40)
entrada_tarefa.pack(pady=5)

ttk.Label(janela, text="Descrição:").pack()
entrada_descricao = ttk.Entry(janela, width=40)
entrada_descricao.pack(pady=5)

ttk.Label(janela, text="Horário:").pack()
entrada_horario = ttk.Entry(janela, width=40)
entrada_horario.pack(pady=5)

ttk.Button(janela, text="Adicionar Tarefa", command=adicionar_tarefa).pack(pady=5)
ttk.Button(janela, text="Editar Tarefa", command=editar_tarefa).pack(pady=5)
ttk.Button(janela, text="Excluir Tarefa", command=excluir_tarefa).pack(pady=5)

lista_tarefas = tk.Listbox(janela, width=50, bg="#3c3f41", fg="white", selectbackground="#555555")
lista_tarefas.pack(pady=10)
lista_tarefas.bind("<Double-Button-1>", mostrar_detalhes)

inicializar_db()  # <<<< Aqui
carregar_tarefas()
checar_avisos()
janela.mainloop()






