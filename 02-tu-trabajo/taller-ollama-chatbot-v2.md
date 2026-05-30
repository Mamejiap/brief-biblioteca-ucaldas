# Taller — Chatbot de Pruebas con Ollama
## Versión 2 — Reglas expandidas y endpoints auditados

**Propósito:** instalar un modelo de lenguaje local con Ollama y construir un chatbot que te ayude a generar y ejecutar pruebas contra tu API de la Biblioteca UCaldas.

**Duración estimada:** 60 – 80 minutos  
**Requisito previo:** tu API debe estar corriendo en `localhost:3001` (Etapa 2 completada)

> **Cambios respecto a v1:**  
> — SYSTEM_PROMPT expandido de 8 a 15 reglas de negocio (integración con `plantilla-especificacion.md`).  
> — Lista de endpoints corregida y sincronizada con los routers reales de Version_2.  
> — Parte 5 ampliada con 6 preguntas adicionales desafiantes.

---

## ¿Por qué Ollama para pruebas?

Cuando le pides a una IA que te genere tests anclándola a tus reglas de negocio, el resultado depende del contexto que le das. Con Ollama puedes:

- Correr el modelo localmente, sin enviar tu código a servidores externos.
- Construir un chatbot especializado que ya conoce las reglas RN1–RN15 antes de que le preguntes.
- Iterar rápido: cambia el system prompt y vuelve a correr sin gastar créditos de API.

---

## Parte 1 — Instalar Ollama

### macOS

```bash
brew install ollama
```

