from django.test import TestCase
from unittest.mock import patch
from users.utils.email import enviar_correo_confirmacion

class EmailSendControlFlowTest(TestCase):

    @patch('users.utils.email.send_mail')
    def test_envio_correo_con_datos_validos(self, mocked_send_mail):
        """
        [Caja Blanca - Flujo de Control] Cobertura de instrucciones y rutas

        Ruta: Todos los pasos normales sin excepciones
        Instrucciones cubiertas:
            1. Definición de asunto
            2. Generación de mensaje
            3. Uso de DEFAULT_FROM_EMAIL
            4. Envío de correo
        """

        destinatario = "usuario@example.com"
        token = "abc123"

        # Act
        enviar_correo_confirmacion(destinatario, token)

        # Asserts
        self.assertTrue(mocked_send_mail.called)
        args, kwargs = mocked_send_mail.call_args

        self.assertEqual(args[0], "Confirma tu correo electrónico")
        self.assertIn(token, args[1])
        self.assertEqual(args[3], [destinatario])

    @patch('users.utils.email.send_mail', side_effect=Exception("Fallo de red"))
    def test_fallo_al_enviar_correo(self, mocked_send_mail):
        """
        [Caja Blanca - Flujo de Control] Manejo de fallos

        Ruta: Excepción al llamar a send_mail()
        Verifica que la función maneje correctamente un fallo en el envío.
        """

        destinatario = "usuario@example.com"
        token = "abc123"

        # Act & Assert
        with self.assertRaises(Exception) as context:
            enviar_correo_confirmacion(destinatario, token)

        self.assertEqual(str(context.exception), "Fallo de red")