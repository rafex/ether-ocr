# SPEC.md

## Metadata

- ID: pdf-to-rag-text
- Estado: done
- Owner: rafex
- Fecha de creacion: 2026-06-03
- Ultima actualizacion: 2026-06-03

## Problema

El RAG de `/Users/rafex/repository/github/rafex/faiss-poc` acepta archivos de texto plano UTF-8. Los PDF deben convertirse y limpiarse antes de subirlos para evitar que el backend rechace binarios, Markdown, HTML o caracteres de control.

## Objetivo

Crear en `ether-ocr/python/src` una herramienta Python que convierta documentos PDF o texto extraido a texto plano UTF-8, normalice artefactos frecuentes de PDF y valide que la salida sea compatible con el RAG.

## Alcance

- Extraer texto de PDF usando `pdftotext -layout` cuando la entrada sea `.pdf`.
- Limpiar numeracion de pagina, espacios de layout, saltos excesivos y separar articulos/secciones.
- Validar que la salida sea texto plano UTF-8 sin Markdown, HTML ni caracteres de control.
- Exponer CLI ejecutable con `python -m ether_ocr`.
- Mantener la implementacion en Python bajo `python/src`.

## Fuera de alcance

- OCR visual de PDFs escaneados sin capa de texto.
- Subida automatica al API del RAG.
- Implementacion Rust.
- Dependencias pesadas de parsing PDF dentro de Python.

## Criterios de aceptacion

- Dado un PDF con capa de texto, la CLI genera un `.txt` limpio en UTF-8.
- Dado un `.txt` crudo, la CLI genera un `.txt` limpio sin invocar `pdftotext`.
- La validacion reporta errores descriptivos para Markdown, HTML o caracteres de control.
- La logica central tiene tests unitarios sin requerir Poppler.
- La documentacion SpecNative refleja comandos y estructura nueva.

## Validacion

- `python3 -m unittest discover -s python/tests`
- Prueba manual opcional con Poppler instalado:
  `PYTHONPATH=python/src python3 -m ether_ocr prepare entrada.pdf salida.txt`
