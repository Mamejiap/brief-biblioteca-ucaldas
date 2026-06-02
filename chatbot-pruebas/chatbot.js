const readline = require("readline");
const { execSync } = require("child_process");

const BASE_URL = "http://127.0.0.1:8000";
const OLLAMA_URL = "http://127.0.0.1:11434/api/chat";
const MODELO = "llama3.2:3b ";

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
  let comandosEjecutados = false;

  for (let i = 0; i < lineas.length; i++) {
    let lineaActual = lineas[i].trim();

    if (lineaActual.startsWith("EJECUTAR:")) {
      let comando = lineaActual.replace("EJECUTAR:", "").trim();

      // ROBUSTEZ: Si el chatbot dejó el comando en la línea de abajo, lo rescatamos
      if (comando === "" && i + 1 < lineas.length) {
        comando = lineas[i + 1].trim();
        i++; // Saltamos la siguiente línea ya que la procesamos aquí
      }

      // Si después de la limpieza hay un comando válido, lo ejecutamos
      if (comando.startsWith("curl")) {
        comandosEjecutados = true;
        console.log(`\n[EJECUTANDO]: ${comando}\n`);
        try {
          // Ejecutamos el comando de forma síncsa
          const resultado = execSync(comando, { encoding: "utf-8", timeout: 10000 });
          console.log("[RESULTADO]:\n" + resultado);
        } catch (err) {
          console.log("[RESULTADO]:\n" + (err.stdout || err.message));
        }
        // NOTA DE QA: Eliminamos el "return true" de aquí para que NO se detenga en el primero
      }
    }
  }
  return comandosEjecutados;
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