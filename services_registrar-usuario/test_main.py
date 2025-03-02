import unittest
import json
from unittest.mock import patch, MagicMock
from flask import Flask, Request
from main import register_user

class TestRegisterUser(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

    def test_register_user_opcoes(self):
        """Testa se a função responde corretamente a requisições OPTIONS"""
        with self.app.test_request_context('/register', method="OPTIONS"):
            response = register_user(Request.from_values())
        
        self.assertEqual(response[1], 204)

    def test_register_user_dados_faltando(self):
        """Testa se a função retorna erro quando email ou senha não são fornecidos"""
        with self.app.test_request_context('/register', method="POST", json={}):
            response = register_user(Request.from_values())
        
        self.assertEqual(response[1], 400)
        self.assertIn("Email e senha são obrigatórios", response[0])

    @patch("main.auth.create_user")
    def test_register_user_sucesso(self, mock_create_user):
        """Testa se a função registra um usuário com sucesso"""
        mock_user = MagicMock()
        mock_user.uid = "user123"
        mock_create_user.return_value = mock_user

        with self.app.test_request_context('/register', method="POST", json={"email": "teste@email.com", "password": "senha123"}):
            response = register_user(Request.from_values())

        self.assertEqual(response[1], 201)
        self.assertIn("Usuário criado com sucesso", response[0])
        self.assertIn("user123", response[0])

    @patch("main.auth.create_user")
    def test_register_user_erro_criacao(self, mock_create_user):
        """Testa se a função retorna erro ao tentar criar um usuário"""
        mock_create_user.side_effect = Exception("Erro ao criar usuário")

        with self.app.test_request_context('/register', method="POST", json={"email": "teste@email.com", "password": "senha123"}):
            response = register_user(Request.from_values())

        self.assertEqual(response[1], 500)
        self.assertIn("Erro ao criar usuário", response[0])

if __name__ == '__main__':
    unittest.main()
