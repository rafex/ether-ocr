# DECISIONS.md

Registro de decisiones persistentes del proyecto.

## Cuando registrar aqui

Registrar una decision cuando cambie algo que futuras iniciativas
o agentes deban respetar:

- la arquitectura del sistema
- una convencion de codigo o de documentacion
- una tecnologia o dependencia base
- un tradeoff que condicione trabajo futuro

Ver `AGENTS.md` para entender la separacion semantica entre este
archivo y `SPEC.md`.

## Cuando leer este archivo

Antes de iniciar una nueva iniciativa, revisar si alguna decision
registrada condiciona el diseno o la implementacion.

## Formato sugerido

### DEC-0001 - Titulo de la decision

- Fecha: YYYY-MM-DD
- Estado: `proposed | accepted | deprecated | replaced`
- Relacionado con specs:
- Relacionado con tareas:
- Contexto: que problema obligo la decision
- Decision: que se decidio exactamente
- Consecuencias: costos, beneficios y limites
- Reemplaza: DEC-XXXX o `none`

### DEC-0001 - Usar Poppler como extractor PDF inicial

- Fecha: 2026-06-03
- Estado: accepted
- Relacionado con specs: pdf-to-rag-text
- Relacionado con tareas: TASK-0002
- Contexto: El RAG consumidor acepta texto plano UTF-8 y los PDFs deben convertirse antes de subirlos. Implementar parsing PDF completo en Python agregaria dependencias y complejidad innecesaria para PDFs con capa de texto.
- Decision: Usar `pdftotext -layout` de Poppler como dependencia externa para extraer texto de PDFs; la limpieza y validacion viven en Python.
- Consecuencias: La herramienta es simple y estable para PDFs textuales, pero requiere instalar Poppler y no resuelve PDFs escaneados sin OCR.
- Reemplaza: none

### DEC-0002 — Usar Tesseract como motor OCR

- Fecha: 2026-06-04
- Estado: `accepted`
- Relacionado con specs:
- Contexto: Los PDFs escaneados e imagenes no tienen capa de texto extraible con Poppler. Se necesita un motor OCR para extraer texto de estos documentos. Tesseract es el motor open-source mas maduro con soporte multi-idioma y bindings Python estables (pytesseract).
- Decisión: Usar Tesseract OCR como motor principal para PDFs escaneados e imagenes. La conversion PDF→imagen se hace con pdf2image + Poppler. Las dependencias se instalan en el contenedor Docker, no en el host. El pipeline decide automaticamente si usar Poppler o Tesseract segun el tipo de entrada.
- Consecuencias: Beneficios: OCR funcional para documentos escaneados, sin dependencias propietarias. Costos: requiere instalar Tesseract + datos de idioma (~50MB por idioma), la calidad depende de la resolucion de entrada, el procesamiento es mas lento que Poppler para PDFs con capa de texto.
- Reemplaza: none

### DEC-0003 — Usar FastAPI como framework REST

- Fecha: 2026-06-04
- Estado: `accepted`
- Relacionado con specs:
- Contexto: ether-ocr necesita exponer una API REST. Se evaluaron FastAPI y Flask. FastAPI ofrece validacion nativa con Pydantic, generacion automatica de OpenAPI, soporte async nativo y mejor rendimiento que Flask. Es el framework mas usado en Python moderno para APIs.
- Decisión: Usar FastAPI + uvicorn como framework para la API REST. Usar Pydantic v2 para schemas de request/response. La API se versiona con prefijo /api/v1/.
- Consecuencias: Beneficios: OpenAPI auto-generado, validacion de tipos en runtime, docs interactivos (/docs), mejor ecosistema async. Costos: dependencia adicional (~5MB), curva de aprendizaje si el equipo solo conoce Flask. La decision es reversible — FastAPI y Flask comparten概念 similares.
- Reemplaza: none
