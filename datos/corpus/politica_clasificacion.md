# Política de clasificación de datos

## Niveles
- **Pública**: puede publicarse.
- **Interna**: uso interno, sin datos personales (por ejemplo KPI agregados).
- **Confidencial**: contiene datos personales (PII) de clientes: nombre, DNI, correo, teléfono, fecha de nacimiento, número de tarjeta.
- **Restringida**: datos de empleados (planilla, sueldos, cuentas de abono).
- **Secreta**: credenciales y llaves.

## Etiquetado automático
El clasificador de columnas sensibles etiqueta cada columna como `PII`, `SENSIBLE` o `NO_SENSIBLE` a partir de su nombre y de una muestra de valores. Las columnas `PII` y `SENSIBLE` se enmascaran para los roles analista y auditor.

## Protección de datos personales
El tratamiento de datos personales sigue la Ley 29733 y su reglamento. Los datos de este Lakehouse son sintéticos.