O descarga el instalador desde [ollama.com/download](https://ollama.com/download) y ejecuta el `.dmg`.

Verifica que quedó instalado:

```bash
ollama --version
```

### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows

Descarga el instalador `.exe` desde [ollama.com/download](https://ollama.com/download) y sigue el asistente.

---

## Parte 2 — Elegir y descargar un modelo

Ollama sirve modelos localmente. Elige uno según la RAM disponible en tu máquina:

| Modelo              | RAM mínima | Perfil                                             |
|---------------------|------------|----------------------------------------------------|
| `llama3.2:1b`       | 2 GB       | Muy liviano, respuestas cortas                     |
| `llama3.2:3b`       | 4 GB       | Buen balance velocidad / calidad                   |
| `qwen2.5-coder:7b`  | 8 GB       | Especializado en código, mejor para generar tests  |
| `mistral:7b`        | 8 GB       | General, bueno para razonamiento                   |

**Recomendado si tienes 8 GB o más:**

```bash
ollama pull qwen2.5-coder:7b
```

**Recomendado si tu máquina es limitada:**

```bash
ollama pull llama3.2:3b
```

Espera a que el modelo termine de descargar (puede tardar varios minutos según tu conexión). El progreso se muestra en la terminal.

Verifica que quedó disponible:

```bash
ollama list
```

---

## Parte 3 — Probar el modelo desde la terminal

Antes de construir el chatbot, confirma que el modelo responde:

```bash
ollama run qwen2.5-coder:7b
```

Escribe algo simple y presiona Enter:

```
>>> Hola, ¿puedes generar un comando curl para hacer GET a localhost:3001/api/libros?
```

Si responde correctamente, el modelo funciona. Sal con `/bye` o Ctrl+D.

---

## Parte 4 — Construir el chatbot de pruebas

El chatbot es un script Node.js que:

1. Precarga las reglas de negocio como system prompt.
2. Acepta tu pregunta en lenguaje natural.
3. Le pregunta al modelo y muestra la respuesta.
4. Opcionalmente ejecuta el `curl` generado y te muestra el resultado real.

### 4.1 Crear la carpeta del chatbot

Dentro de tu carpeta de entrega:

```bash
mkdir chatbot-pruebas
cd chatbot-pruebas
npm init -y
npm install node-fetch readline
```

> Si tu Node.js es v18 o superior, `fetch` ya viene incluido y puedes omitir `node-fetch`.

### 4.2 Crear el archivo principal

Crea el archivo `chatbot-pruebas/chatbot.js` con este contenido. Ajusta `MODELO` si usaste uno diferente.

> **Nota de auditoría v2:** la sección `REGLAS DE NEGOCIO` fue expandida de 8 a 15 reglas
> sincronizando la guía original con `plantilla-especificacion.md`. La sección
> `ENDPOINTS CONOCIDOS` fue corregida contra los routers reales de Version_2
> (se eliminaron 2 endpoints inexistentes y se añadieron 7 que faltaban).

```js
const readline = require("readline");
const { execSync } = require("child_process");

const BASE_URL = "http://localhost:3001";
const OLLAMA_URL = "http://localhost:11434/api/chat";
const MODELO = "qwen2.5-coder:7b"; // cambia si usaste otro

const SYSTEM_PROMPT = `
Eres un asistente de QA especializado en probar una API REST de biblioteca universitaria.

BASE URL del servidor: ${BASE_URL}

REGLAS DE NEGOCIO QUE DEBES CONOCER:

— Préstamos: quién puede pedir y bajo qué condiciones —
RN1. Un estudiante de pregrado no puede tener más de 3 préstamos activos simultáneamente. Si lo intenta: 409 Conflict {error: "limite_prestamos_alcanzado", limite: 3, actuales: N}.
RN2. Un estudiante de posgrado no puede tener más de 5 préstamos activos simultáneamente. Si lo intenta: 409 Conflict {error: "limite_prestamos_alcanzado", limite: 5, actuales: N}.
RN3. Si un estudiante tiene al menos un préstamo vencido sin devolver, no puede solicitar nuevos préstamos: 409 Conflict {error: "prestamo_vencido_pendiente"}.
RN4. Si un estudiante tiene multas con estado "pendiente" (sin pagar), no puede solicitar nuevos préstamos: 409 Conflict {error: "multa_pendiente", monto_total: N}.
RN5. Un ejemplar que ya está prestado (estado "prestado") no puede prestarse de nuevo hasta ser devuelto: 409 Conflict {error: "ejemplar_no_disponible"}.

— Plazos —
RN6. El plazo de préstamo depende del tipo de libro: 15 días para libros normales (alta_demanda=false), 3 días para libros de alta demanda (alta_demanda=true). Este plazo se calcula automáticamente al crear el préstamo: fecha_devolucion_esperada = fecha_prestamo + plazo_dias.

— Devolución —
RN7. Al registrar una devolución (PUT /api/prestamos/:id/devolucion): el préstamo pasa a estado "devuelto", el ejemplar vuelve a estado "disponible", y se genera automáticamente una multa si hubo retraso. Si el préstamo ya fue devuelto: 409 Conflict {error: "prestamo_ya_devuelto"}.

— Multas —
RN8. La multa por devolución tardía es de 2000 pesos por día de retraso por cada libro. Fórmula: dias_retraso × 2000. El bloqueo por multa (RN4) se levanta automáticamente cuando todas las multas del estudiante pasan a estado "pagada".

— Renovación —
RN9. La renovación de un préstamo (PUT /api/prestamos/:id/renovar) solo es posible si: (a) el préstamo está activo y no vencido, (b) no existe una solicitud de reserva activa de otro estudiante esperando el mismo libro. Si alguna condición falla: 409 Conflict {error: "renovacion_no_permitida"}.
RN10. Los libros de alta demanda (alta_demanda=true) NO pueden renovarse bajo ninguna circunstancia, incluso si no hay lista de espera. Plazo máximo fijo: 3 días. Si se intenta renovar: 409 Conflict {error: "renovacion_no_permitida", razon: "alta_demanda"}.

— Préstamos vencidos —
RN11. Un préstamo se considera vencido cuando tiene estado "activo" y su fecha_devolucion_esperada es anterior a la fecha actual. El estado "vencido" NO se almacena en la base de datos: se calcula dinámicamente en cada solicitud. El endpoint GET /api/prestamos/vencidos retorna la lista calculada en tiempo real.

— Historial y consultas —
RN12. El historial de un estudiante (GET /api/estudiantes/:id/historial) incluye todos sus préstamos (activos, devueltos y vencidos), todas sus multas y el monto total de multas pendientes. Si el estudiante no existe: 404 Not Found.

— Reservas —
RN13. Un estudiante puede registrar una solicitud de reserva (POST /api/reservas) para un libro que está completamente prestado. La reserva bloquea la renovación de cualquier préstamo activo de ese libro (ver RN9). Si el estudiante ya tiene una reserva activa del mismo libro: 409 Conflict.
RN14. Las reservas se atienden en orden FIFO (primera en entrar, primera en salir) según fecha_reserva. Cuando un ejemplar queda disponible, el estudiante con la reserva activa más antigua sobre ese libro tiene prioridad.

— Cancelación de reserva —
RN15. Una reserva puede cancelarse (DELETE /api/reservas/:id) si está en estado "activa". Al cancelarse, deja de bloquear renovaciones del préstamo correspondiente.

ENDPOINTS CONOCIDOS (Version_2 — rutas reales auditadas contra el código):
- GET    /api/libros                             Catálogo con filtros opcionales: ?sala=&alta_demanda=&disponible=
- POST   /api/libros                             Crear libro {id, titulo, autor, sala, alta_demanda}
- GET    /api/libros/:id                         Detalle de un libro con sus ejemplares
- POST   /api/libros/:id/ejemplares             Agregar ejemplar a un libro {id}
- POST   /api/estudiantes                        Crear estudiante {id, nombre, programa, semestre, tipo}
- GET    /api/estudiantes/:id                    Obtener datos de un estudiante
- GET    /api/estudiantes/:id/historial          Historial: préstamos + multas + monto pendiente
- POST   /api/prestamos                          Crear préstamo {estudiante_id, ejemplar_id, fecha_prestamo?}
- GET    /api/prestamos/vencidos                 Listar préstamos vencidos (cálculo dinámico)
- GET    /api/prestamos/:id                      Obtener un préstamo por ID
- PUT    /api/prestamos/:id/devolucion           Registrar devolución (body vacío)
- PUT    /api/prestamos/:id/renovar              Renovar préstamo (body vacío)
- POST   /api/reservas                           Crear reserva {estudiante_id, libro_id}
- DELETE /api/reservas/:id                       Cancelar reserva

NOTAS DE IMPLEMENTACIÓN:
- Todos los campos usan snake_case: estudiante_id, ejemplar_id, alta_demanda, fecha_prestamo.
- POST /api/prestamos acepta fecha_prestamo opcional (formato YYYY-MM-DD) para simular fechas pasadas en pruebas (Opción A).
- Los errores de validación Pydantic retornan 422 (no 400). Ambos son válidos: 400 para errores de negocio, 422 para errores de tipo/schema.
- GET /api/estudiantes (listar todos) NO existe en Version_2. Usa POST para crear y GET /:id para consultar individualmente.
- GET /api/prestamos (listar todos) NO existe en Version_2. Usa GET /api/prestamos/vencidos o GET /api/prestamos/:id.

INSTRUCCIONES DE COMPORTAMIENTO:
- Cuando el usuario pida probar una regla, genera el comando curl exacto para hacerlo.
- Primero genera los datos de prueba necesarios (crear estudiante, crear libro, etc.).
- Explica brevemente qué debe pasar y por qué código HTTP esperas.
- Si el usuario te pregunta por un error, analiza el código HTTP y el body de la respuesta.
- Si el usuario te pide ejecutar el curl, responde con el comando y di "EJECUTAR:" antes del comando para que el sistema lo detecte.
- Sé conciso. No repitas información que el usuario ya sabe.
`.trim();

const historial = [{ role: "system", content: SYSTEM_PROMPT }];

async function preguntarAlModelo(mensajeUsuario) {
  historial.push({ role: "user", content: mensajeUsuario });

  const respuesta = await fetch(OLLAMA_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: MODELO,
      messages: historial,
      stream: false,
    }),
  });

  if (!respuesta.ok) {
    throw new Error(`Ollama respondió ${respuesta.status}. ¿Está corriendo? Ejecuta: ollama serve`);
  }

  const datos = await respuesta.json();
  const contenido = datos.message.content;
  historial.push({ role: "assistant", content: contenido });
  return contenido;
}

function ejecutarCurl(respuestaModelo) {
  const lineas = respuestaModelo.split("\n");
  for (const linea of lineas) {
    if (linea.trim().startsWith("EJECUTAR:")) {
      const comando = linea.replace("EJECUTAR:", "").trim();
      console.log(`\n[EJECUTANDO]: ${comando}\n`);
      try {
        const resultado = execSync(comando, { encoding: "utf-8", timeout: 10000 });
        console.log("[RESULTADO]:\n" + resultado);
      } catch (err) {
        console.log("[RESULTADO]:\n" + (err.stdout || err.message));
      }
      return true;
    }
  }
  return false;
}

async function iniciar() {
  console.log("=== Chatbot de Pruebas — Biblioteca UCaldas v2 ===");
  console.log(`Modelo: ${MODELO}`);
  console.log(`Servidor: ${BASE_URL}`);
  console.log('Escribe tu pregunta. Ejemplos:');
  console.log('  "prueba que un pregrado no pueda tener 4 préstamos"');
  console.log('  "ejecuta la prueba RN6 para el plazo de alta demanda"');
  console.log('  "crea datos de prueba para RN1"');
  console.log('Escribe "salir" para terminar.\n');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const preguntar = () => {
    rl.question("Tú: ", async (entrada) => {
      if (entrada.toLowerCase() === "salir") {
        console.log("Hasta luego.");
        rl.close();
        return;
      }

      if (!entrada.trim()) {
        preguntar();
        return;
      }

      try {
        const respuesta = await preguntarAlModelo(entrada);
        console.log(`\nChatbot: ${respuesta}\n`);
        ejecutarCurl(respuesta);
      } catch (err) {
        console.error(`Error: ${err.message}`);
      }

      preguntar();
    });
  };

  preguntar();
}

iniciar();
```

### 4.3 Iniciar Ollama en segundo plano

Abre una terminal separada y ejecuta:

```bash
ollama serve
```

Deja esa terminal abierta. Ollama expone la API en `http://localhost:11434`.

### 4.4 Correr el chatbot

En otra terminal (con tu API también corriendo en `localhost:3001`):

```bash
node chatbot.js
```

---

## Parte 5 — Pruebas guiadas con el chatbot

Haz estas preguntas al chatbot en orden. Registra las respuestas en tu `bitacora.md`.

### Sesión 1 — Datos de prueba

```
Tú: crea los datos de prueba base para todas las reglas: un estudiante pregrado EST-PRE-01, uno posgrado EST-POS-01, un libro normal LIB-001 con 6 ejemplares y un libro de alta demanda LIB-002 con 1 ejemplar
```

Ejecuta los comandos que genere el chatbot uno por uno.

### Sesión 2 — RN1 y RN2

```
Tú: genera la prueba RN1 completa: crear los 3 préstamos válidos para pregrado y luego intentar el cuarto

Tú: ahora haz lo mismo para RN2 con el estudiante de posgrado, recuerda que su límite es 5
```

### Sesión 3 — RN5 y RN6

```
Tú: prueba que un ejemplar ya prestado no se puede prestar de nuevo (RN5)

Tú: muéstrame cómo verificar que el plazo del préstamo es correcto para un libro normal versus uno de alta demanda (RN6)
```

### Sesión 4 — Validaciones

```
Tú: genera pruebas de entradas inválidas: body vacío, estudiante inexistente y ejemplar inexistente

Tú: el resultado del body vacío fue { "error": "..." } con código 400. ¿Eso es correcto según la especificación?
```

### Sesión 5 — Análisis de un fallo

Si alguna prueba devuelve un resultado inesperado, dile al chatbot:

```
Tú: el endpoint POST /api/prestamos devolvió 200 OK en lugar de 409 cuando el estudiante ya tiene 3 préstamos. El body fue: { "id": "P-004", ... }. ¿Qué regla está violando y en qué archivo debería buscar el problema?
```

---

### Sesión 6 — Pruebas desafiantes adicionales (v2)

Las siguientes 6 preguntas validan reglas avanzadas y casos límite. Son intencionalmente difíciles para evaluar si el chatbot mantiene coherencia con el sistema de reglas completo.

#### Pregunta 6-A — Conflicto de reglas simultáneas

```
Tú: un estudiante de pregrado tiene exactamente 3 préstamos activos, uno de ellos está vencido y además tiene una multa pendiente de $6.000.
Intenta crear un nuevo préstamo para ese estudiante. ¿Qué regla se activa primero según el código de Version_2 y qué código HTTP esperas? Dame el curl exacto para reproducirlo.
```

> *Propósito:* verificar que el chatbot entiende el orden de evaluación de RN1, RN3 y RN4. En Version_2 el orden es: límite → vencido → multa → disponibilidad.

#### Pregunta 6-B — Renovación de libro de alta demanda

```
Tú: tengo un préstamo activo del ejemplar EJ-002-01 (que pertenece a LIB-002, un libro de alta demanda) y no hay ninguna reserva pendiente sobre ese libro.
¿Puedo renovar ese préstamo? Dame el curl para intentarlo y explica qué respuesta esperas según las reglas de la biblioteca.
```

> *Propósito:* verificar que el chatbot conoce RN10 (alta demanda no se renueva) y no confunde con RN9 (lista de espera).

#### Pregunta 6-C — Cálculo de multa con inyección de fecha

```
Tú: quiero probar RN8 sin esperar días reales. Sé que POST /api/prestamos acepta el campo opcional fecha_prestamo.
Dame el curl completo para: (1) crear un préstamo con fecha 20 días atrás sobre un libro normal, (2) devolver ese préstamo hoy. ¿Cuántos días de retraso habrá y cuál será el monto exacto de la multa?
```

> *Propósito:* verificar que el chatbot conoce la Opción A de inyección de fecha y calcula correctamente: plazo 15 días, prestado hace 20 → 5 días de retraso → $10.000.

#### Pregunta 6-D — Reserva que bloquea renovación

```
Tú: EST-PRE-01 tiene un préstamo activo de EJ-001-01 (LIB-001, libro normal, no vencido).
EST-POS-01 quiere el mismo libro y hace una reserva. Ahora EST-PRE-01 intenta renovar.
Dame los tres curls en orden: crear la reserva, intentar la renovación y explicar por qué debe fallar.
```

> *Propósito:* verificar que el chatbot entiende la interacción entre RN9 y RN13 (reserva activa bloquea renovación).

#### Pregunta 6-E — Desbloqueo después de pago de multa

```
Tú: EST-PRE-01 fue bloqueado por una multa de $4.000 (RN4). En nuestra base de datos (SQLite), ¿cómo marcaríamos esa multa como pagada para desbloquear al estudiante? ¿Existe un endpoint en la API para eso? Si no existe, ¿qué endpoint de la especificación original lo contemplaba y por qué no se implementó en Version_2?
```

> *Propósito:* verificar que el chatbot detecta la brecha entre la especificación (POST /multas/:id/pago) y Version_2 (que no implementa ese endpoint). Es un hallazgo de completitud válido.

#### Pregunta 6-F — Consistencia de nomenclatura al cambiar de versión

```
Tú: la guía original de pruebas usa "estudianteId" y "ejemplarId" en el body del curl. Pero cuando ejecuto el curl contra localhost:3001 me da 422. ¿Por qué falla y cuál es el body correcto para Version_2?
```

> *Propósito:* verificar que el chatbot conoce la diferencia de nomenclatura camelCase (V1) vs snake_case (V2) y puede explicar por qué Pydantic rechaza con 422 en lugar de 400.

---

## Parte 6 — Ajustar el system prompt

El system prompt es el conocimiento que el chatbot tiene desde el inicio. Es importante que refleje tu implementación real.

**Tarea:** abre `chatbot.js` y modifica la sección `ENDPOINTS CONOCIDOS` para que coincida exactamente con las rutas que generó tu API (quizás son `/prestamos` sin el prefijo `/api`, o usan otro verbo HTTP).

También puedes agregar:

```js
DECISIONES DE IMPLEMENTACIÓN:
- D1: Los días de multa se cuentan como días calendario.
- D2: El estado de un préstamo puede ser: activo, devuelto. El estado "vencido" se calcula dinámicamente.
- D3: Libro y Ejemplar son entidades separadas para controlar disponibilidad individualmente.
- D4: Sin autenticación en esta versión — cualquier cliente puede crear préstamos y devoluciones.
- D5: POST /multas/:id/pago existe en la especificación pero NO está implementado en Version_2.
```

Guarda el prompt modificado como `prompts/07-system-prompt-chatbot.md` para tu entrega.

---

## Parte 7 — Registro en la bitácora

Al final de esta sesión, agrega una sección a tu `bitacora.md`:

```markdown
## Chatbot Ollama — Registro

### Modelo usado
- Nombre: qwen2.5-coder:7b (o el que usaste)
- RAM consumida aproximada: X GB

### Preguntas útiles que generó el chatbot
| Pregunta que hice | Qué generó el chatbot | ¿Fue útil? |
|-------------------|-----------------------|------------|
| ...               | ...                   | Sí / No    |

### Limitaciones observadas
- ¿El chatbot inventó endpoints que no existen?
- ¿Confundió reglas entre sí?
- ¿Tuvo que corregirle algo?

### Comparación: chatbot local vs ChatGPT/Claude en la nube
- ¿Qué diferencias notaste en la calidad de las respuestas?
- ¿Qué ventajas tiene correrlo localmente?
```

---

## Solución de problemas comunes

### "fetch is not defined"

Tu versión de Node.js es menor a 18. Instala el paquete:

```bash
npm install node-fetch
```

Y agrega al inicio de `chatbot.js`:

```js
const fetch = (...args) => import("node-fetch").then(({ default: f }) => f(...args));
```

### "Error: Ollama respondió 404"

El modelo que escribiste en `MODELO` no está instalado. Verifica con:

```bash
ollama list
```

Y ajusta el valor de `MODELO` en `chatbot.js`.

### "Error: connect ECONNREFUSED 127.0.0.1:11434"

Ollama no está corriendo. Ejecútalo:

```bash
ollama serve
```

### El chatbot no genera comandos curl

El modelo más pequeño (1b o 3b) a veces responde en lenguaje natural sin generar comandos. Reformula la pregunta siendo más explícito:

```
Tú: dame el comando curl exacto para probar RN1, incluyendo los headers y el body JSON
```

### La respuesta es muy lenta

Es normal con modelos de 7b en máquinas sin GPU. Mientras esperas, lee el código que generó tu API en la Etapa 2. Si la lentitud es inaceptable, cambia a `llama3.2:3b`:

```bash
ollama pull llama3.2:3b
```

Y actualiza `MODELO` en `chatbot.js`.

---

## Entregables de este taller

Agrega a tu carpeta de entrega:

```
mi-entrega/
├── chatbot-pruebas/
│   ├── chatbot.js              El script del chatbot (versión v2 con 15 reglas)
│   └── package.json
├── 02-tu-trabajo/
│   └── taller-ollama-chatbot-v2.md   Esta versión expandida
├── prompts/
│   └── 07-system-prompt-chatbot.md   El system prompt que usaste (con tus ajustes)
└── bitacora.md                 Con la sección "Chatbot Ollama — Registro" completada
```

---

## Apéndice — Tabla de auditoría (v1 → v2)

### Reglas de negocio

| Regla en chatbot v1 | Estado | Acción en v2 |
|---------------------|--------|--------------|
| RN1 pregrado max 3 | ✅ ya estaba | Sin cambios |
| RN2 posgrado max 5 | ✅ ya estaba | Sin cambios |
| RN3 vencido bloquea | ✅ ya estaba | Sin cambios |
| RN4 multa bloquea | ✅ ya estaba | Sin cambios |
| RN5 ejemplar no disponible | ✅ ya estaba | Sin cambios |
| RN6 plazo 15/3 días | ✅ ya estaba | Sin cambios |
| RN7 renovación con lista espera | ✅ ya estaba | Renombrada RN9 en v2 (expandida) |
| RN8 multa 2000/día | ✅ ya estaba | Sin cambios |
| RN7 proceso devolución | ❌ faltaba | **Añadida** (de spec RN6) |
| RN9 condiciones renovación | ❌ faltaba | **Añadida** (de spec RN8, condiciones completas) |
| RN10 alta demanda no renovable | ❌ faltaba | **Añadida** (regla lógica propuesta) |
| RN11 vencido dinámico | ❌ faltaba | **Añadida** (de spec RN9) |
| RN12 historial completo | ❌ faltaba | **Añadida** (de spec RN10) |
| RN13 reservas | ❌ faltaba | **Añadida** (de spec D5 + entidad SolicitudReserva) |
| RN14 FIFO reservas | ❌ faltaba | **Añadida** (regla lógica propuesta) |
| RN15 cancelar reserva | ❌ faltaba | **Añadida** (regla lógica propuesta) |

**Total reglas nuevas añadidas: 7** (RN7 devolución, RN9 renovación completa, RN10, RN11, RN12, RN13, RN14/RN15 se cuentan como 2 sobre reservas).

### Endpoints

| Endpoint | En chatbot v1 | En Version_2 real | Acción en v2 |
|----------|---------------|--------------------|--------------|
| GET /api/libros | ✅ | ✅ (+ filtros ?sala, ?alta_demanda, ?disponible) | Actualizado con filtros |
| POST /api/libros | ✅ | ✅ | Sin cambios |
| POST /api/libros/:id/ejemplares | ✅ | ✅ | Sin cambios |
| GET /api/libros/:id | ❌ faltaba | ✅ | **Añadido** |
| GET /api/estudiantes | ✅ en v1 | ❌ no existe | **Eliminado** (no implementado) |
| POST /api/estudiantes | ✅ | ✅ | Sin cambios |
| GET /api/estudiantes/:id | ❌ faltaba | ✅ | **Añadido** |
| GET /api/estudiantes/:id/historial | ✅ | ✅ | Sin cambios |
| POST /api/prestamos | ✅ | ✅ | Sin cambios |
| GET /api/prestamos | ✅ en v1 | ❌ no existe | **Eliminado** (no implementado) |
| GET /api/prestamos/vencidos | ❌ faltaba | ✅ | **Añadido** |
| GET /api/prestamos/:id | ❌ faltaba | ✅ | **Añadido** |
| PUT /api/prestamos/:id/devolucion | ✅ | ✅ | Sin cambios |
| PUT /api/prestamos/:id/renovar | ✅ | ✅ | Sin cambios |
| POST /api/reservas | ❌ faltaba | ✅ | **Añadido** |
| DELETE /api/reservas/:id | ❌ faltaba | ✅ | **Añadido** |
| POST /multas/:id/pago | — | ❌ no implementado | Documentado como brecha |
