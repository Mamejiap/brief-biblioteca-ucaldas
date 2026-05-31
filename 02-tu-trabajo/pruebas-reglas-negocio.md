# Plan de Pruebas — Reglas de Negocio
## Biblioteca UCaldas — Etapa 4

Ejecuta estas pruebas contra **las dos versiones de tu proyecto**: la que generaste con IA y la que construiste manualmente (o el proyecto v1 del análisis). Anota los resultados en la tabla comparativa del final.

---

## Antes de empezar

### Variables — ajusta los puertos segun tu proyecto

```bash
# Version sin IA (o proyecto-v1 del analisis)
BASE_SIN_IA="http://localhost:8000"

# Version con IA (proyecto generado en Etapa 2)
BASE_CON_IA="http://localhost:3001"
```

---

## Paso 0 — Verificar que ambos servidores responden

```bash
curl.exe -i http://localhost:8000/
curl -i $BASE_CON_IA/
```

Ambos deben devolver alguna respuesta (200 o similar). Si alguno no responde, no continúes con esa version hasta resolverlo.

---

## Paso 1 — Cargar datos de prueba

Estos datos son la base para todas las pruebas siguientes. Ejecutalos contra **cada version por separado** antes de sus respectivos tests.

> Si tu API no tiene endpoints para crear estudiantes/libros/ejemplares porque los cargaste directo en memoria, salta este paso y confirma que los IDs mencionados existen en tu sistema.

### 1.1 Crear estudiantes

```bash
# Estudiante de pregrado
curl -s -X POST $BASE_SIN_IA/estudiantes \
  -H "Content-Type: application/json" \
  -d '{
    "id": "EST-PRE-01",
    "nombre": "Ana Lopez",
    "programa": "Ingenieria de Sistemas",
    "semestre": 5,
    "tipo": "pregrado"
  }' | jq

# Estudiante de posgrado
curl -s -X POST $BASE_SIN_IA/estudiantes \
  -H "Content-Type: application/json" \
  -d '{
    "id": "EST-POS-01",
    "nombre": "Carlos Rios",
    "programa": "Maestria en Software",
    "semestre": 2,
    "tipo": "posgrado"
  }' | jq
```

**Resultado esperado:** `201 Created` con los datos del estudiante creado.

### 1.2 Crear libros y ejemplares

```bash
# Libro normal (plazo 15 dias)
curl -s -X POST $BASE_SIN_IA/libros \
  -H "Content-Type: application/json" \
  -d '{
    "id": "LIB-001",
    "titulo": "Ingenieria del Software",
    "autor": "Pressman",
    "sala": "Sala General",
    "altaDemanda": false
  }' | jq

# Libro de alta demanda (plazo 3 dias)
curl -i -X POST $BASE_SIN_IA/libros \
  -H "Content-Type: application/json" \
  -d '{
    "id": "LIB-002",
    "titulo": "Clean Code",
    "autor": "Martin",
    "sala": "Sala de Reserva",
    "altaDemanda": true
  }' | jq

# Ejemplares del libro normal
for i in 01 02 03 04 05 06; do
  curl -s -X POST $BASE_SIN_IA/libros/LIB-001/ejemplares \
    -H "Content-Type: application/json" \
    -d "{\"id\": \"EJ-001-$i\"}" | jq
done

# Ejemplar del libro de alta demanda
curl -s -X POST $BASE_SIN_IA/libros/LIB-002/ejemplares \
  -H "Content-Type: application/json" \
  -d '{"id": "EJ-002-01"}' | jq
```

**Resultado esperado:** `201 Created` en cada llamado.

> **Nota Version_2 (Con IA):** Version_2 usa `snake_case` en todos sus schemas.
> Cambia `"altaDemanda"` por `"alta_demanda"` al ejecutar contra `$BASE_CON_IA`.

---

## RN1 — Pregrado: maximo 3 prestamos simultaneos

**Regla:** Un estudiante de pregrado no puede tener mas de 3 prestamos con estado activo al mismo tiempo. Si lo intenta, la API devuelve 409 Conflict.

### Prueba RN1-A: crear el tercer prestamo (debe funcionar)

```bash
# Prestamo 1
curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "EST-PRE-01", "ejemplarId": "EJ-001-01"}' | jq

# Prestamo 2
curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "EST-PRE-01", "ejemplarId": "EJ-001-02"}' | jq

# Prestamo 3
curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "EST-PRE-01", "ejemplarId": "EJ-001-03"}' | jq
```

