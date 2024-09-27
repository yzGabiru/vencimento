from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://vencimento.vercel.app"]}})

# Configurações do Supabase
url = "https://jrsuxglwohshxxikzydj.supabase.co/"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impyc3V4Z2x3b2hzaHh4aWt6eWRqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjc0NjkyMzUsImV4cCI6MjA0MzA0NTIzNX0.6R0X1dtT2V7EAgpIEiDZt0tUmOVtXiFlQlNvyOyG-MI"
supabase: Client = create_client(url, key)

@app.route('/')
def index():
    return "Server is running!"

# Buscar produtos
@app.route('/users', methods=['GET'])
def get_users():
    response = supabase.table("VALIDADE_PRODUTOS").select("*").execute()
    users = response.data
    return jsonify(users)

# Verificar se o produto existe
@app.route('/users/<codigo_barra>', methods=['GET'])
def check_product(codigo_barra):
    response = supabase.table("VALIDADE_PRODUTOS").select("NOME_PRODUTO").eq("CODIGO_BARRA", codigo_barra).execute()
    product = response.data
    if product:
        return jsonify({"NOME_PRODUTO": product[0]['NOME_PRODUTO']}), 200
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

    # Inserindo o produto na tabela
    supabase.table("VALIDADE_PRODUTOS").insert({
        "CODIGO_BARRA": codigo_barra,
        "NOME_PRODUTO": nome_produto,
        "QUANTIDADE_PRODUTO": quantidade,
        "VALIDADE": validade_produto
    }).execute()
    
    return jsonify({"message": "Produto cadastrado com sucesso."}), 201

# Deletar produto
@app.route('/users', methods=['DELETE'])
def delete_user():
    codigo_validade = request.json.get('CODIGO_VALIDADE')
    
    if not codigo_validade:
        return jsonify({"error": "Código de validade é obrigatório."}), 400

    # Deletando o produto da tabela
    response = supabase.table("VALIDADE_PRODUTOS").delete().eq("CODIGO_VALIDADE", codigo_validade).execute()
    if response.data:
        return jsonify({"message": "Produto deletado com sucesso."}), 200
    else:
        return jsonify({"error": "Produto não encontrado."}), 404

if __name__ == '__main__':
    app.run(debug=True)
