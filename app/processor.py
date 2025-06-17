from app.utils.extractors import (
    detectar_email,
    detectar_telefono,
    detectar_nombre,
    detectar_experiencia,
    detectar_educacion,
)
from langdetect import detect

def procesar_texto(texto: str) -> tuple[dict, list]:
    idioma = detect(texto)
    data = {
        "idioma": idioma,
        "longitud": len(texto),
        "nombre": detectar_nombre(texto),
        "email": detectar_email(texto),
        "telefono": detectar_telefono(texto),
        "experiencia": detectar_experiencia(texto),
        "educacion": detectar_educacion(texto),
    }

    habilidades = extraer_habilidades(texto)  # si no tienes esto aún, deja como []
    return data, habilidades

def extraer_habilidades(texto: str) -> list:
    # Versión simple (puedes mejorarla después)
    habilidades_comunes = ["Python", "Excel", "Inglés", "SQL", "Trabajo en equipo", "Comunicación"]
    return [h for h in habilidades_comunes if h.lower() in texto.lower()]
