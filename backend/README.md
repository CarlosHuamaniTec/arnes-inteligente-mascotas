# Backend - Arnés Inteligente para Mascotas 🐾

Backend desarrollado en **Django + Django REST Framework** para el proyecto académico "Arnés Inteligente para Mascotas".

Permite el registro e inicio de sesión de usuarios, con autenticación mediante token y confirmación de correo.

---

## 🧱 Tecnologías usadas

- Python 3.13.0
- Django 5.2.1
- Django REST Framework
- Token Authentication
- SMTP (Gmail) – Para confirmación de correo
- SQLite

---

## 🚀 Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Registra un nuevo usuario e inicia proceso de confirmación |
| `/api/auth/login/` | POST | Inicia sesión y devuelve un token |
| `/api/auth/verify-email/` | POST | Confirma el correo del usuario |

---

## 📦 Historias de Usuario Implementadas

| HU | Descripción |
|----|-------------|
| HU01 | Registro de usuario |
| HU02 | Inicio de sesión con correo y contraseña |
| HU10 | Confirmación de correo tras registro |

---

## 🛠️ Requisitos

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver