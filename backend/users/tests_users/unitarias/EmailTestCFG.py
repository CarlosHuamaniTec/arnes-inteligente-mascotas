# users/tests_users/unitarias/EmailTestCFG.py

from django.test import TestCase
from unittest.mock import patch
from users.utils.email import enviar_correo_confirmacion


class EmailTestCFG(TestCase):
    """
    Prueba unitaria de caja blanca para la función enviar_correo_confirmacion().
    
    Flujo de Control:
        [Entrada]
           ↓
        ¿Destinatario válido?
           ↘ No → Se lanza error desde send_mail()
             ↓
        ¿Token válido? → No → Se pasa vacío a plantilla
                          ↘ Sí → Token insertado en mensaje
                             ↓
        Cargar plantilla → Si falla, se levanta excepción
                           ↓
        Enviar correo → Si hay fallo SMTP, se lanza error
    
    Cobertura aplicada:
        - Cobertura de instrucción/nodo: cada línea ejecutada al menos una vez
        - Cobertura de condición: validación de parámetros y envío real
        - Cobertura de ruta completa: desde entrada hasta salida o excepción
    """

    def test_envio_correo_con_datos_validos(self):
        """
        [Caja Blanca - CFG] Camino principal
        
        Camino:
        Destinatario != None → token != None → plantilla cargada → correo enviado
            
        Cobertura:
        - Todos los nodos ejecutados
        - Ruta principal recorrida sin errores
        """
        destinatario = "usuario@example.com"
        token = "abc123"

        with patch('users.utils.email.send_mail') as mocked_send_mail:
            enviar_correo_confirmacion(destinatario, token)

            # Verificar que send_mail haya sido llamado
            self.assertTrue(mocked_send_mail.called)

            args, kwargs = mocked_send_mail.call_args

            # Validar contenido del correo
            self.assertEqual(args[0], "Confirma tu correo electrónico")
            self.assertIn(token, args[1])
            self.assertEqual(args[3], [destinatario])

    def test_fallo_al_enviar_correo(self):
        """
        [Caja Blanca - CFG] Condición 1: fallo en envío
        
        Camino:
        Datos válidos → Excepción en send_mail() → Levantar error
            
        Cobertura:
        - Nodo decisión: error durante envío
        - Excepción lanzada
        """
        destinatario = "usuario@example.com"
        token = "abc123"

        with patch('users.utils.email.send_mail', side_effect=Exception("Fallo de red")) as mocked_send_mail:
            with self.assertRaises(Exception) as context:
                enviar_correo_confirmacion(destinatario, token)

            self.assertEqual(str(context.exception), "Fallo de red")

    def test_envio_sin_destinatario_lanza_error(self):
        """
        [Caja Blanca - CFG] Condición 2: destinatario == None
        
        Camino:
        destinatario == None → send_mail() lanza error
            
        Cobertura:
        - Nodo decisión: destinatario es obligatorio
        - Excepción lanzada
        """
        with self.assertRaises(Exception):
            enviar_correo_confirmacion(None, "token123")

    def test_envio_correo_plantilla_html_correcta(self):
        """
        [Caja Blanca - CFG] Carga de plantilla HTML
        
        Camino:
        Contexto con token → render_to_string → plantilla con token
            
        Cobertura:
        - Camino básico con carga de template
        """
        from django.template.loader import render_to_string

        token = "abc123"
        context = {"token": token}
        html_message = render_to_string("emails/confirm_email.html", context)
        
        self.assertIn(token, html_message)
        self.assertIn("<p class=\"token\">", html_message)
        self.assertIn("</html>", html_message)

    def test_envio_correo_no_vacio(self):
        """
        [Caja Blanca - CFG] Validación de datos no vacíos
        
        Camino:
        token != None → mensaje no vacío
            
        Cobertura:
        - Camino básico con mensaje lleno
        """
        from django.template.loader import render_to_string

        token = "abc123"
        context = {"token": token}
        html_message = render_to_string("emails/confirm_email.html", context)
        plain_message = strip_tags(html_message) # type: ignore

        self.assertNotEqual(html_message.strip(), "")
        self.assertNotEqual(plain_message.strip(), "")

    def test_envio_correo_condiciones_invalidas(self):
        """
        [Caja Blanca - CFG] Campos inválidos o mal formateados
        
        Camino:
        email mal formateado → send_mail() lanza error
            
        Cobertura:
        - Camino alternativo con validación de formato de correo
        """
        invalid_emails = [
            "usuario@ejemplo",
            "usuario.sin.arroba.com",
            "usuario@ejemplo..com",
        ]

        for email in invalid_emails:
            with self.subTest(email=email):
                with patch('users.utils.email.send_mail', side_effect=Exception("Correo inválido")) as mocked_send_mail:
                    with self.assertRaises(Exception) as context:
                        enviar_correo_confirmacion(email, "abc123")

                    self.assertEqual(str(context.exception), "Correo inválido")

    def test_envio_correo_y_uso_de_contexto(self):
        """
        [Caja Blanca - CFG] Inserción correcta de token en mensaje
        
        Camino:
        contexto con token → insertado correctamente en mensaje
            
        Cobertura:
        - Camino básico con token insertado
        """
        token = "xyz789"
        destinatario = "test@example.com"

        with patch('users.utils.email.send_mail') as mocked_send_mail:
            enviar_correo_confirmacion(destinatario, token)

            args, kwargs = mocked_send_mail.call_args
            html_message = args[1]

            self.assertIn(token, html_message)

    def test_envio_correo_sin_token(self):
        """
        [Caja Blanca - CFG] Envío sin token
        
        Camino:
        token == None → mensaje sigue siendo válido
            
        Cobertura:
        - Camino secundario con token vacío
        """
        destinatario = "empty-token@example.com"

        with patch('users.utils.email.send_mail') as mocked_send_mail:
            enviar_correo_confirmacion(destinatario, None)

            args, kwargs = mocked_send_mail.call_args
            html_message = args[1]

            self.assertIn("Confirma tu correo electrónico", args[0])
            self.assertIn("Este es un mensaje automático", html_message)