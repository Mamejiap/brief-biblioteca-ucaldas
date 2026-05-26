# Prompt #06

**Fecha y hora:** 2026-05-26 12:30

**Propósito en una línea:** Ejecutar la prueba RN1-B para validar si la API v1 implementa el límite de 3 préstamos simultáneos por estudiante pregrado

**Etapa del taller:** 4

**IA usada:** GitHub Copilot

---

### Prompt enviado (literal)

```
Actúa como un ingeniero de software experto en testing de APIs REST con curl.

Contexto:
Estoy trabajando en el repositorio `brief-biblioteca-ucaldas`.
La base de los casos de prueba está en:

`02-tu-trabajo/pruebas-reglas-negocio.md`

Estoy llenando la bitácora de la versión 1 en:

`02-tu-trabajo/plantilla-bitacora-v1.md`

Por ahora NO necesito ejecutar todas las pruebas. Solo quiero ensayar la prueba:

`RN1-B cuarto prestamo pregrado`

Objetivo:
Ejecutar únicamente la prueba RN1-B usando solo la variable:

`BASE_SIN_IA`

No ejecutes todavía BASE_CON_IA.
No ejecutes RN2-B ni las demás pruebas.
No modifiques el código de la API.
No modifiques archivos todavía, solo dame los resultados para que yo los copie manualmente.

Instrucciones:

1. Abre o revisa el archivo:
   `02-tu-trabajo/pruebas-reglas-negocio.md`

2. Localiza la prueba:
   `RN1-B cuarto prestamo pregrado`

3. Identifica los curl necesarios para preparar y ejecutar RN1-B.
   Si RN1-B representa el cuarto préstamo de un estudiante de pregrado, asegúrate de que primero existan o se creen los tres préstamos previos necesarios para preparar el escenario.

4. Ejecuta la prueba únicamente contra:
   `$BASE_SIN_IA`

5. Captura:
   - Código HTTP real.
   - Body real de la respuesta.
   - Si el body es útil o no.

Criterio para "body útil":
- Escribe `Si` si la respuesta incluye un mensaje que explica por qué falló.
- Escribe `No` si solo devuelve el código, respuesta vacía o no explica claramente el fallo.

Resultado esperado para RN1-B:
- Regla: RN1
- Esperado: HTTP 409
- Motivo esperado: el estudiante de pregrado intenta realizar un cuarto préstamo, pero el máximo permitido es 3.

Formato de salida requerido:

1. Primero muestra el curl exacto ejecutado contra BASE_SIN_IA.

2. Luego muestra:

```txt
HTTP real Sin IA: [codigo]
Body real Sin IA:
[body]
Body útil Sin IA: Si/No
Luego entrega la fila lista para pegar en la tabla:
| RN1-B cuarto prestamo pregrado | RN1 | 409 | [HTTP real] | [Si/No] | | |

Finalmente responde brevemente estas preguntas solo para RN1-B:

¿Qué código HTTP devolvió la versión sin IA?
¿El cuerpo de la respuesta identifica por qué falló?
¿El resultado coincide con el esperado 409?
Si no coincide, ¿qué indica eso sobre la implementación de RN1?
```

Importante:

Si el endpoint no existe, registra el HTTP real y el body real.
Si el resultado es 201 Created o 200 OK en lugar de 409, indícalo como posible incumplimiento de RN1.
Si el body muestra un error por datos mal preparados, indícalo y explica qué dato faltó preparar.
```

---

### Resumen de la respuesta de la IA

Ejecutó 4 curls POST a `/prestamos` en Git Bash contra `http://localhost:8000`. Los 3 primeros con diferentes `libro_id` devolvieron 201 Created. El 4to intento (RN1-B) también devolvió 201 Created con nuevo préstamo aceptado, cuando debería haber retornado 409 Conflict. El body NO incluye mensaje de error (body útil = No). Capturó el HTTP exacto (201) y body completo. Detectó automaticamente que la API v1 no implementa la regla RN1 (límite de préstamos por estudiante). También identificó incompatibilidad: el test esperado usa `tipo: pregrado` y IDs como `EST-PRE-01`, pero la API v1 solo tiene IDs numéricos y sin campo de tipo.

---

### Mi evaluación

**¿La respuesta cumplió con lo que pedí?**

- [x] Completamente.
- [ ] Parcialmente. Faltó: [...]
- [ ] No, se desvió. Hizo: [...]

**¿La acepté tal cual o la modifiqué?**

- [x] Tal cual.
- [ ] La modifiqué a mano. Cambios: [...]
- [ ] Le pedí corrección con un prompt nuevo (ver prompt #[N+1]).
- [ ] La rechacé completamente. Razón: [...]

**¿Qué aprendí de esta interacción?**

La IA ejecutó los curls correctamente en bash una vez que cambié a Git Bash. Sin embargo, el resultado demostró que la API v1 no valida RN1 (límite de préstamos por tipo de estudiante). Aprendí que una auditoría de código estática (como la que hizo en Etapa 3) necesita confirmación ejecutando los curls: H1 (omisión de RN1) se confirmó prácticamente. El test esperado asume estructura de datos que la v1 no tiene (tipos de estudiante, ejemplares individuales).

---
