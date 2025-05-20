# Arnés Inteligente para Mascotas - Backend 🐾

Backend desarrollado en **Django + Django REST Framework (DRF)** para el proyecto académico **Arnés Inteligente para Mascotas**.

Este backend ofrece funcionalidades de registro, inicio de sesión y generación de tokens para autenticación segura desde una aplicación móvil.

---

## 🧱 Tecnologías usadas

- **Python 3.13.0**
- **Django 5.2.1**
- **Django REST Framework**
- **Token Authentication**
- **SQLite**

## 🚀 Endpoints Disponibles

### 1. Registro de Usuario

- **URL:** `POST /api/auth/register/`
- **Datos requeridos:**
  - `email` (único)
  - `first_name`
  - `password`
- **Opcionales:**
  - `last_name`
  - `phone`
  - `city`

#### Ejemplo de solicitud:
json
{
  "email": "juan@api.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "phone": "+51999999999",
  "city": "Lima",
  "password": "mipassword123"
}

### 1. Registro de Usuario

- **URL:** `POST /api/auth/register/`
- **Datos requeridos:**
  - `email` (único)
  - `first_name`
  - `password`
- **Opcionales:**
  - `last_name`
  - `phone`
  - `city`

#### Ejemplo de solicitud:
json
{
  "email": "juan@api.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "phone": "+51999999999",
  "city": "Lima",
  "password": "mipassword123"
}
