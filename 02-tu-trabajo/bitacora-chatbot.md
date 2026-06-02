## Chatbot Ollama — Registro

### Modelo usado
- Nombre: llama3.2:3b
- RAM consumida aproximada: 2.5 GB y 100% CPU

## Pruebas guiadas con el chatbot

### Sesión 1 — Datos de prueba

```
Tú: crea los datos de prueba base para todas las reglas: un estudiante pregrado EST-PRE-01, uno posgrado EST-POS-01, un libro normal LIB-001 con 6 ejemplares y un libro de alta demanda LIB-002 con 1 ejemplar
```
Respuesta del chatbot
```
Chatbot: A continuación, te proporciono los datos de prueba base para todas las reglas:

**Estudiantes**

* **EST-PRE-01 (estudiante pregrado)**
        + `id`: `PREG-001`
        + `nombre`: `"Juan Pérez"`
        + `programa`: `"Ingeniería en Sistemas"`
        + `semestre`: `"2023-2"`
        + `tipo`: `"pregrado"`
* **EST-POS-01 (estudiante posgrado)**
        + `id`: `PSEG-001`
        + `nombre`: `"María García"`
        + `programa`: `"Maestría en Ciencia de Datos"`
        + `semestre`: `"2023-2"`
        + `tipo`: `"posgrado"`

**Libros**

* **LIB-001 (libro normal)**
        + `id`: `LIB-001`
        + `titulo`: `"Algebra Lineal"`
        + `autor`: `"John Smith"`
        + `sala`: `"Sala A"`
        + `alta_demanda`: `false`
        + `disponible`: `true`
* **LIB-002 (libro de alta demanda)**
        + `id`: `LIB-002`
        + `titulo`: `"Inteligencia Artificial"`
        + `autor`: `"Jane Doe"`
        + `sala`: `"Sala B"`
        + `alta_demanda`: `true`
        + `disponible`: `false`

**Ejemplares**

* **EJEMP-001 (ejemplo de libro normal)**
        + `id`: `EJEMP-001`
        + `libro_id`: `LIB-001`
        + `disponible`: `true`
* **EJEMP-002 (ejemplo de libro de alta demanda)**
        + `id`: `EJEMP-002`
        + `libro_id`: `LIB-002`
        + `disponible`: `false`

**Préstamos**

* Crea un préstamo para el estudiante pregrado EST-PRE-01:
        + `id`: `PREST-001`
        + `estudiante_id`: `PREG-001`
        + `ejemplar_id`: `EJEMP-001`
        + `fecha_prestamo`: `"2023-03-15"`
* Crea un préstamo para el estudiante posgrado EST-POS-01:
        + `id`: `PREST-002`
        + `estudiante_id`: `PSEG-001`
        + `ejemplar_id`: `EJEMP-001`
        + `fecha_prestamo`: `"2023-03-15"`

**Reservas**

* Crea una reserva para el estudiante pregrado EST-PRE-01 por el libro LIB-001:
        + `id`: `RES-001`
        + `estudiante_id`: `PREG-001`
        + `libro_id`: `LIB-001`
* Crea una reserva para el estudiante posgrado EST-POS-01 por el libro LIB-002:
        + `id`: `RES-002`
        + `estudiante_id`: `PSEG-001`
        + `libro_id`: `LIB-002`

**Préstamos vencidos**

* No hay préstamos vencidos en este punto.

Para generar los datos de prueba, puedes utilizar las siguientes comandos `curl`:

```bash
# Estudiantes
echo -e "PREG-001,juan,perez,ingenieria en sistemas,2023-2,pregrado" | curl -X POST http://127.0.0.1:8000/api/estudiantes

echo -e "PSEG-001,maria,garcia,maestria en ciencia de datos,2023-2,posgrado" | curl -X POST http://127.0.0.1:8000/api/estudiantes

# Libros
echo -e "LIB-001,algebra lineal,john smith,Sala A,false,true" | curl -X POST http://127.0.0.1:8000/api/libros

echo -e "LIB-002,inteligencia artificial,jane doe,Sala B,true,false" | curl -X POST http://127.0.0.1:8000/api/libros

