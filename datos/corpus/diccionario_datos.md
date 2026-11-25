# Diccionario de datos

| Columna | Tabla | Descripción | Clasificación |
|---|---|---|---|
| cliente_id | silver.clientes | Identificador interno del cliente | Interna |
| nombre_completo | silver.clientes | Nombres y apellidos | PII |
| dni | silver.clientes | Documento de identidad (8 dígitos) | PII |
| email | silver.clientes | Correo electrónico | PII |
| telefono | silver.clientes | Celular (9 dígitos) | PII |
| fecha_nacimiento | silver.clientes | Fecha de nacimiento | PII |
| segmento | silver.clientes | masivo, emergente, preferente, premium | Interna |
| ingreso_mensual | silver.clientes | Ingreso mensual declarado | Sensible |
| monto | silver.transacciones | Monto de la compra en soles | Interna |
| canal | silver.transacciones | app, web, tienda, agente, pos | Interna |
| numero_tarjeta | silver.transacciones | Número de tarjeta (prefijo de prueba 4000) | PII |
| saldo | silver.productos | Saldo del producto | Sensible |
| sueldo_bruto | silver.planilla | Sueldo bruto mensual | Sensible |
| cuenta_abono | silver.planilla | Cuenta donde se abona el sueldo | PII |
| n_tx | gold.kpi_transacciones_diarias | Número de transacciones aprobadas | Interna |
| monto_total | gold.* | Suma de montos | Interna |
| porcentaje_ok | gold.calidad_datos | Porcentaje de registros que cumplen la regla | Interna |
