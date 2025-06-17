from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

async def get_documentos_no_procesados():
    response = supabase.table("documentos").select("*").eq("procesado", False).execute()
    return response.data

async def guardar_procesado(documento_id: int, data: dict, habilidades: list):
    # Actualizar el documento como procesado
    supabase.table("documentos").update({
        "procesado": True,
        "data_procesada": data
    }).eq("id", documento_id).execute()
    
    # Guardar las habilidades
    for habilidad in habilidades:
        supabase.table("habilidades").insert({
            "documento_id": documento_id,
            "nombre": habilidad
        }).execute()
    
    return {"documento_id": documento_id, "data": data, "habilidades": habilidades}

async def guardar_documento(nombre_archivo: str, contenido: str) -> int:
    """
    Guarda un nuevo documento en la base de datos.
    Retorna el ID del documento creado.
    """
    response = supabase.table("documentos").insert({
        "nombre_archivo": nombre_archivo,
        "contenido_raw_texto": contenido,
        "procesado": False
    }).execute()
    
    if not response.data:
        raise Exception("Error al guardar el documento")
    
    return response.data[0]["id"]
