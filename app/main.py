from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from app.supabase_client import get_documentos_no_procesados, guardar_procesado, guardar_documento
from app.processor import procesar_texto
from app.utils.file_processor import procesar_archivo
from supabase import create_client, Client
import os
from pathlib import Path
import tempfile
from app.services.cv_processor import extraer_texto, procesar_cv
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O especifica ["http://localhost:8080"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Verificar variables de entorno
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Las variables de entorno SUPABASE_URL y SUPABASE_KEY deben estar configuradas")
    print("Por favor, configura estas variables antes de iniciar el servidor:")
    print("export SUPABASE_URL=tu_url_de_supabase")
    print("export SUPABASE_KEY=tu_key_de_supabase")
    raise ValueError("Variables de entorno no configuradas")

# Inicializar cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class ProcessDocumentRequest(BaseModel):
    documento_id: int
    file_path: str

class SurveyCreateRequest(BaseModel):
    titulo: str
    descripcion: str
    tipo_encuesta: str
    preguntas: List[Dict[str, Any]]
    activa: bool = True

class SurveyResponseRequest(BaseModel):
    encuesta_id: int
    respuestas: Dict[str, str]

class ReportRequest(BaseModel):
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    tipo_reporte: str = "general"

# MODELO Y SIMULACIÓN DE VACANTES
class Vacante(BaseModel):
    vacante_id: int
    titulo: str
    descripcion: str
    activa: bool

vacantes_db = [
    Vacante(vacante_id=1, titulo="Desarrollador Python", descripcion="Trabajo remoto", activa=True),
    Vacante(vacante_id=2, titulo="Data Analyst", descripcion="Presencial en Lima", activa=True),
]

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
async def process_document(request: ProcessDocumentRequest):
    try:
        print(f"Recibiendo solicitud para documento_id: {request.documento_id}, file_path: {request.file_path}")
        
        # Obtener el archivo de Supabase Storage
        file_path = request.file_path
        print(f"Intentando descargar archivo de: {file_path}")
        
        try:
            response = supabase.storage.from_('cvs').download(file_path)
            print(f"Respuesta de Supabase: {type(response)}")
        except Exception as storage_error:
            print(f"Error al descargar de Supabase: {str(storage_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al descargar archivo de Supabase: {str(storage_error)}"
            )
        
        if not response:
            print("No se pudo descargar el archivo de Supabase")
            raise HTTPException(status_code=404, detail="Archivo no encontrado en storage")

        print("Archivo descargado exitosamente")

        # Crear archivo temporal
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(response)
                temp_path = temp_file.name
                print(f"Archivo temporal creado en: {temp_path}")
        except Exception as file_error:
            print(f"Error al crear archivo temporal: {str(file_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al crear archivo temporal: {str(file_error)}"
            )

        try:
            # Procesar el CV
            print("Iniciando procesamiento del CV")
            resultado = await procesar_cv(response, request.documento_id)
            print("CV procesado exitosamente")
            
            # Actualizar estado en la base de datos
            print("Actualizando estado en la base de datos")
            try:
                # Solo actualizamos el estado por ahora
                supabase.table('documentos_cargados').update({
                    'estado': 'procesado'
                }).eq('documento_id', request.documento_id).execute()
                print("Estado actualizado exitosamente")
            except Exception as db_error:
                print(f"Error al actualizar estado en la base de datos: {str(db_error)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al actualizar estado en la base de datos: {str(db_error)}"
                )

            return {
                "status": "success",
                "message": "Documento procesado exitosamente",
                "data": resultado
            }
        finally:
            # Limpiar archivo temporal
            try:
                print(f"Eliminando archivo temporal: {temp_path}")
                os.unlink(temp_path)
            except Exception as cleanup_error:
                print(f"Error al eliminar archivo temporal: {str(cleanup_error)}")

    except HTTPException as he:
        print(f"HTTPException en process_document: {str(he)}")
        raise he
    except Exception as e:
        print(f"Error inesperado en process_document: {str(e)}")
        # Actualizar estado de error en la base de datos
        try:
            supabase.table('documentos_cargados').update({
                'estado': 'error'
            }).eq('documento_id', request.documento_id).execute()
        except Exception as db_error:
            print(f"Error al actualizar estado de error en la base de datos: {str(db_error)}")
        
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documentos-pendientes")
async def get_pending_documents():
    try:
        response = supabase.table('documentos_cargados').select('*').eq('estado', 'pendiente').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== ENDPOINTS PARA ENCUESTAS =====

@app.get("/encuestas")
async def get_surveys():
    """Obtener todas las encuestas activas"""
    try:
        response = supabase.table('encuestas').select('*').eq('activa', True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/encuestas")
async def create_survey(survey: SurveyCreateRequest):
    """Crear una nueva encuesta (solo administradores)"""
    try:
        response = supabase.table('encuestas').insert({
            'titulo': survey.titulo,
            'descripcion': survey.descripcion,
            'tipo_encuesta': survey.tipo_encuesta,
            'preguntas': survey.preguntas,
            'activa': survey.activa
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/encuestas/{encuesta_id}/responder")
async def submit_survey_response(encuesta_id: int, response_data: SurveyResponseRequest):
    """Enviar respuesta a una encuesta"""
    try:
        # Verificar que el usuario esté autenticado
        user_response = supabase.auth.get_user()
        if not user_response.user:
            raise HTTPException(status_code=401, detail="Usuario no autenticado")
        
        # Verificar que no haya respondido antes
        existing_response = supabase.table('respuestas_encuesta').select('*').eq(
            'encuesta_id', encuesta_id
        ).eq('usuario_respuesta_id', user_response.user.id).execute()
        
        if existing_response.data:
            raise HTTPException(status_code=400, detail="Ya has respondido esta encuesta")
        
        # Guardar la respuesta
        response = supabase.table('respuestas_encuesta').insert({
            'encuesta_id': encuesta_id,
            'usuario_respuesta_id': user_response.user.id,
            'respuestas': response_data.respuestas
        }).execute()
        
        return {"message": "Respuesta enviada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/encuestas/{encuesta_id}/respuestas")
async def get_survey_responses(encuesta_id: int):
    """Obtener respuestas de una encuesta (solo empleadores/administradores)"""
    try:
        response = supabase.table('respuestas_encuesta').select('*').eq('encuesta_id', encuesta_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== ENDPOINTS PARA REPORTES =====

@app.get("/reportes/dashboard")
async def get_dashboard_reports():
    """Obtener métricas del dashboard"""
    try:
        # Contar documentos procesados
        docs_response = supabase.table('documentos_cargados').select('documento_id').execute()
        total_docs = len(docs_response.data) if docs_response.data else 0
        
        # Contar candidatos activos
        users_response = supabase.table('usuarios').select('usuario_id').eq('rol', 'candidato').execute()
        active_candidates = len(users_response.data) if users_response.data else 0
        
        # Contar análisis completados
        processed_response = supabase.table('datos_documentos_procesados').select('procesado_id').execute()
        completed_analyses = len(processed_response.data) if processed_response.data else 0
        
        # Obtener habilidades más comunes
        skills_response = supabase.table('datos_documentos_procesados').select('habilidades_indexadas').execute()
        all_skills = []
        if skills_response.data:
            for item in skills_response.data:
                if item.get('habilidades_indexadas'):
                    all_skills.extend(item['habilidades_indexadas'])
        
        # Contar habilidades
        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_documents": total_docs,
            "active_candidates": active_candidates,
            "completed_analyses": completed_analyses,
            "top_skills": [{"skill": skill, "count": count} for skill, count in top_skills]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reportes/candidatos")
async def get_candidates_report():
    """Obtener reporte de candidatos"""
    try:
        # Obtener datos de candidatos con sus predicciones
        response = supabase.table('datos_postulantes').select('''
            postulante_id,
            nombre_completo,
            habilidades,
            experiencia,
            predicciones_compatibilidad(probabilidad_exito, factores_clave)
        ''').execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reportes/habilidades")
async def get_skills_report():
    """Obtener reporte de habilidades"""
    try:
        # Obtener todas las habilidades de los documentos procesados
        response = supabase.table('datos_documentos_procesados').select('habilidades_indexadas').execute()
        
        all_skills = []
        if response.data:
            for item in response.data:
                if item.get('habilidades_indexadas'):
                    all_skills.extend(item['habilidades_indexadas'])
        
        # Contar habilidades
        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Formatear para gráficos
        skills_data = [{"name": skill, "value": count} for skill, count in skill_counts.items()]
        skills_data.sort(key=lambda x: x["value"], reverse=True)
        
        return skills_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reportes/experiencia")
async def get_experience_report():
    """Obtener reporte de distribución de experiencia"""
    try:
        # Obtener datos de experiencia
        response = supabase.table('datos_postulantes').select('experiencia').execute()
        
        experience_ranges = {
            '0-1 años': 0,
            '1-3 años': 0,
            '3-5 años': 0,
            '5-8 años': 0,
            '8+ años': 0
        }
        
        if response.data:
            for item in response.data:
                if item.get('experiencia'):
                    # Calcular años totales de experiencia
                    total_years = 0
                    for exp in item['experiencia']:
                        if isinstance(exp, dict) and 'duracion' in exp:
                            # Asumir que duracion está en meses
                            total_years += exp['duracion'] / 12
                    
                    # Categorizar
                    if total_years <= 1:
                        experience_ranges['0-1 años'] += 1
                    elif total_years <= 3:
                        experience_ranges['1-3 años'] += 1
                    elif total_years <= 5:
                        experience_ranges['3-5 años'] += 1
                    elif total_years <= 8:
                        experience_ranges['5-8 años'] += 1
                    else:
                        experience_ranges['8+ años'] += 1
        
        # Formatear para gráficos
        experience_data = [{"range": range_name, "count": count} for range_name, count in experience_ranges.items()]
        
        return experience_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== ENDPOINTS PARA GESTIÓN DE CANDIDATOS =====

@app.get("/candidatos")
async def get_candidates():
    """Obtener lista de candidatos (solo empleadores/administradores)"""
    try:
        response = supabase.table('datos_postulantes').select('''
            postulante_id,
            nombre_completo,
            email,
            habilidades,
            experiencia,
            predicciones_compatibilidad(probabilidad_exito, factores_clave)
        ''').execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/candidatos/{candidato_id}")
async def get_candidate_detail(candidato_id: int):
    """Obtener detalles de un candidato específico"""
    try:
        response = supabase.table('datos_postulantes').select('''
            *,
            predicciones_compatibilidad(*),
            documentos_cargados(*)
        ''').eq('postulante_id', candidato_id).single().execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== ENDPOINTS PARA PREDICCIONES =====

@app.get("/predicciones")
async def get_predictions():
    """Obtener todas las predicciones (solo empleadores/administradores)"""
    try:
        response = supabase.table('predicciones').select('''
            *,
            datos_documentos_procesados(
                documento_id,
                documentos_cargados(nombre_archivo, uploader_id)
            )
        ''').execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predicciones/calcular")
async def calculate_prediction(documento_id: int):
    """Calcular predicción para un documento específico y generar recomendaciones personalizadas"""
    try:
        # Obtener datos procesados del documento
        processed_response = supabase.table('datos_documentos_procesados').select('*').eq('documento_id', documento_id).single().execute()
        
        if not processed_response.data:
            raise HTTPException(status_code=404, detail="Documento no procesado")
        
        data = processed_response.data
        habilidades = data.get('habilidades_indexadas', [])
        experiencia = 0
        # Intentar extraer años de experiencia si está disponible
        if data.get('data_extraida') and isinstance(data['data_extraida'], dict):
            experiencia = data['data_extraida'].get('experiencia_anos', 0)
        
        # Habilidades clave que buscamos
        habilidades_clave = ["Python", "Inglés", "Liderazgo", "Trabajo en equipo", "SQL"]
        recomendaciones = []
        factores_clave = []
        score = 70  # base

        # Analizar habilidades
        for habilidad in habilidades_clave:
            if habilidad not in habilidades:
                recomendaciones.append(f"Mejorar o adquirir la habilidad: {habilidad}")
            else:
                factores_clave.append(f"Posee {habilidad}")

        # Analizar experiencia
        if experiencia < 2:
            recomendaciones.append("Ganar más experiencia laboral (mínimo 2 años recomendado)")
            score -= 10
        elif experiencia >= 5:
            factores_clave.append("Experiencia laboral sólida")
            score += 10

        # Ajustar score por cantidad de habilidades
        score += min(len([h for h in habilidades if h in habilidades_clave]) * 3, 15)
        score = max(50, min(score, 95))  # Limitar entre 50 y 95

        # Guardar predicción
        prediction_response = supabase.table('predicciones').insert({
            'procesado_data_id': data['procesado_id'],
            'probabilidad_exito': round(score, 2),
            'factores_clave': factores_clave,
            'version_modelo_ml_id': 1  # Asumiendo que existe el modelo base
        }).execute()

        return {
            "probabilidad_exito": round(score, 2),
            "factores_clave": factores_clave,
            "recomendaciones": recomendaciones
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vacantes")
async def get_vacantes():
    return [v.dict() for v in vacantes_db if v.activa]
