# Glosario de KPI

## Ticket promedio
Monto total dividido entre el número de transacciones aprobadas. Se calcula desde `gold.kpi_transacciones_diarias`.

## Transacciones por canal
Conteo de transacciones aprobadas agrupado por `canal`. Fuente: `gold.kpi_transacciones_diarias`.

## Tasa de rechazo
Transacciones con `estado = 'rechazada'` entre el total. Fuente: `silver.transacciones`.

## Clientes por segmento
Número de clientes en cada segmento. Fuente: `gold.resumen_segmentos`.

## Calidad de datos
Porcentaje de registros que cumplen cada regla de calidad. Fuente: `gold.calidad_datos`. El umbral aceptable es 98%.
