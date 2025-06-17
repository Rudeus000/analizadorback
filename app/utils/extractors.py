import re

def detectar_email(texto: str) -> str:
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", texto)
    return match.group(0) if match else "No encontrado"

def detectar_telefono(texto: str) -> str:
    match = re.search(r"\+?\d{1,3}[\s\-]?\(?\d+\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}", texto)
    return match.group(0) if match else "No encontrado"

def detectar_nombre(texto: str) -> str:
    posibles = re.findall(r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+", texto)
    return posibles[0] if posibles else "No detectado"

def detectar_experiencia(texto: str) -> str:
    if "experiencia" in texto.lower():
        return "Encontrada sección de experiencia"
    return "No detectado"

def detectar_educacion(texto: str) -> str:
    claves = ["universidad", "instituto", "bachiller", "maestría", "licenciatura"]
    if any(palabra in texto.lower() for palabra in claves):
        return "Encontrada sección educativa"
    return "No detectado"
