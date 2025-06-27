# app/services/cv_processor.py
import mimetypes
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile
import os

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
from app.integrations.supabase import supabase_client


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


async def procesar_cv(file_content: bytes, documento_id: int) -> Dict[str, Any]:
    """
    Procesa un archivo CV y extrae información relevante.
    
    Args:
        file_content: Contenido del archivo en bytes
        documento_id: ID del documento en la base de datos
        
    Returns:
        Dict con la información extraída del CV
    """
    try:
        print(f"Iniciando procesamiento de CV para documento_id: {documento_id}")
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name
            print(f"Archivo temporal creado en: {temp_path}")

        try:
            # TODO: Implementar la lógica de extracción de texto y análisis
            # Por ahora retornamos un resultado de ejemplo
            resultado = {
                "documento_id": documento_id,
                "estado": "procesado",
                "informacion_extraida": {
                    "nombre": "Ejemplo",
                    "experiencia": [],
                    "educacion": [],
                    "habilidades": []
                }
            }

            print("Procesamiento completado exitosamente")
            return resultado

        finally:
            # Limpiar archivo temporal
            print(f"Eliminando archivo temporal: {temp_path}")
            os.unlink(temp_path)

    except Exception as e:
        print(f"Error en procesar_cv: {str(e)}")
        raise e