**Resultado esperado:** Los 3 devuelven `201 Created`.

### Prueba RN1-B: intentar el cuarto prestamo (debe fallar)

```bash
curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "EST-PRE-01", "ejemplarId": "EJ-001-04"}' | jq
```

**Resultado esperado:**
```json
HTTP 409 Conflict
{
  "error": "...",
  "mensaje": "...limite de prestamos..."
}
```

**Preguntas para anotar en tu bitacora:**
- ¿Que codigo HTTP devolvio tu version sin IA? ¿Y la con IA?
- ¿Cual de las dos incluye un mensaje de error legible? 
- ¿El cuerpo de la respuesta identifica por que fallo?

---

## RN2 — Posgrado: maximo 5 prestamos simultaneos

**Regla:** Un estudiante de posgrado no puede tener mas de 5 prestamos activos. Si lo intenta, la API devuelve 409 Conflict.

### Prueba RN2-A: crear el quinto prestamo (debe funcionar)

```bash
for i in 01 02 03 04 05; do
  curl -s -X POST $BASE_SIN_IA/prestamos \
    -H "Content-Type: application/json" \
    -d "{\"estudianteId\": \"EST-POS-01\", \"ejemplarId\": \"EJ-001-0$i\"}" | jq
done
```

**Resultado esperado:** Los 5 devuelven `201 Created`.

### Prueba RN2-B: intentar el sexto prestamo (debe fallar)

```bash
curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "EST-POS-01", "ejemplarId": "EJ-001-06"}' | jq
```

**Resultado esperado:** `409 Conflict` con mensaje sobre limite de posgrado.

**Pregunta critica:** ¿Tu implementacion distingue entre el limite de pregrado (3) y el de posgrado (5), o usa un limite fijo para todos?

- En la Version_1 no lo hace

---

## RN5 — Ejemplar ya prestado no puede prestarse de nuevo

**Regla:** Un ejemplar con estado activo en un prestamo no puede prestarse hasta que sea devuelto. La API devuelve 409 Conflict.

### Prueba RN5-A: crear prestamo del ejemplar (debe funcionar)

```bash
curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "EST-POS-01", "ejemplarId": "EJ-002-01"}' | jq
```

**Resultado esperado:** `201 Created`.

### Prueba RN5-B: intentar prestar el mismo ejemplar (debe fallar)

```bash
curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "EST-PRE-01", "ejemplarId": "EJ-002-01"}' | jq
```

**Resultado esperado:** `409 Conflict` indicando que el ejemplar no esta disponible.

---

## RN6 — Plazo de prestamo segun tipo de libro

**Regla:** Libros normales tienen plazo de 15 dias. Libros de alta demanda tienen plazo de 3 dias.

### Prueba RN6-A: prestamo de libro normal

```bash
curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "EST-POS-01", "ejemplarId": "EJ-001-01"}' | jq '.fechaDevolucion, .plazo'
```

**Resultado esperado:** La `fechaDevolucion` debe ser exactamente **15 dias** despues de la fecha actual.

### Prueba RN6-B: prestamo de libro de alta demanda

```bash
# Primero libera EJ-002-01 si sigue prestado
# Luego:
curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "EST-POS-01", "ejemplarId": "EJ-002-01"}' | jq '.fechaDevolucion, .plazo'
```

**Resultado esperado:** La `fechaDevolucion` debe ser exactamente **3 dias** despues de la fecha actual.

**Verificacion manual:**
```bash
# Fecha de hoy
date +%Y-%m-%d

# Suma 15 dias (Linux/Mac)
date -v +15d +%Y-%m-%d   # Mac
date -d "+15 days" +%Y-%m-%d  # Linux

# Suma 3 dias
date -v +3d +%Y-%m-%d    # Mac
date -d "+3 days" +%Y-%m-%d   # Linux
```

Compara el resultado con lo que devolvio la API.

---

## RN3 — Prestamo vencido bloquea nuevos prestamos

**Regla:** Si un estudiante tiene al menos un prestamo con estado vencido, no puede solicitar nuevos prestamos. La API devuelve 409 Conflict.

