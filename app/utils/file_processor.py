import pdfplumber
import docx
from fastapi import UploadFile, HTTPException
import io

async def procesar_archivo(archivo: UploadFile) -> str:
    """
    Procesa diferentes tipos de archivos y extrae su contenido como texto.
    Soporta PDF y DOCX por ahora.
    """
    contenido = await archivo.read()
    
    # Determinar el tipo de archivo por su extensión
    extension = archivo.filename.split('.')[-1].lower()
    
    try:
        if extension == 'pdf':
            return procesar_pdf(contenido)
        elif extension == 'docx':
            return procesar_docx(contenido)
        elif extension == 'txt':
            return procesar_txt(contenido)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de archivo no soportado: {extension}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el archivo: {str(e)}"
        )

def procesar_pdf(contenido: bytes) -> str:
    """Procesa un archivo PDF y extrae su texto."""
    with pdfplumber.open(io.BytesIO(contenido)) as pdf:
        texto = ""
        for pagina in pdf.pages:
            texto += pagina.extract_text() or ""
        return texto

def procesar_docx(contenido: bytes) -> str:
    """Procesa un archivo DOCX y extrae su texto."""
    doc = docx.Document(io.BytesIO(contenido))
    texto = ""
    for parrafo in doc.paragraphs:
        texto += parrafo.text + "\n"
    return texto

def procesar_txt(contenido: bytes) -> str:
    """Procesa un archivo de texto plano."""
    return contenido.decode('utf-8') 