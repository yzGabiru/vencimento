import sys
sys.path.append(r"C:\Users\Gabiru\AppData\Local\Programs\Python\Python311\Lib\site-packages")
from flask import Flask, jsonify, request
from flask_cors import CORS
import pyodbc

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})  # Permitir a origem correta

def get_db_connection():
    conn = pyodbc.connect(
        r'DRIVER={SQL Server};'
        r'SERVER=DESKTOP-RN5FHVV\SQLEXPRESS02;'
        r'DATABASE=VALIDADE;'
        r'TRUSTED_CONNECTION=yes;'
    )
    return conn

@app.route('/')
def index():
    return "Server is running!"

# Buscar produtos
@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT CODIGO_VALIDADE, CODIGO_BARRA, NOME_PRODUTO, QUANTIDADE_PRODUTO, VALIDADE FROM VALIDADE_PRODUTOS")
    rows = cursor.fetchall()
    users = [{"CODIGO_VALIDADE": row[0], "CODIGO_BARRA": row[1], "NOME_PRODUTO": row[2], "QUANTIDADE_PRODUTO": row[3], "VALIDADE": row[4]} for row in rows]
    cursor.close()
    conn.close()
    return jsonify(users)

# Verificar se o produto existe
@app.route('/users/<codigo_barra>', methods=['GET'])
def check_product(codigo_barra):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT NOME_PRODUTO FROM VALIDADE_PRODUTOS WHERE CODIGO_BARRA = ?", (codigo_barra,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    if product:
        return jsonify({"NOME_PRODUTO": product[0]}), 200
    else:
        return jsonify({"error": "Produto não encontrado."}), 404

# Adicionar produto
@app.route('/users', methods=['POST'])
def add_user():
    productData = request.json
    codigo_barra = productData.get('CODIGO_BARRA')
    nome_produto = productData.get('NOME_PRODUTO')
    quantidade = productData.get('QUANTIDADE_PRODUTO')
    validade_produto = productData.get('VALIDADE')

    if not all([codigo_barra, quantidade, validade_produto]):
        return jsonify({"error": "Código de barras, quantidade e validade são obrigatórios"}), 400

    conn = get_db_connection()
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
@app.route('/users', methods=['DELETE'])
def delete_user():
    codigo_validade = request.json.get('CODIGO_VALIDADE')  # Corrigido para CODIGO_VALIDADE
    
    if not codigo_validade:
        return jsonify({"error": "Código de validade é obrigatório."}), 400

    conn = get_db_connection()
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