# Ejemplares
curl -X POST http://127.0.0.1:8000/api/libros/LIB-001/ejemplares/EJEMP-001

curl -X POST http://127.0.0.1:8000/api/libros/LIB-002/ejemplares/EJEMP-002

# Préstamos
curl -X POST -H "Content-Type: application/json" --data '{"estudiante_id": "PREG-001", "ejemplar_id": "EJEMP-001", "fecha_prestamo": "2023-03-15"}' http://127.0.0.1:8000/api/prestamos

curl -X POST -H "Content-Type: application/json" --data '{"estudiante_id": "PSEG-001", "ejemplar_id": "EJEMP-001", "fecha_prestamo": "2023-03-15"}' http://127.0.0.1:8000/api/prestamos

# Reservas
curl -X POST -H "Content-Type: application/json" --data '{"estudiante_id": "PREG-001", "libro_id": "LIB-001"}' http://127.0.0.1:8000/api/reservas

curl -X POST -H "Content-Type: application/json" --data '{"estudiante_id": "PSEG-001", "libro_id": "LIB-002"}' http://127.0.0.1:8000/api/reservas
```

Luego, puedes ejecutar los comandos de prueba utilizando `EJECUTAR:`:

```bash
# Verifique que los datos estén creados correctamente
curl -X GET http://127.0.0.1:8000/api/estudiantes/PREG-001

curl -X GET http://127.0.0.1:8000/api/libros/LIB-001

curl -X GET http://127.0.0.1:8000/api/reservas

```

### Sesión 2 — RN1 y RN2

```
Tú: genera la prueba RN1 completa: crear los 3 préstamos válidos para pregrado y luego intentar el cuarto

Tú: ahora haz lo mismo para RN2 con el estudiante de posgrado, recuerda que su límite es 5
```

Respuesta de chatbot 
#### RN1
```
Chatbot: A continuación, te proporciono la prueba RN1 completa:

**Crear los 3 préstamos válidos para pregrado**

```bash
# Estudiante pregrado EST-PRE-01
curl -X POST http://127.0.0.1:8000/api/estudiantes/PREG-001

# Libro normal LIB-001 con 6 ejemplares
curl -X GET http://127.0.0.1:8000/api/libros/LIB-001

# Préstamo 1 para EST-PRE-01 (3 préstamos activos simultáneamente)
curl -X POST -H "Content-Type: application/json" --data '{"estudiante_id": "PREG-001", "ejemplar_id": "EJEMP-001", "fecha_prestamo": "2023-03-15"}' http://127.0.0.1:8000/api/prestamos

# Préstamo 2 para EST-PRE-01
curl -X POST -H "Content-Type: application/json" --data '{"estudiante_id": "PREG-001", "ejemplar_id": "EJEMP-002", "fecha_prestamo": "2023-03-16"}' http://127.0.0.1:8000/api/prestamos

# Préstamo 3 para EST-PRE-01
curl -X POST -H "Content-Type: application/json" --data '{"estudiante_id": "PREG-001", "ejemplar_id": "EJEMP-003", "fecha_prestamo": "2023-03-17"}' http://127.0.0.1:8000/api/prestamos
```

**Intentar el cuarto préstamo**

```bash
# Intentar crear un cuarto préstamo para EST-PRE-01 (limite alcanzada)
curl -X POST -H "Content-Type: application/json" --data '{"estudiante_id": "PREG-001", "ejemplar_id": "EJEMP-004", "fecha_prestamo": "2023-03-18"}' http://127.0.0.1:8000/api/prestamos

# Verificar la respuesta
curl -X GET http://127.0.0.1:8000/api/prestamos/PREST-001
```

La respuesta esperada es un código de estado 409 Conflict con el mensaje:

```json
{
    "error": "limite_prestamos_alcanzado",
    "limite": 3,
    "actuales": 4
}
```

Esto indica que el estudiante pregrado EST-PRE-01 ha alcanzado su límite de préstamos activos, es decir, 3

#### RN2
```

```

### Sesión 3 — RN5 y RN6

