import unittest
import json
from unittest.mock import patch, MagicMock
from flask import Flask, Request
from main import listar_pedidos

class TestListarPedidos(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

    @patch("main.verificar_autenticacao")
    def test_listar_pedidos_sem_autenticacao(self, mock_verificar_autenticacao):
        """Testa se a função retorna erro quando o usuário não está autenticado"""
        mock_verificar_autenticacao.return_value = (None, json.dumps({"error": "Token de autenticação ausente ou inválido"}), 401)

        with self.app.test_request_context('/pedidos', method="GET"):
            response = listar_pedidos(Request.from_values())
        
        self.assertEqual(response[1], 401)
        self.assertIn("Token de autenticação ausente ou inválido", response[0])

    @patch("main.verificar_autenticacao")
    def test_listar_pedidos_metodo_nao_permitido(self, mock_verificar_autenticacao):
        """Testa se a função retorna erro quando o método HTTP não é GET"""
        mock_verificar_autenticacao.return_value = ({"uid": "user123"}, None, 200)

        with self.app.test_request_context('/pedidos', method="POST"):
            response = listar_pedidos(Request.from_values())
        
        self.assertEqual(response[1], 405)
        self.assertIn("Método não permitido", response[0])

    @patch("main.verificar_autenticacao")
    @patch("main.db.collection")
    def test_listar_pedidos_sucesso(self, mock_db_collection, mock_verificar_autenticacao):
        """Testa se a função retorna a lista de pedidos com sucesso"""
        mock_verificar_autenticacao.return_value = ({"uid": "user123"}, None, 200)

        # Simula pedidos existentes no Firestore
        mock_doc1 = MagicMock()
        mock_doc1.id = "pedido_1"
        mock_doc1.to_dict.return_value = {
            "status": "enviado",
            "total": 100.0,
            "data_criacao": "2023-03-01",
            "cliente": "João",
            "email": "joao@email.com",
            "itens": ["item1", "item2"]
        }

        mock_doc2 = MagicMock()
        mock_doc2.id = "pedido_2"
        mock_doc2.to_dict.return_value = {
            "status": "pendente",
            "total": 50.0,
            "data_criacao": "2023-03-02",
            "cliente": "Maria",
            "email": "maria@email.com",
            "itens": ["item3"]
        }

        mock_db_collection.return_value.stream.return_value = [mock_doc1, mock_doc2]

        with self.app.test_request_context('/pedidos', method="GET"):
            response = listar_pedidos(Request.from_values())
        
        self.assertEqual(response[1], 200)
        pedidos = json.loads(response[0])
        self.assertEqual(len(pedidos), 2)
        self.assertEqual(pedidos[0]["id"], "pedido_1")
        self.assertEqual(pedidos[1]["id"], "pedido_2")

    @patch("main.verificar_autenticacao")
    @patch("main.db.collection")
    def test_listar_pedidos_vazio(self, mock_db_collection, mock_verificar_autenticacao):
        """Testa se a função retorna uma lista vazia quando não há pedidos"""
        mock_verificar_autenticacao.return_value = ({"uid": "user123"}, None, 200)

        # Simula nenhum pedido no Firestore
        mock_db_collection.return_value.stream.return_value = []

        with self.app.test_request_context('/pedidos', method="GET"):
            response = listar_pedidos(Request.from_values())
        
        self.assertEqual(response[1], 200)
        pedidos = json.loads(response[0])
        self.assertEqual(len(pedidos), 0)

    @patch("main.verificar_autenticacao")
    @patch("main.db.collection")
    def test_listar_pedidos_erro_interno(self, mock_db_collection, mock_verificar_autenticacao):
        """Testa se a função retorna erro interno do servidor quando ocorre uma exceção"""
        mock_verificar_autenticacao.return_value = ({"uid": "user123"}, None, 200)

        # Simula um erro inesperado ao acessar o Firestore
        mock_db_collection.side_effect = Exception("Erro inesperado")

        with self.app.test_request_context('/pedidos', method="GET"):
            response = listar_pedidos(Request.from_values())
        
        self.assertEqual(response[1], 500)
        self.assertIn("Erro inesperado", response[0])

if __name__ == '__main__':
    unittest.main()
