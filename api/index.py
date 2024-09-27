import sys
import pyodbc
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permitir todas as origens

def get_db_connection():
    try:
        conn = pyodbc.connect(
            r'DRIVER={SQL Server};'
            r'SERVER=DESKTOP-RN5FHVV\SQLEXPRESS02;'
            r'DATABASE=VALIDADE;'
            r'TRUSTED_CONNECTION=yes;'
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

@app.route('/')
def index():
    return "Server is running!"

# Buscar produtos
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro de conexão com o banco de dados."}), 500

    cursor = conn.cursor()
    cursor.execute("SELECT CODIGO_VALIDADE, CODIGO_BARRA, NOME_PRODUTO, QUANTIDADE_PRODUTO, VALIDADE FROM VALIDADE_PRODUTOS")
    rows = cursor.fetchall()
    users = [{"CODIGO_VALIDADE": row[0], "CODIGO_BARRA": row[1], "NOME_PRODUTO": row[2], "QUANTIDADE_PRODUTO": row[3], "VALIDADE": row[4]} for row in rows]
    cursor.close()
    conn.close()
    return jsonify(users)

# Adicionar produto
@app.route('/api/users', methods=['POST'])
def add_user():
    productData = request.json
    codigo_barra = productData.get('CODIGO_BARRA')
    nome_produto = productData.get('NOME_PRODUTO')
    quantidade = productData.get('QUANTIDADE_PRODUTO')
    validade_produto = productData.get('VALIDADE')

    if not all([codigo_barra, quantidade, validade_produto]):
        return jsonify({"error": "Código de barras, quantidade e validade são obrigatórios"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro de conexão com o banco de dados."}), 500

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO VALIDADE_PRODUTOS (CODIGO_BARRA, NOME_PRODUTO, QUANTIDADE_PRODUTO, VALIDADE) VALUES (?, ?, ?, ?)", 
        (codigo_barra, nome_produto, quantidade, validade_produto)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"message": "Produto cadastrado com sucesso."}), 201

# Deletar produto
@app.route('/api/users/<codigo_validade>', methods=['DELETE'])
def delete_user(codigo_validade):
    if not codigo_validade:
        return jsonify({"error": "Código de validade é obrigatório."}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro de conexão com o banco de dados."}), 500

    cursor = conn.cursor()
    cursor.execute("DELETE FROM VALIDADE_PRODUTOS WHERE CODIGO_VALIDADE = ?", (codigo_validade,))
    if cursor.rowcount == 0:
        return jsonify({"error": "Produto não encontrado."}), 404

    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"message": "Produto deletado com sucesso."}), 200

if __name__ == '__main__':
    app.run(debug=True)