```
Tú: prueba que un ejemplar ya prestado no se puede prestar de nuevo (RN5)

Tú: muéstrame cómo verificar que el plazo del préstamo es correcto para un libro normal versus uno de alta demanda (RN6)
```

Respuesta del chatbot
#### RN5  
```
Chatbot: EJECUTAR: curl -X POST -H "Content-Type: application/json" -d "{\"estudiante_id\":\"EST-POS-01\",\"ejemplar_id\":\"EJ-001-03\"}" http://127.0.0.1:8000/api/prestamos


[EJECUTANDO]: curl -X POST -H "Content-Type: application/json" -d "{\"estudiante_id\":\"EST-POS-01\",\"ejemplar_id\":\"EJ-001-03\"}" http://127.0.0.1:8000/api/prestamos

  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
  0      0   0      0   0      0      0      0                              100    159 100    103 100     56   3198   1738                              100    159 100    103 100     56   3192   1735                              100    159 100    103 100     56   3187   1733                              0
[RESULTADO]:
{"error":"ejemplar_no_disponible","mensaje":"Ejemplar 'EJ-001-03' no está disponible para préstamo."}

```
#### RN6
```
Chatbot: EJECUTAR: curl -X GET http://127.0.0.1:8000/api/libros/1
EJECUTAR: curl -X POST -H "Content-Type: application/json" -d "{\"estudiante_id\":\"EST-POS-01\",\"ejemplar_id\":1,\"fecha_prestamo\":\"2022-01-01\"}" http://127.0.0.1:8000/api/prestamos


[EJECUTANDO]: curl -X GET http://127.0.0.1:8000/api/libros/1

  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
  0      0   0      0   0      0      0      0                              100     68 100     68   0      0   2791      0                              100     68 100     68   0      0   2780      0                              100     68 100     68   0      0   2770      0                              0
[RESULTADO]:
{"error":"libro_no_encontrado","mensaje":"Libro '1' no encontrado."}

[EJECUTANDO]: curl -X POST -H "Content-Type: application/json" -d "{\"estudiante_id\":\"EST-POS-01\",\"ejemplar_id\":1,\"fecha_prestamo\":\"2022-01-01\"}" http://127.0.0.1:8000/api/prestamos

  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
  0      0   0      0   0      0      0      0                              100    189 100    113 100     76  20937  14081                              100    189 100    113 100     76  20703  13924                              100    189 100    113 100     76  20511  13795                              0
[RESULTADO]:
{"detail":[{"type":"string_type","loc":["body","ejemplar_id"],"msg":"Input should be a valid string","input":1}]}

```
### Sesión 4 — Validaciones

```
Tú: genera pruebas de entradas inválidas: body vacío, estudiante inexistente y ejemplar inexistente

Tú: el resultado del body vacío fue { "error": "..." } con código 400. ¿Eso es correcto según la especificación?
```
Respuesta del chatbot

