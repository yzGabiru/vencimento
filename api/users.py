from flask import Flask, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://vencimento.vercel.app"]}})

# Configuração do Firebase
cred = credentials.Certificate("C:\\Users\\Gabiru\\Desktop\\vencimento\\validade-74f73-firebase-adminsdk-d37x2-3a6db9e4ed.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def index():
    return "Server is running!"

# Buscar produtos
@app.route('/users', methods=['GET'])
def get_users():
    users_ref = db.collection("VALIDADE_PRODUTOS")
    users = users_ref.stream()
    products = [{doc.id: doc.to_dict()} for doc in users]
    return jsonify({"produtos": products})

# Verificar se o produto existe
@app.route('/users/<codigo_barra>', methods=['GET'])
def check_product(codigo_barra):
    doc_ref = db.collection("VALIDADE_PRODUTOS").document(codigo_barra)
    product = doc_ref.get()
    if product.exists:
        return jsonify({"NOME_PRODUTO": product.to_dict()['NOME_PRODUTO']}), 200
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

    # Inserindo o produto na coleção
    db.collection("VALIDADE_PRODUTOS").document(codigo_barra).set({
        "NOME_PRODUTO": nome_produto,
        "QUANTIDADE_PRODUTO": quantidade,
        "VALIDADE": validade_produto
    })
    
    return jsonify({"message": "Produto cadastrado com sucesso."}), 201

# Deletar produto
@app.route('/users', methods=['DELETE'])
def delete_user():
    codigo_barra = request.json.get('CODIGO_BARRA')
    
    if not codigo_barra:
        return jsonify({"error": "Código de barras é obrigatório."}), 400

    # Verificando se o produto existe antes de deletar
    doc_ref = db.collection("VALIDADE_PRODUTOS").document(codigo_barra)
    if doc_ref.get().exists:
        doc_ref.delete()
        return jsonify({"message": "Produto deletado com sucesso."}), 200
    else:
        return jsonify({"error": "Produto não encontrado."}), 404

if __name__ == '__main__':
    app.run(debug=True)  # Use debug=False em produção
