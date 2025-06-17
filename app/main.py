from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from app.supabase_client import get_documentos_no_procesados, guardar_procesado, guardar_documento
from app.processor import procesar_texto
from app.utils.file_processor import procesar_archivo
from supabase import create_client
import os
from pathlib import Path
import tempfile
from app.services.cv_processor import extraer_texto, procesar_cv

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O especifica ["http://localhost:8080"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/")
def root():
    return {"message": "API CV Processor activa"}

@app.get("/documentos-pendientes")
async def documentos_pendientes():
    return await get_documentos_no_procesados()

@app.post("/procesar/{documento_id}")
async def procesar(documento_id: int):
    documentos = await get_documentos_no_procesados()
    doc = next((d for d in documentos if d["documento_id"] == documento_id), None)

    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado o ya procesado")

    data, habilidades = procesar_texto(doc["contenido_raw_texto"])
    resultado = await guardar_procesado(documento_id, data, habilidades)
    return {"procesado": True, "resultado": resultado}

@app.post("/subir-documento")
async def subir_documento(archivo: UploadFile = File(...)):
    try:
        # Procesar el archivo y obtener el texto
        texto = await procesar_archivo(archivo)
        
        # Guardar el documento en la base de datos
        documento_id = await guardar_documento(archivo.filename, texto)
        
        return {
            "mensaje": "Documento subido exitosamente",
            "documento_id": documento_id,
            "nombre_archivo": archivo.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-document")
async def process_document(request: Request):
    data = await request.json()
    documento_id = data.get("documento_id")
    file_path = data.get("file_path")

    # 1. Obtener info del documento
    doc_resp = supabase.table("documentos_cargados").select("*").eq("documento_id", documento_id).maybe_single().execute()
    if not doc_resp or not getattr(doc_resp, 'data', None):
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    documento = doc_resp.data

    # 2. Descargar el archivo desde Supabase Storage
    bucket = "cvs"
    file_key = file_path  # Usa el file_path completo, por ejemplo 'cvs/1750138633995.docx'
    file_resp = supabase.storage.from_(bucket).download(file_key)
    if not file_resp:
        raise HTTPException(status_code=500, detail="No se pudo descargar el archivo")

    # 3. Guardar archivo temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix="." + documento["nombre_archivo"].split(".")[-1]) as tmp:
        tmp.write(file_resp)
        tmp_path = Path(tmp.name)

    try:
        # 4. Extraer texto
        texto = extraer_texto(tmp_path)
        # 5. Actualizar contenido_raw_texto en documentos_cargados
        supabase.table("documentos_cargados").update({"contenido_raw_texto": texto}).eq("documento_id", documento_id).execute()
        # 6. Procesar y guardar en datos_documentos_procesados
        datos_extraidos = procesar_cv(tmp_path, set())
        supabase.table("datos_documentos_procesados").insert({
            "documento_id": documento_id,
            "tipo_entidad_procesada": "cv_candidato",
            "data_extraida": datos_extraidos,
            "habilidades_indexadas": datos_extraidos.get("habilidades", [])
        }).execute()
    finally:
        os.remove(tmp_path)

    return {"procesado": True, "documento_id": documento_id}