```
Tú: genera pruebas de entradas inválidas: body vacío, estudiante inexistente y ejemplar inexistente

Chatbot: EJECUTAR: curl -X POST -H "Content-Type: application/json" -d "{}" http://127.0.0.1:8000/api/prestamos
EJECUTAR: curl -X POST -H "Content-Type: application/json" -d "{\"estudiante_id\":\"EST-NO-EXISTE\"}" http://127.0.0.1:8000/api/prestamos
EJECUTAR: curl -X POST -H "Content-Type: application/json" -d "{\"ejemplar_id\":\"EJ-NO-EXISTE\"}" http://127.0.0.1:8000/api/prestamos


[EJECUTANDO]: curl -X POST -H "Content-Type: application/json" -d "{}" http://127.0.0.1:8000/api/prestamos

  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
100    180 100    178 100      2   4721     53                              0
[RESULTADO]:
{"detail":[{"type":"missing","loc":["body","estudiante_id"],"msg":"Field required","input":{}},{"type":"missing","loc":["body","ejemplar_id"],"msg":"Field required","input":{}}]}

[EJECUTANDO]: curl -X POST -H "Content-Type: application/json" -d "{\"estudiante_id\":\"EST-NO-EXISTE\"}" http://127.0.0.1:8000/api/prestamos

  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
100    158 100    125 100     33  17687   4669                              0
[RESULTADO]:
{"detail":[{"type":"missing","loc":["body","ejemplar_id"],"msg":"Field required","input":{"estudiante_id":"EST-NO-EXISTE"}}]}

[EJECUTANDO]: curl -X POST -H "Content-Type: application/json" -d "{\"ejemplar_id\":\"EJ-NO-EXISTE\"}" http://127.0.0.1:8000/api/prestamos

  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
100    154 100    124 100     30  11079   2680                              0
[RESULTADO]:
{"detail":[{"type":"missing","loc":["body","estudiante_id"],"msg":"Field required","input":{"ejemplar_id":"EJ-NO-EXISTE"}}]}
Tú: el resultado del body vacío fue { "error": "..." } con código 400. ¿Eso es correcto según la especificación?

Chatbot: EJECUTAR: curl -X POST -H "Content-Type: application/json" -d "{}" http://127.0.0.1:8000/api/prestamos
(Espera respuesta con código 400 y error "limite_prestamos_alcanzado")


[EJECUTANDO]: curl -X POST -H "Content-Type: application/json" -d "{}" http://127.0.0.1:8000/api/prestamos

  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
100    180 100    178 100      2  21337    239                              0
[RESULTADO]:
{"detail":[{"type":"missing","loc":["body","estudiante_id"],"msg":"Field required","input":{}},{"type":"missing","loc":["body","ejemplar_id"],"msg":"Field required","input":{}}]}
```

### Sesión 5 — Análisis de un fallo

Si alguna prueba devuelve un resultado inesperado, dile al chatbot:

```
Tú: el endpoint POST /api/prestamos devolvió 200 OK en lugar de 409 cuando el estudiante ya tiene 3 préstamos. El body fue: { "id": "P-004", ... }. ¿Qué regla está violando y en qué archivo debería buscar el problema?
```
Respuesta del chatbot
```
Tú: el endpoint POST /api/prestamos devolvió 200 OK en lugar de 409 cuando el estudiante ya tiene 3 préstamos. El body fue: { "id": "P-004", ... }. ¿Qué regla está violando y en qué archivo debería buscar el problema?

Chatbot: EJECUTAR: curl -X POST -H "Content-Type: application/json" -d "{\"id\":\"P-004\",\"estudiante_id\":\"EST-POS-01\",\"ejemplar_id\":1,\"fecha_prestamo\":\"2022-01-01\"}" http://127.0.0.1:8000/api/prestamos

(El problema debe estar en RN1, que establece que un estudiante no puede tener más de 3 préstamos activos simultáneamente)


[EJECUTANDO]: curl -X POST -H "Content-Type: application/json" -d "{\"id\":\"P-004\",\"estudiante_id\":\"EST-POS-01\",\"ejemplar_id\":1,\"fecha_prestamo\":\"2022-01-01\"}" http://127.0.0.1:8000/api/prestamos

  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
100    202 100    113 100     89  12427   9787                              0
[RESULTADO]:
{"detail":[{"type":"string_type","loc":["body","ejemplar_id"],"msg":"Input should be a valid string","input":1}]}
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

Respuesta del chatbot

```
Chatbot: En ese caso, la lógica de validación del límite de préstamos no está funcionando correctamente en Version_2.

La función `validate` de la clase `Prestamo` debería verificar no solo el número de préstamos activos del estudiante, sino también cualquier otro estado que pueda afectar su capacidad para pedir un nuevo préstamo (como tener una multa pendiente).

La corrección se puede lograr agregando más condiciones en la función `validate` para considerar los casos especiales como el estudiante de pregrado con 3 préstamos activos y problemas asociados.
```

#### Pregunta 6-B — Renovación de libro de alta demanda

```
Tú: tengo un préstamo activo del ejemplar EJ-002-01 (que pertenece a LIB-002, un libro de alta demanda) y no hay ninguna reserva pendiente sobre ese libro.
¿Puedo renovar ese préstamo? Dame el curl para intentarlo y explica qué respuesta esperas según las reglas de la biblioteca.
```

> *Propósito:* verificar que el chatbot conoce RN10 (alta demanda no se renueva) y no confunde con RN9 (lista de espera).

Respuesta del chatbot
```
Chatbot: No puedes renovar ese préstamo porque, según RN9 (Renovación), los libros de alta demanda no pueden ser renovados bajo ninguna circunstancia.