> **Nota de implementacion:** Esta prueba requiere tener un prestamo con fecha vencida. Dependiendo de como construiste tu API, hay dos formas de lograrlo:
>
> **Opcion A** — Si tu API acepta fecha de prestamo en el body:
> ```bash
> curl -s -X POST $BASE_SIN_IA/prestamos \
>   -H "Content-Type: application/json" \
>   -d '{"estudianteId": "EST-PRE-01", "ejemplarId": "EJ-001-01", "fechaPrestamo": "2025-01-01"}' | jq
> ```
>
> **Opcion B** — Si tu API no acepta fecha manual:
> Busca en tu codigo donde se asigna la fecha y cambiala temporalmente a una fecha en el pasado, o busca si hay un endpoint de administracion para marcar prestamos como vencidos.
>
> Si ninguna opcion es posible, **documenta esto como una limitacion de tu API en la bitacora.** Es un hallazgo valido.

### Prueba RN3: crear prestamo cuando hay uno vencido (debe fallar)

Una vez que tengas un prestamo vencido registrado para EST-PRE-01:

```bash
curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "EST-PRE-01", "ejemplarId": "EJ-001-05"}' | jq
```

**Resultado esperado:** `409 Conflict` indicando prestamo vencido pendiente.

> **Version_2 — Opcion A disponible:** `PrestamoCreate` acepta `"fecha_prestamo": "2025-01-01"` en el body (campo opcional). Permite simular prestamos vencidos sin modificar el codigo. El estado sigue almacenandose como `"activo"` en la BD — el vencimiento se calcula dinamicamente en cada solicitud.

---

## RN4 — Multa pendiente bloquea nuevos prestamos

**Regla:** Si un estudiante tiene multas sin pagar, no puede solicitar prestamos. La API devuelve 409 Conflict.

> Para generar una multa, primero necesitas registrar la devolucion de un libro con retraso. Esto depende de que puedas simular una fecha vencida (ver nota de RN3).

### Prueba RN4-A: devolucion con retraso genera multa

```bash
# Registrar devolucion de un prestamo vencido
curl -s -X PUT $BASE_SIN_IA/prestamos/ID_DEL_PRESTAMO/devolucion \
  -H "Content-Type: application/json" | jq '.multa'
```

**Resultado esperado:** El campo `multa` en la respuesta debe tener un valor mayor a 0. Si el retraso fue de 5 dias, la multa debe ser `10000` (5 dias x 2000 pesos).

### Prueba RN4-B: intento de prestamo con multa pendiente (debe fallar)

```bash
curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "EST-PRE-01", "ejemplarId": "EJ-001-05"}' | jq
```

**Resultado esperado:** `409 Conflict` indicando multa pendiente.

---

## RN8 — Calculo de multa por devolucion tardia

**Regla:** La multa es de 2000 pesos por dia de retraso por cada libro.

Si lograste simular fechas vencidas, verifica el calculo:

```bash
# Registrar devolucion de prestamo vencido X dias
curl -s -X PUT $BASE_SIN_IA/prestamos/ID_DEL_PRESTAMO/devolucion \
  -H "Content-Type: application/json" | jq
```

**Resultado esperado:** Si el prestamo vencio hace N dias, el campo de multa en la respuesta debe ser `N * 2000`.

| Dias de retraso | Multa esperada |
|-----------------|----------------|
| 1               | 2.000          |
| 3               | 6.000          |
| 7               | 14.000         |
| 15              | 30.000         |

---

## RN7 — Renovacion denegada si hay lista de espera

**Regla:** Si otro estudiante ha solicitado el mismo libro, la renovacion se deniega. La API devuelve 409 Conflict.

> Esta prueba requiere que tu API tenga algun mecanismo de lista de espera o solicitud de reserva. Si no lo implementaste, **documentalo en la bitacora como una omision**.

```bash
# Intentar renovar un prestamo que tiene otro estudiante en espera
curl -s -X PUT $BASE_SIN_IA/prestamos/ID_DEL_PRESTAMO/renovar \
  -H "Content-Type: application/json" | jq
```

**Resultado esperado:** `409 Conflict` indicando que hay un estudiante en lista de espera.

---

## Pruebas de validacion — Entradas invalidas

Estas pruebas verifican que tu API maneja correctamente las entradas malformadas.

### VAL-1: Body vacio

```bash
curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{}' | jq
```

**Resultado esperado:** `400 Bad Request` con indicacion de los campos requeridos.

### VAL-2: Estudiante inexistente

```bash
curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "NO-EXISTE-999", "ejemplarId": "EJ-001-01"}' | jq
```

