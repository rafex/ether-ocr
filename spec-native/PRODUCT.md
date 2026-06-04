# PRODUCT.md

Fuente de verdad del producto.

## Problema

Los sistemas RAG necesitan texto plano UTF-8 limpio, pero los documentos
llegan en formatos heterogeneos: PDFs con capa de texto, PDFs escaneados
sin capa de texto, imagenes (PNG, JPEG, TIFF) y texto crudo con artefactos
de formato. Extraer, limpiar y validar ese texto requiere herramientas
especializadas que hoy no estan unificadas ni expuestas como servicio.

## Usuarios

- **Agentes de IA y pipelines RAG**: necesitan un endpoint que reciba
  documentos y devuelva texto limpio listo para indexar, sin acoplarse
  a la logica de extraccion.
- **Desarrolladores de plataformas de documentos**: necesitan una API
  autocontenida que puedan desplegar en su infraestructura sin depender
  de servicios cloud externos.

## Objetivos

- **API REST unificada**: un solo servicio que acepta PDFs, imagenes y
  texto plano, y devuelve texto UTF-8 limpio validado.
- **OCR + extraccion directa**: decide automaticamente si usar Poppler
  (extraccion directa) o Tesseract (OCR) segun el tipo de entrada.
- **Autenticacion**: proteger los endpoints con API key o JWT.
- **Procesamiento batch**: aceptar multiples archivos en una sola
  peticion.
- **Metadatos enriquecidos**: devolver paginas procesadas, confianza OCR,
  idioma detectado y tamanio del texto resultante.
- **Respuesta eficiente para textos largos**: cuando el texto extraido
  es muy grande, devolver una referencia a un archivo JSON o un tar.gz
  comprimido en lugar de saturar el body de la respuesta HTTP.
- **Container-first**: toda la herramienta se despliega con Docker,
  sin depender de servicios externos.

## No objetivos

- Este producto **NO** inserta datos en ningun RAG. Solo extrae, limpia
  y devuelve texto. La insercion en `faiss-poc` u otros sistemas la
  realiza un agente externo.
- No es un servicio de almacenamiento de documentos.
- No entrena modelos de OCR personalizados.
- No expone interfaz grafica.

## Valor diferencial

- **Autocontenido**: Poppler + Tesseract + Python en una imagen Docker.
  No requiere APIs cloud ni servicios externos.
- **Pipeline inteligente**: detecta automaticamente si un PDF tiene capa
  de texto (usa Poppler, rapido) o necesita OCR (usa Tesseract).
- **Respuesta adaptativa**: para documentos cortos devuelve el texto
  inline; para documentos extensos devuelve un archivo comprimido (tar.gz)
  o una referencia JSON.
- **Disenado para agentes**: la API esta pensada para ser consumida por
  agentes de IA y pipelines automatizados, no por humanos directos.
- **Listo para Rust**: el diseno separa claramente la capa de transporte
  (API) del motor de procesamiento, facilitando la migracion futura del
  motor a Rust sin romper la API.