El curl para intentar renovar el préstamo sería:

curl -X PATCH -H "Content-Type: application/json" -d '{"id": "EJ-002-01"}' http://127.0.0.1:8000/api/prestamos/actualizar

Espero una respuesta con código 422 (Unprocessable Entity), ya que el sistema está intentando realizar una acción no permitida para un libro de alta demanda.   
```

#### Pregunta 6-C — Cálculo de multa con inyección de fecha

```
Tú: quiero probar RN8 sin esperar días reales. Sé que POST /api/prestamos acepta el campo opcional fecha_prestamo.
Dame el curl completo para: (1) crear un préstamo con fecha 20 días atrás sobre un libro normal, (2) devolver ese préstamo hoy. ¿Cuántos días de retraso habrá y cuál será el monto exacto de la multa?
```

> *Propósito:* verificar que el chatbot conoce la Opción A de inyección de fecha y calcula correctamente: plazo 15 días, prestado hace 20 → 5 días de retraso → $10.000.


Respuesta del chatbot.
```
Chatbot: Para probar RN8, necesitamos simular un préstamo con fecha de vencimiento en el pasado y luego devolverlo.

Aquí te dejo el curl completo para cada caso:

1. Crear un préstamo con fecha 20 días atrás sobre un libro normal:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"estudiante_id": "EST-PRE-01", "ejemplar_id": "EJ-001-06", "fecha_prestamo": "2023-03-05"}' \
  http://127.0.0.1:8000/api/prestamos
```
2. Devolver ese préstamo hoy:
```bash
curl -X PATCH -H "Content-Type: application/json" \
  -d '{"id": "EJ-001-06"}' \
  http://127.0.0.1:8000/api/prestamos/actualizar

Después de ejecutar estos curls, puedes verificar el mon
```
#### Pregunta 6-D — Reserva que bloquea renovación

```
Tú: EST-PRE-01 tiene un préstamo activo de EJ-001-01 (LIB-001, libro normal, no vencido).
EST-POS-01 quiere el mismo libro y hace una reserva. Ahora EST-PRE-01 intenta renovar.
Dame los tres curls en orden: crear la reserva, intentar la renovación y explicar por qué debe fallar.
```

> *Propósito:* verificar que el chatbot entiende la interacción entre RN9 y RN13 (reserva activa bloquea renovación).

Respuesta del chatbot.
```
Chatbot: Aquí te dejo los tres curls:

1. Crear la reserva:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": "EST-PRE-01", "libro_id": "LIB-001"}' \
  http://127.0.0.1:8000/api/reservas
```
2. Intentar renovar el préstamo:
```bash
curl -X PATCH -H "Content-Type: application/json" \
  -d '{"id": "EJ-001-01"}' \
  http://127.0.0.1:8000/api/prestamos/actualizar

3. (No necesitamos este curl, ya que la reserva previa debe interferir con la renovación)

La renovación debe fallar porque, según RN9 (Renovación), los libros no pueden ser renovados si hay una reserva pendiente sobre el mismo libro. En este caso, EST-PRE-01 intenta renovar un préstamo activo que ya tiene una reserva pendiente, lo que va en contra de las políticas de la biblioteca. La respuesta esperada es 409 (Conflict).

```

#### Pregunta 6-E — Desbloqueo después de pago de multa

```
Tú: EST-PRE-01 fue bloqueado por una multa de $4.000 (RN4). En nuestra base de datos (SQLite), ¿cómo marcaríamos esa multa como pagada para desbloquear al estudiante? ¿Existe un endpoint en la API para eso? Si no existe, ¿qué endpoint de la especificación original lo contemplaba y por qué no se implementó en Version_2?
```

> *Propósito:* verificar que el chatbot detecta la brecha entre la especificación (POST /multas/:id/pago) y Version_2 (que no implementa ese endpoint). Es un hallazgo de completitud válido.

Respuesta del chatbot.
```
Chatbot: En SQLite, podemos marcar una multa como pagada insertando una fila con el valor 1 en la columna "pagado" de la tabla donde se almacena la multa.

