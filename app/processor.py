from app.utils.extractors import (
    detectar_email,
    detectar_telefono,
    detectar_nombre,
    detectar_ubicacion,
    detectar_linkedin,
    detectar_github,
    extraer_experiencia_laboral,
    extraer_educacion,
    extraer_certificaciones,
    extraer_proyectos,
    extraer_idiomas,
    extraer_habilidades_avanzadas,
    detectar_experiencia,
    detectar_educacion,
    extraer_habilidades,
)
from langdetect import detect

def procesar_texto(texto: str) -> tuple[dict, list]:
    idioma = detect(texto)
    
    # Información básica
    data = {
        "idioma": idioma,
        "longitud": len(texto),
        "nombre": detectar_nombre(texto),
        "email": detectar_email(texto),
        "telefono": detectar_telefono(texto),
        "ubicacion": detectar_ubicacion(texto),
        "linkedin": detectar_linkedin(texto),
        "github": detectar_github(texto),
    }
    
    # Información detallada
    data["experiencia_laboral"] = extraer_experiencia_laboral(texto)
    data["educacion"] = extraer_educacion(texto)
    data["certificaciones"] = extraer_certificaciones(texto)
    data["proyectos"] = extraer_proyectos(texto)
    data["idiomas"] = extraer_idiomas(texto)
    data["habilidades_detalladas"] = extraer_habilidades_avanzadas(texto)
    
    # Información básica de secciones
    data["tiene_experiencia"] = detectar_experiencia(texto)
    data["tiene_educacion"] = detectar_educacion(texto)
    
    # Habilidades simples (para compatibilidad)
    habilidades = extraer_habilidades(texto)
    
    return data, habilidades

def extraer_habilidades(texto: str) -> list:
    # Versión simple (puedes mejorarla después)
    habilidades_comunes = ["Python", "Excel", "Inglés", "SQL", "Trabajo en equipo", "Comunicación"]
    return [h for h in habilidades_comunes if h.lower() in texto.lower()]
