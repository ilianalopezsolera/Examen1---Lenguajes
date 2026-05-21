# Sistema de Gestión de Evidencias - Examen 1

Este proyecto consiste en una API REST desarrollada con el framework Django y Django REST Framework (DRF), diseñada para automatizar, almacenar y controlar el registro de evidencias académicas o empresariales. El sistema cuenta con almacenamiento de archivos en la nube, autenticación segura y un flujo de integración continua.

---

## Características Principales

* **Gestión del CRUD de Evidencias:** Endpoints desarrollados para la creación, lectura, actualización y eliminación de registros de evidencias en la base de datos de forma relacional.
* **Almacenamiento en la Nube:** Integración con el servicio de Cloudinary para la carga, gestión y visualización segura de archivos multimedia y documentos adjuntos a las evidencias.
* **Seguridad y Autenticación Doble:** Acceso restringido mediante el uso de tokens seguros tradicionales y de terceros.
* **Validación Automatizada (CI/CD):** Configuración de flujos de trabajo con GitHub Actions para garantizar la estabilidad del código en cada integración.

---

## Arquitectura y Tecnologías Utilizadas

* **Backend:** Python, Django, Django REST Framework (DRF)
* **Base de Datos:** SQLite (Entorno de desarrollo local)
* **Autenticación:** Simple JWT (JSON Web Tokens) y Google OAuth 2.0
* **Almacenamiento de Archivos:** Cloudinary SDK
* **Lector de Entornos:** Python-dotenv

---

## Módulos del Sistema

### 1. CRUD de Evidencias
Desarrollo de la lógica de negocio para la administración de las evidencias, permitiendo almacenar la información de texto y enlazar de forma automática las URLs de los archivos físicos procesados por el backend.

### 2. Autenticación Tradicional (JWT)
Configuración de los endpoints de Django REST Framework para el manejo de credenciales locales (usuario y contraseña) a través de la ruta `/api/token/`. El sistema genera tokens de acceso y refresco para proteger las operaciones de escritura en la API.

### 3. Integración con Google OAuth 2.0
Registro de los endpoints bajo la ruta `/api/auth/google/` para habilitar el inicio de sesión mediante el uso de cuentas de correo institucionales, validando la identidad de los usuarios de prueba registrados en la consola de Google Cloud.

### 4. Seguridad de Credenciales y Variables de Entorno
Implementación de archivos `.env` locales para aislar y proteger las credenciales sensibles del sistema, tales como las API Keys de Cloudinary y los Client IDs de Google, evitando su exposición en el repositorio público.

### 5. Pipeline de Integración Continua (CI/CD)
Estructuración de flujos automatizados con GitHub Actions en la carpeta `.github/workflows/` para ejecutar pruebas, revisar sintaxis y validar la compilación del entorno en cada push realizado a las ramas de desarrollo.

---

## Instrucciones de Instalación Local

Para levantar el entorno de desarrollo localmente, ejecute los siguientes comandos en la terminal:

1. Clonar el repositorio e ingresar al directorio del proyecto.
2. Instalar las dependencias del sistema:
   ```bash
   pip install -r requirements.txt
