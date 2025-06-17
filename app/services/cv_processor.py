# app/services/cv_processor.py
import mimetypes
import hashlib
import logging
from pathlib import Path
from typing import Optional

import docx
import pdfplumber
import openpyxl
from langdetect import detect

from app.utils.extractors import (
    detectar_email,
    detectar_telefono,
    detectar_nombre,
    detectar_experiencia,
    detectar_educacion,
)


# Configurar logs
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

SUPPORTED_MIME_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
}


def obtener_mime_type(file_path: Path) -> Optional[str]:
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type


def es_duplicado(texto: str, textos_hash: set) -> bool:
    contenido_hash = hashlib.md5(texto.encode()).hexdigest()
    return contenido_hash in textos_hash


def detectar_idioma(texto: str) -> str:
    try:
        return detect(texto)
    except Exception as e:
        logger.warning(f"Fallo en detección de idioma: {e}")
        return "unknown"


def extraer_texto(file_path: Path) -> str:
    mime_type = obtener_mime_type(file_path)

    if mime_type == "application/pdf":
        with pdfplumber.open(file_path) as pdf:
            texto = " ".join([page.extract_text() or "" for page in pdf.pages])
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file_path)
        texto = " ".join([p.text for p in doc.paragraphs])
    elif mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        wb = openpyxl.load_workbook(file_path)
        texto = " ".join(str(cell.value) for sheet in wb.worksheets for row in sheet.iter_rows() for cell in row if cell.value)
    else:
        raise ValueError("Tipo de archivo no soportado")

    if not texto.strip():
        raise ValueError("Documento sin texto legible")

    return texto


def procesar_cv(file_path: Path, textos_hash: set) -> dict:
    mime_type = obtener_mime_type(file_path)
    logger.info(f"Procesando archivo: {file_path.name}, MIME: {mime_type}")

    if mime_type not in SUPPORTED_MIME_TYPES:
        raise ValueError("Formato no soportado")

    texto = extraer_texto(file_path)

    if es_duplicado(texto, textos_hash):
        raise ValueError("Documento duplicado")

    idioma = detectar_idioma(texto)
    if idioma not in ["es", "en"]:
        raise ValueError(f"Idioma no soportado: {idioma}")

    # Aquí puedes agregar detección de nombre, correo, teléfono, etc.
    datos_extraidos = {
        "idioma": idioma,
        "longitud": len(texto),
        "nombre": detectar_nombre(texto),
        "email": detectar_email(texto),
        "telefono": detectar_telefono(texto),
        "experiencia": detectar_experiencia(texto),
        "educacion": detectar_educacion(texto),
    }

    if datos_extraidos.get("longitud", 0) < 30:
        raise ValueError("Documento demasiado corto o sin contenido útil")

    return datos_extraidos