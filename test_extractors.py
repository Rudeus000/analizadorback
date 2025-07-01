#!/usr/bin/env python3
"""
Script de prueba para demostrar las nuevas capacidades de extracción de CV
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.extractors import *
from app.services.cv_processor import procesar_cv_avanzado

def test_cv_ejemplo():
    """
    Prueba con un CV de ejemplo para demostrar las capacidades
    """
    
    cv_ejemplo = """
    JUAN CARLOS MARTÍNEZ LÓPEZ
    Desarrollador Full Stack Senior
    juan.martinez@email.com | +34 666 123 456
    Madrid, España
    linkedin.com/in/juanmartinez
    github.com/juanmartinez
    
    EXPERIENCIA LABORAL
    
    Desarrollador Full Stack Senior
    TechCorp Inc. | Enero 2020 - Presente
    - Desarrollo de aplicaciones web con React, Node.js y MongoDB
    - Implementación de arquitecturas microservicios con Docker y Kubernetes
    - Liderazgo de equipo de 5 desarrolladores
    
    Desarrollador Frontend
    StartupXYZ S.L. | Marzo 2018 - Diciembre 2019
    - Desarrollo de interfaces con Angular y TypeScript
    - Optimización de rendimiento y SEO
    
    EDUCACIÓN
    
    Ingeniería Informática
    Universidad Politécnica de Madrid | Graduado en 2017
    
    Maestría en Desarrollo de Software
    Universidad Complutense | Finalizado en 2018
    
    CERTIFICACIONES
    
    AWS Certified Solutions Architect - Associate (2022)
    Microsoft Certified: Azure Developer Associate (2021)
    React Professional Certification (2020)
    TOEFL Score: 95 (2019)
    
    PROYECTOS
    
    E-commerce Platform
    github.com/juanmartinez/ecommerce
    React, Node.js, MongoDB, AWS
    
    Task Management App
    github.com/juanmartinez/taskapp
    Angular, Firebase, TypeScript
    
    HABILIDADES TÉCNICAS
    
    Lenguajes: JavaScript, TypeScript, Python, Java, SQL
    Frameworks: React, Angular, Node.js, Express, Django
    Bases de datos: MongoDB, PostgreSQL, MySQL, Redis
    Herramientas: Git, Docker, Kubernetes, Jenkins, Jira
    Cloud: AWS, Azure, Google Cloud, Firebase
    Metodologías: Agile, Scrum, DevOps, CI/CD
    
    IDIOMAS
    
    Español - Nativo
    Inglés - Avanzado
    Francés - Intermedio
    
    SOFT SKILLS
    
    Liderazgo, Comunicación, Trabajo en equipo, Resolución de problemas, 
    Creatividad, Adaptabilidad, Gestión del tiempo
    """
    
    print("🔍 PROCESANDO CV DE EJEMPLO")
    print("=" * 50)
    
    # Procesar el CV
    resultado = procesar_cv_avanzado(cv_ejemplo)
    
    # Mostrar resultados
    print(f"📝 NOMBRE: {resultado['nombre']}")
    print(f"📧 EMAIL: {resultado['email']}")
    print(f"📱 TELÉFONO: {resultado['telefono']}")
    print(f"📍 UBICACIÓN: {resultado['ubicacion']}")
    print(f"🔗 LINKEDIN: {resultado['linkedin']}")
    print(f"🐙 GITHUB: {resultado['github']}")
    print(f"🌍 IDIOMA: {resultado['idioma_detectado']}")
    print(f"⏰ AÑOS EXPERIENCIA: {resultado['experiencia_anos']}")
    print(f"📊 PUNTUACIÓN APTITUD: {resultado['puntuacion_aptitud']}%")
    
    print("\n💼 EXPERIENCIA LABORAL:")
    for i, exp in enumerate(resultado['experiencia_laboral'], 1):
        print(f"  {i}. {exp['puesto']} en {exp['empresa']}")
        print(f"     Fechas: {exp.get('fechas', 'No especificadas')}")
    
    print("\n🎓 EDUCACIÓN:")
    for i, edu in enumerate(resultado['educacion'], 1):
        print(f"  {i}. {edu['titulo']}")
        print(f"     Institución: {edu['institucion']}")
        print(f"     Graduación: {edu['fecha_graduacion']}")
    
    print("\n🏆 CERTIFICACIONES:")
    for i, cert in enumerate(resultado['certificaciones'], 1):
        print(f"  {i}. {cert['nombre']} ({cert['fecha']}) - {cert['tipo']}")
    
    print("\n🚀 PROYECTOS:")
    for i, proj in enumerate(resultado['proyectos'], 1):
        print(f"  {i}. {proj['nombre']}")
        print(f"     URL: {proj['url']}")
        print(f"     Tecnologías: {', '.join(proj['tecnologias'])}")
    
    print("\n🗣️ IDIOMAS:")
    for i, idioma in enumerate(resultado['idiomas'], 1):
        print(f"  {i}. {idioma['idioma']} - {idioma['nivel']}")
    
    print("\n🛠️ HABILIDADES DETALLADAS:")
    habilidades = resultado['habilidades_detalladas']
    for categoria, skills in habilidades.items():
        if skills:
            print(f"  {categoria.replace('_', ' ').title()}: {', '.join(skills)}")
    
    print("\n" + "=" * 50)
    print("✅ PROCESAMIENTO COMPLETADO")
    print(f"📈 PUNTUACIÓN FINAL: {resultado['puntuacion_aptitud']}%")

if __name__ == "__main__":
    test_cv_ejemplo() 