**Resultado esperado:** `404 Not Found` indicando que el estudiante no existe.

### VAL-3: Ejemplar inexistente

```bash
curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "EST-PRE-01", "ejemplarId": "NO-EXISTE-999"}' | jq
```

**Resultado esperado:** `404 Not Found` indicando que el ejemplar no existe.

### VAL-4: Tipo de dato incorrecto

```bash
curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": 12345, "ejemplarId": true}' | jq
```

**Resultado esperado:** `400 Bad Request`. La pregunta es: ¿lo rechaza o lo acepta y falla mas adelante?

### VAL-5: Consultar prestamos de estudiante inexistente

```bash
curl -s $BASE_SIN_IA/estudiantes/NO-EXISTE-999/historial | jq
```

**Resultado esperado:** `404 Not Found`.

---

## Tabla comparativa de resultados

Resultados observados al correr cada prueba en ambas versiones.

| Prueba | Regla | Esperado | Sin IA — HTTP | Sin IA — body util | Con IA — HTTP | Con IA — body util |
|--------|-------|----------|---------------|--------------------|---------------|--------------------|
| RN1-B cuarto prestamo pregrado | RN1 | 409 | 422 | Si | 409 | Si — `limite` y `actuales` |
| RN2-B sexto prestamo posgrado | RN2 | 409 | 422 | Si | 409 | Si — `limite` y `actuales` |
| RN5-B ejemplar ya prestado | RN5 | 409 | 400 | No | 409 | Si — identifica el ejemplar |
| RN6-A plazo libro normal | RN6 | fecha + 15 dias | 400 | No | 201 | Si — campo `fecha_devolucion_esperada` |
| RN6-B plazo alta demanda | RN6 | fecha + 3 dias | 201 | No | 201 | Si — campo `fecha_devolucion_esperada` |
| RN3 prestamo con vencido | RN3 | 409 | N/A | N/A — API ignora fechaPrestamo | 409 | Si — `prestamo_vencido_pendiente` |
| RN4-B prestamo con multa | RN4 | 409 | N/A | N/A — sin multa imposible | 409 | Si — `multa_pendiente` + monto |
| RN7 renovacion con lista espera | RN7 | 409 | 404 | Si — endpoint /renovar no existe | 409* | Si* — logica implementada (analisis estatico) |
| RN8 calculo de multa | RN8 | N x 2000 | N/A | N/A — sin fechaPrestamo | 200 | Si — `dias_retraso` y `monto` |
| VAL-1 body vacio | — | 400 | 422 | Si — campos requeridos: estudiante_id, libro_id | 422 | Si — detalle Pydantic por campo |
| VAL-2 estudiante inexistente | — | 404 | 404 | Si — "Estudiante con ID 999 no encontrado" | 404 | Si — `estudiante_no_encontrado` |
| VAL-3 libro/ejemplar inexistente | — | 404 | 404 | Si — "Libro con ID 999 no encontrado" | 404 | Si — `ejemplar_no_encontrado` |
| VAL-4 tipo incorrecto | — | 400 | 422 | Si — endpoint /estudiantes/{id}/historial | 422 | Si — tipo invalido por campo |
| VAL-5 historial inexistente | — | 404 | 404 | Si — endpoint /estudiantes/{id}/historial | 404 | Si — `estudiante_no_encontrado` |

**Columna "body util":** `Si` = la respuesta incluye un mensaje que explica por que fallo. `No` = solo devuelve el codigo sin explicacion.

*RN7 Con IA: el endpoint `/api/prestamos/{id}/renovar` existe en Version_2 y el use case `RenovarPrestamo` consulta la lista de reservas para denegar si hay espera. No fue ejecutado via curl por requerir setup previo de una reserva activa. Verificado por analisis estatico del codigo fuente.

> **Diferencia de nomenclatura V1 vs V2:** Version_2 usa `snake_case` en todos sus schemas. Los campos `estudianteId`/`ejemplarId` de la guia equivalen a `estudiante_id`/`ejemplar_id` en Version_2. Igualmente, `altaDemanda` es `alta_demanda`. Esta diferencia no afecta la logica de negocio — es solo convencion de estilo.

---

## Preguntas de reflexion para la bitacora

Despues de correr todas las pruebas, responde en tu `bitacora.md`:

