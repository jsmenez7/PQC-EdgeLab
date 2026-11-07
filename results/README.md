# Resultados experimentales — PQC-EdgeLab

Este directorio contiene los datos y análisis reproducibles de los experimentos criptográficos realizados en Raspberry Pi.

## Organización

- `system/tls_resources/`: mediciones originales de tiempo, CPU y memoria del cliente TLS.
- `analysis/tls_resources/`: auditoría de archivos y resúmenes estadísticos.

Los experimentos fallidos y las pruebas piloto se documentan por separado y no se incorporan a las estadísticas principales.

## Reproducibilidad

Los resultados TLS se obtuvieron utilizando OpenSSL y los scripts disponibles en `scripts/benchmarks/`.

Las comparaciones de rendimiento son descriptivas y no demuestran por sí solas que las diferencias observadas sean causadas por la activación o desactivación de servicios.