Sin embargo, no existe un endpoint específico en la API para actualizar el estado de una multa y desbloquear al estudiante. Según la especificación original, RN8 (Multas) establece que el bloqueo por multa se levanta automáticamente cuando todas las multas del estudiante pasan a estado "pagado".

En Version 2, no se implementó este endpoint porque no es necesario actualizar explícitamente el estado de una multa para desbloquear al estudiante. La lógica de actualización se rige por RN8, que establece un mecanismo auto-actualizante para levantar los bloqueos.

En otras palabras, cuando todas las multas de un estudiante pasen a estado "pagado", automáticamente se desbloquea el estudiante. Por lo tanto, no es necesario un endpoint explícito para actualizar el estado de una multa y desbloquear al estudiante.
```

#### Pregunta 6-F — Consistencia de nomenclatura al cambiar de versión

```
Tú: la guía original de pruebas usa "estudianteId" y "ejemplarId" en el body del curl. Pero cuando ejecuto el curl contra localhost:3001 me da 422. ¿Por qué falla y cuál es el body correcto para Version_2?
```

> *Propósito:* verificar que el chatbot conoce la diferencia de nomenclatura camelCase (V1) vs snake_case (V2) y puede explicar por qué Pydantic rechaza con 422 en lugar de 400.

Respuesta del chatbot.
```
Chatbot: La razón por la que falla el curl es que, según RN5 (Disponibilidad), se espera que los campos "estudianteId" y "ejemplarId" estén en snake_case.

En la guía original de pruebas, se usan "estudianteId" y "ejemplarId", pero en Version 2, deben ser "estudent_id" y "ejemplar_id".

Para ejecutar el curl correcto, debes modificar el cuerpo del request para utilizar los nombres de campo correctos:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"student_id": "EST-POS-01", "ejemplar_id": "EJ-001-06"}' \
  http://127.0.0.1:8000/api/reservas

