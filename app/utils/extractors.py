import re
from typing import List, Dict, Any

def detectar_email(texto: str) -> str:
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", texto)
    return match.group(0) if match else "No encontrado"

def detectar_telefono(texto: str) -> str:
    match = re.search(r"\+?\d{1,3}[\s\-]?\(?\d+\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}", texto)
    return match.group(0) if match else "No encontrado"

def detectar_nombre(texto: str) -> str:
    posibles = re.findall(r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+", texto)
    return posibles[0] if posibles else "No detectado"

def detectar_ubicacion(texto: str) -> str:
    # Patrones comunes de ubicación
    patrones = [
        r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+,\s*[A-ZÁÉÍÓÚÑ]{2,}\b",  # Ciudad, País
        r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+,\s*[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\b",  # Ciudad, Estado
    ]
    for patron in patrones:
        match = re.search(patron, texto)
        if match:
            return match.group(0)
    return "No detectado"

def detectar_linkedin(texto: str) -> str:
    match = re.search(r"linkedin\.com/in/[a-zA-Z0-9\-_]+", texto, re.IGNORECASE)
    return match.group(0) if match else "No encontrado"

def detectar_github(texto: str) -> str:
    match = re.search(r"github\.com/[a-zA-Z0-9\-_]+", texto, re.IGNORECASE)
    return match.group(0) if match else "No encontrado"

def extraer_experiencia_laboral(texto: str) -> List[Dict[str, Any]]:
    """Extrae experiencia laboral detallada"""
    experiencias = []
    
    # Patrones para detectar secciones de experiencia
    secciones_experiencia = re.split(r"(?:experiencia|trabajo|laboral|empleo)", texto, flags=re.IGNORECASE)
    
    for seccion in secciones_experiencia[1:]:  # Saltamos la primera sección
        # Buscar fechas
        fechas = re.findall(r"\b(?:ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{4}\b", seccion, re.IGNORECASE)
        
        # Buscar empresas (palabras en mayúsculas que podrían ser nombres de empresas)
        empresas = re.findall(r"\b[A-Z][A-Za-z0-9\s&]+(?:Inc|Corp|LLC|Ltd|S\.A|S\.L)\b", seccion)
        
        # Buscar puestos
        puestos = re.findall(r"\b(?:Desarrollador|Ingeniero|Analista|Arquitecto|Líder|Manager|Director|CEO|CTO|DevOps|Full Stack|Frontend|Backend|Mobile|Data|QA|UX|UI)\s+[A-Za-z\s]+\b", seccion)
        
        if fechas or empresas or puestos:
            experiencia = {
                "empresa": empresas[0] if empresas else "No especificada",
                "puesto": puestos[0] if puestos else "No especificado",
                "fechas": fechas[:2] if len(fechas) >= 2 else fechas,
                "descripcion": seccion[:200] + "..." if len(seccion) > 200 else seccion
            }
            experiencias.append(experiencia)
    
    return experiencias

def extraer_educacion(texto: str) -> List[Dict[str, Any]]:
    """Extrae información educativa detallada"""
    educacion = []
    
    # Patrones para títulos académicos
    titulos = re.findall(r"\b(?:Ingeniería|Ingeniero|Licenciatura|Licenciado|Maestría|Maestro|Doctorado|Doctor|Técnico|Tecnólogo|Bachiller|Diplomado)\s+[A-Za-z\s]+\b", texto)
    
    # Patrones para instituciones educativas
    instituciones = re.findall(r"\b(?:Universidad|Instituto|Escuela|College|University|Institute)\s+[A-Za-z\s]+\b", texto)
    
    # Patrones para fechas de graduación
    fechas_grad = re.findall(r"\b(?:graduado|egresado|finalizado)\s+(?:en\s+)?(\d{4})\b", texto, re.IGNORECASE)
    
    for i, titulo in enumerate(titulos):
        edu_item = {
            "titulo": titulo,
            "institucion": instituciones[i] if i < len(instituciones) else "No especificada",
            "fecha_graduacion": fechas_grad[i] if i < len(fechas_grad) else "No especificada"
        }
        educacion.append(edu_item)
    
    return educacion

def extraer_certificaciones(texto: str) -> List[Dict[str, Any]]:
    """Extrae certificaciones técnicas y profesionales"""
    certificaciones = []
    
    # Patrones para certificaciones comunes
    patrones_cert = [
        r"\b(?:AWS|Amazon Web Services)\s+(?:Certified|Certification)\s+[A-Za-z\s]+\b",
        r"\b(?:Microsoft|MS)\s+(?:Certified|Certification)\s+[A-Za-z\s]+\b",
        r"\b(?:Google|GCP)\s+(?:Certified|Certification)\s+[A-Za-z\s]+\b",
        r"\b(?:Azure)\s+(?:Certified|Certification)\s+[A-Za-z\s]+\b",
        r"\b(?:Oracle)\s+(?:Certified|Certification)\s+[A-Za-z\s]+\b",
        r"\b(?:Cisco)\s+(?:Certified|Certification)\s+[A-Za-z\s]+\b",
        r"\b(?:PMP|Project Management Professional)\b",
        r"\b(?:Scrum|Agile)\s+(?:Master|Certified)\s+[A-Za-z\s]+\b",
        r"\b(?:TOEFL|IELTS|Cambridge)\s+(?:Score|Level)\s+[A-Za-z0-9\s]+\b",
        r"\b(?:React|Angular|Vue|Node|Python|Java|JavaScript)\s+(?:Certified|Certification)\b"
    ]
    
    for patron in patrones_cert:
        matches = re.findall(patron, texto, re.IGNORECASE)
        for match in matches:
            # Buscar fecha de certificación
            fecha_match = re.search(r"\b(\d{4})\b", texto[texto.find(match):texto.find(match)+200])
            certificaciones.append({
                "nombre": match.strip(),
                "fecha": fecha_match.group(1) if fecha_match else "No especificada",
                "tipo": "Técnica" if any(tech in match.lower() for tech in ["aws", "azure", "react", "python", "java"]) else "Profesional"
            })
    
    return certificaciones

def extraer_proyectos(texto: str) -> List[Dict[str, Any]]:
    """Extrae proyectos personales y profesionales"""
    proyectos = []
    
    # Buscar secciones de proyectos
    secciones_proyectos = re.split(r"(?:proyectos|portfolio|trabajos|desarrollos)", texto, flags=re.IGNORECASE)
    
    for seccion in secciones_proyectos[1:]:
        # Buscar nombres de proyectos (títulos en mayúsculas)
        nombres_proyectos = re.findall(r"\b[A-Z][A-Za-z0-9\s\-]+(?:App|System|Platform|Tool|Dashboard|API)\b", seccion)
        
        # Buscar URLs de repositorios
        urls = re.findall(r"(?:github\.com|gitlab\.com|bitbucket\.org)/[a-zA-Z0-9\-_/]+", seccion)
        
        # Buscar tecnologías mencionadas
        tecnologias = re.findall(r"\b(?:React|Angular|Vue|Node|Python|Java|JavaScript|TypeScript|MongoDB|PostgreSQL|MySQL|Docker|Kubernetes|AWS|Azure|Firebase)\b", seccion)
        
        for i, nombre in enumerate(nombres_proyectos):
            proyecto = {
                "nombre": nombre,
                "url": urls[i] if i < len(urls) else "No especificada",
                "tecnologias": list(set(tecnologias)),
                "descripcion": seccion[:150] + "..." if len(seccion) > 150 else seccion
            }
            proyectos.append(proyecto)
    
    return proyectos

def extraer_idiomas(texto: str) -> List[Dict[str, Any]]:
    """Extrae información sobre idiomas"""
    idiomas = []
    
    # Patrones para idiomas
    patrones_idiomas = [
        r"\b(?:Español|Spanish)\s+(?:Nativo|Native|Avanzado|Advanced|Intermedio|Intermediate|Básico|Basic)\b",
        r"\b(?:Inglés|English)\s+(?:Nativo|Native|Avanzado|Advanced|Intermedio|Intermediate|Básico|Basic)\b",
        r"\b(?:Francés|French)\s+(?:Nativo|Native|Avanzado|Advanced|Intermedio|Intermediate|Básico|Basic)\b",
        r"\b(?:Alemán|German)\s+(?:Nativo|Native|Avanzado|Advanced|Intermedio|Intermediate|Básico|Basic)\b",
        r"\b(?:Portugués|Portuguese)\s+(?:Nativo|Native|Avanzado|Advanced|Intermedio|Intermediate|Básico|Basic)\b"
    ]
    
    for patron in patrones_idiomas:
        matches = re.findall(patron, texto, re.IGNORECASE)
        for match in matches:
            idioma, nivel = match.split()[:2]
            idiomas.append({
                "idioma": idioma,
                "nivel": nivel,
                "certificacion": "TOEFL" if "inglés" in idioma.lower() else "No especificada"
            })
    
    return idiomas

def extraer_habilidades_avanzadas(texto: str) -> Dict[str, List[str]]:
    """Extrae habilidades técnicas y profesionales organizadas por categorías"""
    habilidades = {
        "lenguajes_programacion": [],
        "frameworks": [],
        "bases_datos": [],
        "herramientas": [],
        "metodologias": [],
        "cloud": [],
        "soft_skills": [],
        "educacion": [],
        "administracion": [],
        "salud": [],
        "idiomas": [],
        "arte_comunicacion": [],
        "ciencias": [],
        "ingenieria": [],
    }

    # Lenguajes de programación
    lenguajes = re.findall(r"\b(?:Python|Java|JavaScript|TypeScript|C\+\+|C#|PHP|Ruby|Go|Rust|Swift|Kotlin|Scala|R|MATLAB|Perl|Shell|Bash)\b", texto, re.IGNORECASE)
    habilidades["lenguajes_programacion"] = list(set(lenguajes))

    # Frameworks y librerías
    frameworks = re.findall(r"\b(?:React|Angular|Vue|Node\.js|Express|Django|Flask|Spring|Laravel|Symfony|ASP\.NET|Ruby on Rails|FastAPI|Next\.js|Nuxt\.js|Svelte|Ember)\b", texto, re.IGNORECASE)
    habilidades["frameworks"] = list(set(frameworks))

    # Bases de datos
    bases_datos = re.findall(r"\b(?:MySQL|PostgreSQL|MongoDB|Redis|SQLite|Oracle|SQL Server|MariaDB|Cassandra|DynamoDB|Firebase|Supabase)\b", texto, re.IGNORECASE)
    habilidades["bases_datos"] = list(set(bases_datos))

    # Herramientas y tecnologías
    herramientas = re.findall(r"\b(?:Git|Docker|Kubernetes|Jenkins|GitLab|GitHub|Bitbucket|Jira|Confluence|Slack|Trello|Asana|Figma|Adobe|Photoshop|Illustrator|Power BI|AutoCAD|SolidWorks)\b", texto, re.IGNORECASE)
    habilidades["herramientas"] = list(set(herramientas))

    # Metodologías
    metodologias = re.findall(r"\b(?:Agile|Scrum|Kanban|Waterfall|DevOps|CI/CD|TDD|BDD|Lean|Six Sigma|PMI|Design Thinking)\b", texto, re.IGNORECASE)
    habilidades["metodologias"] = list(set(metodologias))

    # Cloud
    cloud = re.findall(r"\b(?:AWS|Azure|Google Cloud|GCP|Firebase|Heroku|DigitalOcean|Vercel|Netlify|Cloudflare)\b", texto, re.IGNORECASE)
    habilidades["cloud"] = list(set(cloud))

    # Soft skills
    soft_skills = re.findall(r"\b(?:Liderazgo|Comunicación|Trabajo en equipo|Resolución de problemas|Creatividad|Adaptabilidad|Gestión del tiempo|Pensamiento crítico|Empatía|Negociación|Proactividad|Organización|Atención al detalle)\b", texto, re.IGNORECASE)
    habilidades["soft_skills"] = list(set(soft_skills))

    # Educación
    educacion = re.findall(r"\b(?:docencia|pedagogía|tutoría|planificación curricular|enseñanza|evaluación educativa|educación|formación|capacitación)\b", texto, re.IGNORECASE)
    habilidades["educacion"] = list(set(educacion))

    # Administración y negocios
    administracion = re.findall(r"\b(?:gestión|liderazgo|finanzas|contabilidad|recursos humanos|planificación estratégica|marketing|ventas|negociación|emprendimiento|administración|dirección|proyectos)\b", texto, re.IGNORECASE)
    habilidades["administracion"] = list(set(administracion))

    # Salud
    salud = re.findall(r"\b(?:enfermería|medicina|atención al paciente|primeros auxilios|farmacología|psicología|nutrición|odontología|salud|clínica|hospital|terapia|diagnóstico)\b", texto, re.IGNORECASE)
    habilidades["salud"] = list(set(salud))

    # Idiomas
    idiomas = re.findall(r"\b(?:inglés|francés|alemán|portugués|traducción|interpretación|español|italiano|chino|japonés|idiomas|bilingüe|multilingüe)\b", texto, re.IGNORECASE)
    habilidades["idiomas"] = list(set(idiomas))

    # Arte y comunicación
    arte_comunicacion = re.findall(r"\b(?:dibujo|pintura|fotografía|redacción|comunicación oral|edición de video|diseño gráfico|música|teatro|cine|escultura|periodismo|publicidad|locución|presentación)\b", texto, re.IGNORECASE)
    habilidades["arte_comunicacion"] = list(set(arte_comunicacion))

    # Ciencias
    ciencias = re.findall(r"\b(?:investigación|análisis de datos|laboratorio|biología|química|física|matemáticas|estadística|ciencias|experimentos|publicaciones)\b", texto, re.IGNORECASE)
    habilidades["ciencias"] = list(set(ciencias))

    # Ingeniería y manufactura
    ingenieria = re.findall(r"\b(?:autocad|solidworks|diseño industrial|mecánica|electricidad|electrónica|ingeniería|manufactura|procesos|calidad|producción)\b", texto, re.IGNORECASE)
    habilidades["ingenieria"] = list(set(ingenieria))

    return habilidades

def detectar_experiencia(texto: str) -> str:
    if "experiencia" in texto.lower():
        return "Encontrada sección de experiencia"
    return "No detectado"

def detectar_educacion(texto: str) -> str:
    claves = ["universidad", "instituto", "bachiller", "maestría", "licenciatura"]
    if any(palabra in texto.lower() for palabra in claves):
        return "Encontrada sección educativa"
    return "No detectado"

def extraer_habilidades(texto: str) -> list:
    # Lista ampliada de habilidades de múltiples áreas profesionales
    habilidades_comunes = [
        # Informática y tecnología
        "Python", "Java", "SQL", "HTML", "CSS", "JavaScript", "Excel", "Power BI", "Git", "Docker",
        # Educación
        "docencia", "pedagogía", "tutoría", "planificación curricular", "enseñanza", "evaluación educativa",
        # Administración y negocios
        "gestión", "liderazgo", "finanzas", "contabilidad", "recursos humanos", "planificación estratégica", "marketing", "ventas", "negociación", "emprendimiento",
        # Salud
        "enfermería", "medicina", "atención al paciente", "primeros auxilios", "farmacología", "psicología", "nutrición", "odontología",
        # Idiomas
        "inglés", "francés", "alemán", "portugués", "traducción", "interpretación", "español",
        # Arte y comunicación
        "dibujo", "pintura", "fotografía", "redacción", "comunicación oral", "edición de video", "diseño gráfico", "música", "teatro",
        # Ciencias
        "investigación", "análisis de datos", "laboratorio", "biología", "química", "física", "matemáticas", "estadística",
        # Ingeniería y manufactura
        "autocad", "solidworks", "diseño industrial", "mecánica", "electricidad", "electrónica",
        # Habilidades blandas
        "Trabajo en equipo", "Comunicación", "Resolución de problemas", "Creatividad", "Adaptabilidad", "Gestión del tiempo", "Pensamiento crítico", "Empatía",
    ]
    habilidades_detectadas = [h for h in habilidades_comunes if h.lower() in texto.lower()]

    # Extra: detectar posibles habilidades/frases nuevas (palabras/frases con mayúscula que no estén en la lista)
    palabras = set([w.strip('.,;:()') for w in texto.split() if w.istitle() and len(w) > 3])
    nuevas = [p for p in palabras if p not in habilidades_comunes and p not in habilidades_detectadas]

    return {
        'habilidades': habilidades_detectadas,
        'otras_habilidades': nuevas
    }
