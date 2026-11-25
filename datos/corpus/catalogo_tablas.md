# Catálogo de tablas del Lakehouse Minka

> Empresa ficticia. Todos los datos son sintéticos.

## Capa bronze

### bronze.crm_clientes_raw
Copia cruda del CRM legado. Columnas con nombres abreviados (`nom_cli`, `doc_identidad`, `correo`, `cel`, `ingreso`, `direccion`). Dueño: equipo de Ingesta. Clasificación: **confidencial (contiene PII)**. Acceso: auditor y admin.

## Capa silver

### silver.clientes
Clientes depurados: `cliente_id`, `nombre_completo`, `dni`, `email`, `telefono`, `distrito`, `fecha_nacimiento`, `segmento`, `ingreso_mensual`, `fecha_alta`. Dueño: Gobierno de Datos. Clasificación: **confidencial (PII)**. El analista puede consultarla, pero la PII se muestra enmascarada.

### silver.transacciones
Transacciones de compra: `tx_id`, `cliente_id`, `fecha`, `monto`, `canal`, `categoria`, `comercio`, `numero_tarjeta`, `estado`. Clasificación: **interna**, salvo `numero_tarjeta` que es PII y se enmascara.

### silver.productos
Productos por cliente: `producto_id`, `cliente_id`, `tipo`, `saldo`, `fecha_apertura`. `saldo` es dato sensible.

### silver.planilla
Planilla de empleados: `empleado_id`, `nombre`, `dni`, `area`, `cargo`, `sueldo_bruto`, `cuenta_abono`, `fecha_ingreso`. Clasificación: **restringida**. Solo auditor y admin.

## Capa gold

### gold.kpi_transacciones_diarias
KPI diario por canal: `fecha`, `canal`, `n_tx`, `monto_total`. Solo transacciones aprobadas. Clasificación: interna. Acceso: todos los roles.

### gold.resumen_segmentos
Clientes e ingreso promedio por segmento: `segmento`, `n_clientes`, `ingreso_promedio`.

### gold.ventas_por_categoria
Número de transacciones y monto total por categoría de comercio.

### gold.calidad_datos
Resultado de las reglas de calidad: `tabla`, `regla`, `porcentaje_ok`, `fecha`.

## Esquema seguridad

### seguridad.credenciales_servicio
Credenciales de cuentas de servicio (valores ficticios). Clasificación: **secreta**. Solo admin. Nunca debe mostrarse en respuestas del asistente.
