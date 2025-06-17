# CV Backend

Este es el backend para la plataforma de análisis y procesamiento de currículums (CVs), desarrollado con FastAPI.

## Requisitos

- Python 3.11 o superior
- pip

## Instalación

1. **Clona el repositorio:**

```bash
git clone <URL_DEL_REPOSITORIO>
cd cv_backend
```

2. **Crea y activa un entorno virtual (opcional pero recomendado):**

```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate
```

3. **Instala las dependencias:**

```bash
pip install -r requirements.txt
```

4. **Configura las variables de entorno:**

Crea un archivo `.env` en la raíz del proyecto con tus variables necesarias, por ejemplo:

```
SUPABASE_URL=tu_url_supabase
SUPABASE_KEY=tu_key_supabase
```

## Ejecución

Para correr el servidor en modo desarrollo:

```bash
uvicorn app.main:app --reload
```

El backend estará disponible en [http://localhost:8000](http://localhost:8000)

## Pruebas

Puedes ejecutar los tests con:

```bash
pytest
```

## Estructura del proyecto

- `app/` - Código fuente principal
- `requirements.txt` - Dependencias del proyecto
- `test_docs/` - Documentos de prueba

## Notas

- Asegúrate de tener configuradas las credenciales de Supabase correctamente.
- Si tienes dudas, revisa los comentarios en el código o contacta al equipo de desarrollo.
