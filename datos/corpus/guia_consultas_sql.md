# Guía de consultas SQL para analistas

- Prefiera las tablas `gold` para reportes: ya están agregadas y no tienen PII.
- Use `LIMIT` al explorar tablas silver.
- Ejemplo de transacciones por canal:
  `SELECT canal, SUM(n_tx) AS n_tx FROM gold.kpi_transacciones_diarias GROUP BY canal`
- Ejemplo de clientes por segmento:
  `SELECT segmento, n_clientes FROM gold.resumen_segmentos`
- Las consultas de escritura están prohibidas para el asistente.
