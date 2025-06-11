import sqlite3
import os

caminho = os.path.join(os.getcwd(), 'tarefas.db')
conn = sqlite3.connect(caminho)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS tarefas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT,
    horario TEXT
)
''')

conn.commit()
conn.close()
print("Banco de dados e tabela criados com sucesso")
