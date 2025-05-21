# backend/users/tests_user/unitarias/test_verify_emailcfg.py

from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from users.views import VerifyEmailView
from users.models import CustomUser


class VerifyEmailViewCFGTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = VerifyEmailView.as_view()

        # Crear usuario de prueba con token de verificación
        self.user = CustomUser.objects.create(
            email="test@example.com",
            first_name="Test",
            is_active=False,
            is_verified=False,
            verification_token="validtoken123"
        )
        self.user.set_password("password")
        self.user.save()

    def test_get_no_token_provided(self):
        """
        Caso sin token: debe retornar error con status 400.
        """
        request = self.factory.get('/verify-email/')
        response = self.view(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"No se proporcion\xF3 un token.", response.content)

    def test_get_token_invalid(self):
        """
        Token inválido → error 400.
        """
        request = self.factory.get('/verify-email/', {'token': 'invalidtoken'})
        response = self.view(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Token inv\xE1lido o expirado.", response.content)

    def test_get_token_valid(self):
        """
        Token válido → activa usuario, elimina token, status 200 y mensaje éxito.
        """
        request = self.factory.get('/verify-email/', {'token': 'validtoken123'})
        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertTrue(self.user.is_verified)
        self.assertIsNone(self.user.verification_token)

        self.assertIn(b"Correo verificado exitosamente", response.content)
        self.assertIn(b"Ahora puedes iniciar sesi\xF3n", response.content)