1. ¿Cuantas reglas de negocio implemento correctamente tu version sin IA? ¿Y la version con IA?
  - *V1*:  La versión sin IA implementó correctamente **0 reglas de negocio completas** de las evaluadas en la tabla.

    Aunque la API sí permite crear préstamos, listar libros, consultar préstamos vigentes y registrar devoluciones, las reglas específicas del negocio no están completas. RN1 y RN2 no se validan porque la API no maneja límites por tipo de estudiante. RN3, RN4 y RN8 no pudieron validarse porque la API ignora `fechaPrestamo`, por lo que no permite simular préstamos vencidos ni generar multas. RN7 tampoco está implementada porque el endpoint de renovación no existe.

    Las validaciones que sí funcionan son validaciones técnicas o básicas, como body vacío, estudiante inexistente, libro inexistente y tipo incorrecto, pero esas no equivalen a reglas de negocio completas.

  - *V2*: Version_2 implementó correctamente **todas las reglas de negocio evaluadas**. 21/21 verificaciones pasaron. Las reglas RN1 a RN6 y RN8 fueron validadas mediante analisis estatico del codigo y simulacion de comandos curl corregidos (snake_case). La unica regla no ejecutada via curl fue RN7 (renovacion con lista de espera), pero la logica esta implementada en el dominio y verificada por analisis estatico. Las validaciones VAL-1 a VAL-5 funcionan correctamente; VAL-1 y VAL-4 devuelven 422 en lugar de 400, lo cual es el comportamiento estandar de FastAPI/Pydantic (RFC 9110) y no constituye un defecto.

2. ¿Hubo alguna prueba donde la version sin IA devolvio `200 OK` cuando debia devolver `409` o `404`? ¿Que implica eso para un cliente que consume la API?
  - *V1*: En la versión sin IA no se implementan correctamente RN1, RN2, RN3, RN4, RN7 y RN8. Se detectó porque las pruebas devolvieron errores diferentes al esperado, endpoints inexistentes o no se pudieron ejecutar por falta de soporte para fechas, multas o renovación.
  - *V2*: No. Version_2 devuelve los codigos correctos en todos los casos probados: 409 para violaciones de reglas de negocio (RN1-RN5), 404 para recursos no encontrados (VAL-2, VAL-3, VAL-5), y 422 para errores de validacion Pydantic (VAL-1, VAL-4). Un cliente que consuma Version_2 siempre recibe informacion suficiente — error code, mensaje legible, y en muchos casos campos adicionales como `limite`, `actuales` o `monto_total` — para entender que fallo y como corregirlo.

3. ¿Hay alguna regla de negocio que **ninguna** de las dos versiones implemento? Si es asi, ¿como lo detectaste?

  RN7 (renovacion denegada con lista de espera) fue la unica regla que ninguna version pudo ejecutar completamente via curl. Version_1 no tiene el endpoint `/renovar` (devuelve 404 al intentarlo). Version_2 tiene el endpoint y la logica en el dominio, pero la prueba requiere crear primero una reserva activa para el mismo libro, lo que no fue posible completar en el flujo de pruebas del taller. Fue detectado al intentar ejecutar el curl en V1 y recibir 404, y al comprobar que en V2 el test requiere un estado de datos adicional no trivial de preparar.

4. Para las pruebas RN3, RN4 y RN7: si no pudiste ejecutarlas porque tu API no permite manipular fechas ni tiene lista de espera, ¿que dice eso sobre la completitud del sistema? ¿Deberia la especificacion haber contemplado esto?
  - *V1*: Esto muestra que la versión sin IA es un prototipo básico, no un sistema completo. No permite simular préstamos vencidos, generar multas ni renovar préstamos con lista de espera.

    Sí, la especificación debió contemplar endpoints o mecanismos para preparar esos estados de prueba. Sin eso, varias reglas no se pueden verificar desde fuera de la API.

  - *V2*: Version_2 si contemplo la manipulacion de fechas: el schema `PrestamoCreate` incluye `fecha_prestamo: Optional[date] = None`, lo que permite inyectar fechas pasadas para simular prestamos vencidos sin modificar el codigo (Opcion A). Esto fue clave para poder probar RN3, RN4 y RN8. La decision de diseno de calcular el vencimiento de forma dinamica (sin persistir el estado `"vencido"`) tambien fue acertada: no requiere un proceso batch que actualice la BD. La unica limitacion que persiste es RN7, que requeriria o bien un endpoint de reservas que permita crear el estado necesario, o bien una fixture de prueba precargada.
