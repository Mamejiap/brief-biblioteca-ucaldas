# Prompt #07

**Fecha y hora:** 2026-05-26 12:32

**Propósito en una línea:** Corregir la ejecución de comandos usando Git Bash en lugar de PowerShell para que los curls funcionen correctamente

**Etapa del taller:** 4

**IA usada:** GitHub Copilot

---

### Prompt enviado (literal)

```
Usa terminal Git Bash para ejecutar los curls. No uses PowerShell.
```

---

### Resumen de la respuesta de la IA

Cambió a Git Bash usando `&'C:\Program Files\Git\bin\bash.exe'` en PowerShell. Después de entrar en bash, los curls funcionaron correctamente con toda la sintaxis del taller: pipes `|`, comandos como `head`, variables `$BASE_SIN_IA`, saltos de línea con backslash `\` y redirecciones. PowerShell interpretaba `head` como cmdlet (no existe) y fallaba; bash ejecutó los comandos correctamente. Ejecutó los 4 curls de prueba RN1-B sin problemas una vez en bash. La solución fue determinante para poder hacer testing.

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

El entorno ejecutable importa tanto como el código. PowerShell y Bash tienen sintaxis incompatibles: PowerShell trata `head` como un cmdlet inexistente, mientras que bash lo ejecuta como comando estándar. El taller fue diseñado con sintaxis bash (pipes, variables, etc.), así que cualquier testing debe hacerse en bash. Una instrucción de una línea resolvió un problema de ejecución que parecía ser del código.

---
