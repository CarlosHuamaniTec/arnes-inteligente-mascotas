# Arnés Inteligente para Mascotas - Backend 🐾

Backend desarrollado en **Django + Django REST Framework (DRF)** para el proyecto académico **Arnés Inteligente para Mascotas**.

Este backend ofrece funcionalidades de registro y autenticación de usuarios, con generación de tokens para acceso seguro desde una aplicación móvil.

---

## 🧱 Tecnologías usadas

- **Python 3.13.0**
- **Django 5.2.1**
- **Django REST Framework**
- **Token Authentication**
- **SQLite**

---

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
{
  "email": "juan@api.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "phone": "+51999999999",
  "city": "Lima",
  "password": "mipassword123"
}
#### Respuesta exitosa:
{
  "message": "Usuario creado exitosamente"
}

#### 2. Inicio de Sesión
- **URL:** `POST /api/auth/login/`
- **Datos requeridos:**
  - `email`
  - `password`
#### Ejemplo de solicitud:
{
  "email": "juan@api.com",
  "password": "mipassword123"
}
#### Respuesta exitosa:
{
  "message": "Inicio de sesión exitoso",
  "token": "9876543210abcdef1234567890abcdef12345678",
  "user_email": "juan@api.com",
  "user_id": 1
}