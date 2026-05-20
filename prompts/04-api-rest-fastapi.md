# Prompt #04

**Fecha y hora:** 2026-05-20 14:30

**Propósito en una línea:** Construir una API REST completa en FastAPI para gestionar préstamos de libros con datos en memoria

**Etapa del taller:** 1

**IA usada:** GitHub Copilot

---

### Prompt enviado (literal)

```
Dentro de la carpeta Version_1 ubicada en la raíz del proyecto, construye una API REST en Python utilizando FastAPI para gestionar los préstamos de libros de una biblioteca universitaria, implementando datos en memoria y desarrollando específicamente los endpoints para listar los libros, crear préstamos, consultar los préstamos vigentes y registrar la devolución de los libros
```

---

### Resumen de la respuesta de la IA

Creó una aplicación FastAPI completa con 11 archivos: `main.py` (con 4 endpoints principales + 2 auxiliares), `requirements.txt` (FastAPI, Uvicorn, Pydantic), `README.md` (documentación extensiva), `ARQUITECTURA.md` (diagrama de capas y flujos), `EJEMPLOS.md` (5 opciones de uso), `requests.http` (peticiones HTTP), `.env.example`, `.gitignore`, y scripts `run.bat` y `run.sh`. Implementó modelos Pydantic, repositorio en memoria con 3 libros y 3 estudiantes iniciales, validaciones robustas, gestión de estados (ACTIVO/VENCIDO/DEVUELTO), y documentación interactiva Swagger/ReDoc. Decisiones autónomas: agregó endpoints de health check y bienvenida, estructura de capas, manejo de excepciones detallado, y múltiples opciones de ejecución.

---

### Mi evaluación

**¿La respuesta cumplió con lo que pedí?**

- [x] Completamente.

**¿La acepté tal cual o la modifiqué?**

- [x] Tal cual.

**¿Qué aprendí de esta interacción?**

Copilot entiende arquitectura de capas y patrones de desarrollo profesionales sin indicarlos explícitamente. Cuando pido "gestionar préstamos", automáticamente estructura con repositorios, modelos y validaciones. La documentación y ejemplos extras demuestran iniciativa para anticipar necesidades del usuario. Los scripts de ejecución automática muestran atención al UX de onboarding.

---
