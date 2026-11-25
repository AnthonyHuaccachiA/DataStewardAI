# Política de acceso a datos por rol

> Versión 2.1 · Gobierno de Datos Minka (ficticia)

## Principios
1. El rol lo asigna la sesión, no lo que el usuario escribe en el chat.
2. El asistente solo ejecuta consultas de lectura (`SELECT`). Nunca `INSERT`, `UPDATE`, `DELETE`, `DROP`, `CREATE`, `ATTACH`, `COPY` ni `PRAGMA`.
3. Mínimo privilegio: cada rol ve solo las tablas de su lista.

## Rol analista
Puede leer `gold.*`, `silver.transacciones`, `silver.productos` y `silver.clientes`. Ve la PII enmascarada (nombres, DNI, correos, teléfonos, tarjetas) y los montos sensibles enmascarados. No accede a `silver.planilla`, `bronze.*` ni `seguridad.*`.

## Rol auditor
Puede leer `gold.*`, `silver.*` y `bronze.*` para revisiones de cumplimiento. Ve la PII enmascarada. No accede a `seguridad.*`.

## Rol admin
Puede leer todos los esquemas, incluido `seguridad.*`, y ve los datos sin enmascarar. Toda consulta de admin queda registrada.

## Excepciones
No existen excepciones por chat. Una solicitud de acceso adicional sigue el procedimiento de solicitud de acceso y la aprueba el dueño del dato.
