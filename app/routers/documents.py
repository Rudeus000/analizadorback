from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from app.services.cv_processor import procesar_cv
from app.integrations.supabase import supabase_client

router = APIRouter()

class ProcessDocumentRequest(BaseModel):
    documento_id: int
    file_path: str

@router.post("/process-document")
async def process_document(request: ProcessDocumentRequest):
    try:
        # Obtener el archivo de Supabase Storage
        file_path = request.file_path
        response = supabase_client.storage.from_('cvs').download(file_path)
        
        if not response:
            raise HTTPException(status_code=404, detail="Archivo no encontrado en storage")

        # Procesar el CV
        resultado = await procesar_cv(response, request.documento_id)
        
        return {
            "status": "success",
            "message": "Documento procesado exitosamente",
            "data": resultado
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 