import unittest
import json
from unittest.mock import patch, MagicMock
from flask import Flask, Request
from main import salvar_pedido

class TestSalvarPedido(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

    def test_salvar_pedido_opcoes(self):
        """Testa se a função responde corretamente a requisições OPTIONS"""
        with self.app.test_request_context('/pedidos', method="OPTIONS"):
            response = salvar_pedido(Request.from_values())
        
        self.assertEqual(response[1], 204)

    @patch("main.verificar_autenticacao")
    def test_salvar_pedido_sem_autenticacao(self, mock_verificar_autenticacao):
        """Testa se a função retorna erro quando o usuário não está autenticado"""
        mock_verificar_autenticacao.return_value = (None, json.dumps({"error": "Token de autenticação ausente ou inválido"}), 401)

        with self.app.test_request_context('/pedidos', method="POST", json={"cliente": "João", "email": "joao@email.com", "itens": []}):
            response = salvar_pedido(Request.from_values())
        
        self.assertEqual(response[1], 401)
        self.assertIn("Token de autenticação ausente ou inválido", response[0])

    @patch("main.verificar_autenticacao")
    def test_salvar_pedido_metodo_nao_permitido(self, mock_verificar_autenticacao):
        """Testa se a função retorna erro quando o método HTTP não é POST"""
        mock_verificar_autenticacao.return_value = ({"uid": "user123"}, None, 200)

        with self.app.test_request_context('/pedidos', method="GET"):
            response = salvar_pedido(Request.from_values())
        
        self.assertEqual(response[1], 405)
        self.assertIn("Método não permitido", response[0])

    @patch("main.verificar_autenticacao")
    def test_salvar_pedido_json_invalido(self, mock_verificar_autenticacao):
        """Testa se a função retorna erro quando o JSON enviado é inválido"""
        mock_verificar_autenticacao.return_value = ({"uid": "user123"}, None, 200)

        with self.app.test_request_context('/pedidos', method="POST", json=None):
            response = salvar_pedido(Request.from_values())
        
        self.assertEqual(response[1], 400)
        self.assertIn("JSON inválido ou não fornecido", response[0])

    @patch("main.verificar_autenticacao")
    def test_salvar_pedido_campos_obrigatorios_faltando(self, mock_verificar_autenticacao):
        """Testa se a função retorna erro quando campos obrigatórios estão faltando"""
        mock_verificar_autenticacao.return_value = ({"uid": "user123"}, None, 200)

        with self.app.test_request_context('/pedidos', method="POST", json={"cliente": "João"}):
            response = salvar_pedido(Request.from_values())
        
        self.assertEqual(response[1], 400)
        self.assertIn("Campos obrigatórios faltando", response[0])

    @patch("main.verificar_autenticacao")
    @patch("main.db.collection")
    def test_salvar_pedido_sucesso(self, mock_db_collection, mock_verificar_autenticacao):
        """Testa se a função salva um pedido com sucesso"""
        mock_verificar_autenticacao.return_value = ({"uid": "user123"}, None, 200)

        # Simula um documento no Firestore
        mock_doc_ref = MagicMock()
        mock_db_collection.return_value.document.return_value = mock_doc_ref

        pedido_exemplo = {
            "cliente": "João",
            "email": "joao@email.com",
            "itens": [{"quantidade": 2, "preco": 10.0}, {"quantidade": 1, "preco": 20.0}]
        }

        with self.app.test_request_context('/pedidos', method="POST", json=pedido_exemplo):
            response = salvar_pedido(Request.from_values())

        self.assertEqual(response[1], 200)
        self.assertIn("Pedido criado com sucesso", response[0])
        self.assertIn("PENDENTE", response[0])

    @patch("main.verificar_autenticacao")
    @patch("main.db.collection")
    def test_salvar_pedido_erro_interno(self, mock_db_collection, mock_verificar_autenticacao):
        """Testa se a função retorna erro interno ao acessar Firestore"""
        mock_verificar_autenticacao.return_value = ({"uid": "user123"}, None, 200)

        # Simula um erro ao acessar Firestore
        mock_db_collection.side_effect = Exception("Erro inesperado")

        pedido_exemplo = {
            "cliente": "João",
            "email": "joao@email.com",
            "itens": [{"quantidade": 1, "preco": 15.0}]
        }

        with self.app.test_request_context('/pedidos', method="POST", json=pedido_exemplo):
            response = salvar_pedido(Request.from_values())

        self.assertEqual(response[1], 500)
        self.assertIn("Erro inesperado", response[0])

if __name__ == '__main__':
    unittest.main()
