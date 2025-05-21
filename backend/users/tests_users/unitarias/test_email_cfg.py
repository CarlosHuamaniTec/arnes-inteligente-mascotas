from django.test import TestCase
from unittest.mock import patch
from users.utils.email import enviar_correo_confirmacion


class EmailSendControlFlowTest(TestCase):

    @patch('users.utils.email.send_mail')
    def test_envio_correo_con_datos_validos(self, mocked_send_mail):
        """
        [Caja Blanca - Flujo de Control] Cobertura de instrucciones y rutas
        
        Camino:
        Datos válidos → Se llama a send_mail() con parámetros correctos
        
        Cobertura:
        - Inicio y fin del flujo
        - Todos los nodos ejecutados
        """

        # Simular datos reales
        destinatario = "usuario@example.com"
        token = "abc123"

        # Llamada a la función
        enviar_correo_confirmacion(destinatario, token)

        # Verificar que send_mail haya sido llamado
        self.assertTrue(mocked_send_mail.called)

        # Obtener argumentos usados
        args, kwargs = mocked_send_mail.call_args

        # Validar contenido usando kwargs en lugar de args
        self.assertEqual(kwargs['subject'], "Confirma tu correo electrónico")
        self.assertIn(token, kwargs['message'])
        self.assertEqual(kwargs['recipient_list'], [destinatario])

    @patch('users.utils.email.send_mail', side_effect=Exception("Fallo de red"))
    def test_fallo_al_enviar_correo(self, mocked_send_mail):
        """
        [Caja Blanca - Flujo de Control] Manejo de fallos
        
        Camino:
        Excepción al llamar a send_mail() → Levanta error
        
        Cobertura:
        - Ruta alternativa con excepción
        """

        destinatario = "usuario@example.com"
        token = "abc123"

        # Act & Assert
        with self.assertRaises(Exception) as context:
            enviar_correo_confirmacion(destinatario, token)

        self.assertEqual(str(context.exception), "Fallo de red")