De esta manera, se enviará un request con el cuerpo correcto y probablemente se producirá una respuesta exitosa.
```

---

### Preguntas útiles que generó el chatbot
| Pregunta que hice | Qué generó el chatbot | ¿Fue útil? |
|-------------------|-----------------------|------------|
| crea los datos de prueba base para todas las reglas: un estudiante pregrado EST-PRE-01, uno posgrado EST-POS-01, un libro normal LIB-001 con 6 ejemplares y un libro de alta demanda LIB-002 con 1 ejemplar | El chatbot generó una estructura conceptual de datos, seguida de comandos curl. Sin embargo, ignoró las cantidades solicitadas, inventó la sintaxis de los payloads usando echo -e | curl para endpoints JSON, asumió campos inexistentes en los endpoints de libros/estudiantes, e inventó un comando GET /api/reservas que no existe. | No (Los comandos fallarían catastróficamente al ejecutarse contra la API v2) |
| genera la prueba RN1 completa: crear los 3 préstamos válidos para pregrado y luego intentar el cuarto | Generó la secuencia de comandos curl para los 4 préstamos. Acertó de forma excelente en la lógica del negocio (RN1), mapeó bien el código 409 y la estructura del JSON de error esperado. Sin embargo, falló críticamente en la consistencia de los IDs, usando IDs de estudiantes y ejemplares que no existen en nuestro entorno. | No (Si copias y pegas estos comandos tal cual, la API te devolverá errores de recursos inexistentes o fallas de Pydantic).|
| Genera la prueba RN2 completa para el estudiante de posgrado. Recuerda que su límite es 5 préstamos válidos y el 6° debe fallar.<br>REGLAS DE FORMATO OBLIGATORIAS PARA WINDOWS: <br>1. Cada comando debe empezar exactamente con la palabra "EJECUTAR: curl".<br>2. No uses saltos de línea entre "EJECUTAR:" y el comando.<br>3. IMPORTANTE: No uses comillas simples (') en las URLs ni en los JSON. Deja las URLs sin comillas (ejemplo: http://127.0.0.1:8000/api/prestamos) y usa comillas dobles con escape (\") dentro del JSON del data. <br>4. Genera exactamente 6 comandos de préstamo seguidos usando el estudiante "EST-POS-01". Como los ejemplares 01, 02 y 03 ya están ocupados, usa en orden los ejemplares: "EJ-001-04", "EJ-001-05", "EJ-001-06", "EJ-002-01". <br>Ejemplo de formato esperado:EJECUTAR: curl -X POST -H "Content-Type: application/json" -d "{\"estudiante_id\": \"EST-POS-01\", \"ejemplar_id\": \"EJ-001-04\"}" http://127.0.0.1:8000/api/prestamos | Generó la lista de comandos respetando estrictamente las reglas de escape para Windows (\"). Sin embargo, falló en la cobertura del escenario: solo incluyó 4 préstamos válidos, un GET colado y un 5° intento repetido, en lugar de los 5 préstamos válidos diferentes + el 6° bloqueado que requiere la regla de negocio de posgrado. | Parcialmente (El formato fue 100% útil y activó la automatización de forma exitosa, pero los datos internos siguen siendo lógicamente insuficientes para estresar la RN2). |
| prueba que un ejemplar ya prestado no se puede prestar de nuevo (RN5) | Recordó de forma autónoma el formato con comillas dobles escapadas (\"). Ejecutó automáticamente el comando y validó de nuevo la regla RN5 con éxito. | Sí (El modelo retuvo el contexto del formato y la lógica de pruebas se mantuvo perfecta). |
| genera pruebas de entradas inválidas: body vacío, estudiante inexistente y ejemplar inexistente | Generó 3 comandos curl con campos incompletos, provocando que Pydantic los frenara a todos con error 422 (Field required) en lugar de evaluar la base de datos. | Parcialmente (Confirmó que la ráfaga de chatbot.js funciona, pero los datos del JSON estuvieron mal estructurados por la IA). |
| el resultado del body vacío fue { "error": "..." } con código 400. ¿Eso es correcto según la especificación? | Repitió el curl vacío afirmando que esperaba un código 400 con la razón "limite_prestamos_alcanzado". | No (El chatbot alucinó: ignoró que los fallos de esquema son 422 y propuso una regla de negocio imposible de evaluar sin un ID). |
| el endpoint POST /api/prestamos devolvió 200 OK en lugar de 409 cuando el estudiante ya tiene 3 préstamos. El body fue: { "id": "P-004", ... }. ¿Qué regla está violando y en qué archivo debería buscar el problema? | Generó un curl erróneo con "ejemplar_id": 1 (error 422). Conceptualmente sugirió revisar la regla RN1, aunque confundió el límite de posgrado (5) con el de pregrado (3). | Parcialmente (Acertó en que es un problema de límites de préstamos, pero falló en la sintaxis del comando y en precisar el límite según el tipo de estudiante).|
|un estudiante de pregrado tiene exactamente 3 préstamos activos, uno de ellos está vencido y además tiene una multa pendiente de $6.000. Intenta crear un nuevo préstamo para ese estudiante. ¿Qué regla se activa primero según el código de Version_2 y qué código HTTP esperas? Dame el curl exacto para reproducirlo.|No analizó el orden de las reglas, no entregó el código HTTP esperado y omitió por completo generar el comando curl. Volvió a reciclar la explicación ficticia sobre la función validate.|No|
| tengo un préstamo activo del ejemplar EJ-002-01 (que pertenece a LIB-002, un libro de alta demanda) y no hay ninguna reserva pendiente sobre ese libro. ¿Puedo renovar ese préstamo? Dame el curl para intentarlo y explica qué respuesta esperas según las reglas de la biblioteca. | Acertó conceptualmente al bloquear la renovación por ser un libro de alta demanda. Sin embargo, generó un curl roto para Windows (comillas simples) y se inventó una ruta inválida (/actualizar). | Parcialmente, fue util en la validacion de la regla del negocio |
| quiero probar RN8 sin esperar días reales. Sé que POST /api/prestamos acepta el campo opcional fecha_prestamo. Dame el curl completo para: (1) crear un préstamo con fecha 20 días atrás sobre un libro normal, (2) devolver ese préstamo hoy ¿Cuántos días de retraso habrá y cuál será el monto exacto de la multa? | Entregó dos comandos curl (uno de creación con fecha dura en 2023 y otro de devolución en la ruta inventada /actualizar). Evadió hacer el cálculo matemático de los días de retraso y el dinero de la multa, diciéndote que "lo miraras en la respuesta del servidor". | No (No cumplió con el propósito de calcular los 5 días de retraso ni los $10.000 de multa esperados, y volvió a fallar en la sintaxis de las comillas simples para Windows). |
| EST-PRE-01 tiene un préstamo activo de EJ-001-01 (LIB-001, libro normal, no vencido). EST-POS-01 quiere el mismo libro y hace una reserva. Ahora EST-PRE-01 intenta renovar. Dame los tres curls en orden: crear la reserva, intentar la renovación y explicar por qué debe fallar. | Generó el curl 1 asociando la reserva erróneamente al estudiante equivocado (EST-PRE-01 en lugar de EST-POS-01). El curl 2 repitió la ruta falsa /actualizar. El curl 3 no lo hizo. Conceptualmente acertó de forma impecable en la teoría de la RN9/RN13 y el código HTTP 409. | Parcialmente (Teóricamente entendió a la perfección cómo la reserva bloquea la renovación, pero cruzó los IDs de los estudiantes en los comandos y falló en las rutas del backend). |
| EST-PRE-01 fue bloqueado por una multa de $4.000 (RN4). En nuestra base de datos (SQLite), ¿cómo marcaríamos esa multa como pagada para desbloquear al estudiante? ¿Existe un endpoint en la API para eso? Si no existe, ¿qué endpoint de la especificación original lo contemplaba y por qué no se implementó en Version_2? | Explicó correctamente la actualización en base de datos (pagado = 1). Sin embargo, se inventó una "lógica auto-actualizante" mágica en el backend para justificar por qué no existía el endpoint de pago en la Version_2, camuflando la brecha de desarrollo. | Parcialmente (Sirve para entender cómo alterar la base de datos de forma manual para desbloquear las pruebas, pero alucinó con los argumentos de arquitectura sobre la automatización del backend). |
| la guía original de pruebas usa "estudianteId" y "ejemplarId" en el body del curl. Pero cuando ejecuto el curl contra localhost:3001 me da 422. ¿Por qué falla y cuál es el body correcto para Version_2? | Explicó de manera excelente el cambio a snake_case, pero al escribir el body correcto cometió un error tipográfico escribiendo "student_id" (en inglés) en lugar de "estudiante_id", y mandó el préstamo al endpoint de /reservas. | Parcialmente (El diagnóstico del error 422 por nomenclatura fue muy acertado, pero su solución de código arrastró un typo de traducción que mantendría el error en tu consola). |

### Limitaciones observadas
- ¿El chatbot inventó endpoints que no existen?

Sí, se la pasó inventando rutas como PATCH /api/prestamos/actualizar porque no tenía acceso real a mi código fuente.

- ¿Confundió reglas entre sí?

Sí, cruzó los límites de pregrado y posgrado, se inventó que para la RN3 hacían falta 3 préstamos vencidos y erró en los números de las reglas.

- ¿Tuvo que corregirle algo?

Bastante. Desde la sintaxis del curl para Windows (por usar comillas simples) hasta el orden de la cascada de bloqueos y términos en "espanglish" como student_id.

### Comparación: chatbot local vs ChatGPT/Claude en la nube
- ¿Qué diferencias notaste en la calidad de las respuestas?

El modelo local se fatiga rápido, pierde el hilo del contexto, olvida las reglas de formato si le metes teoría y alucina con la lógica. Los de la nube mantienen las instrucciones estrictas a la perfección y razonan mucho mejor los casos límite.

- ¿Qué ventajas tiene correrlo localmente?

Privacidad total (mis datos y código no salen de mi máquina), es 100% gratis, funciona sin internet y se integra directo con mis scripts automatizados de prueba.