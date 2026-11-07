# Resultados preliminares — Benchmark TLS 1.3

## Proyecto PQC-EdgeLab

**Fecha de experimentación:** 6 de noviembre de 2026.

### 1. Objetivo

Evaluar preliminarmente el comportamiento temporal de las conexiones TLS 1.3 clásicas (X25519) e híbridas (X25519MLKEM768), considerando dos condiciones de ahorro energético Wi-Fi.

### 2. Configuración experimental

- Servidor: Raspberry Pi Zero W (ARMv6).
- Cliente: Raspberry Pi Zero 2 W (ARMv7).
- Sistema operativo: Raspbian 13 (Trixie).
- Biblioteca: OpenSSL 3.5.7.
- Protocolo: TLS 1.3.
- Ciphersuite: TLS_AES_256_GCM_SHA384.
- Repeticiones: 100 por grupo y sesión.
- Orden: pares aleatorizados con semilla fija.

El tiempo medido corresponde a la ejecución completa del proceso cliente OpenSSL, no exclusivamente al handshake TLS.

### 3. Resultados experimentales

| Métrica | ON clásico | ON híbrido | OFF clásico | OFF híbrido |
|---|---:|---:|---:|---:|
| Media (ms) | 431.987 | 289.526 | 299.576 | 270.359 |
| Mediana (ms) | 195.180 | 200.820 | 195.335 | 201.306 |
| Desv. estándar (ms) | 901.020 | 606.470 | 523.657 | 179.018 |
| P95 (ms) | 1306.712 | 438.975 | 689.308 | 757.398 |
| Ejecuciones mayores de 1 s | 9 | 2 | 2 | 1 |
| Conexiones exitosas | 100/100 | 100/100 | 100/100 | 100/100 |

### 4. Observaciones preliminares

Las medianas se mantuvieron relativamente estables entre ambas sesiones. Sin embargo, las medias, desviaciones estándar y percentiles 95 presentaron variaciones importantes.

Se identificaron ejecuciones que superaron los cinco segundos, especialmente en la primera sesión.

En la segunda sesión se registró que el ahorro energético Wi-Fi del cliente estaba desactivado tanto al inicio como al final de las mediciones.

### 5. Limitaciones

Las mediciones se realizaron en una red Wi-Fi compartida y contienen el tiempo de ejecución del cliente OpenSSL, incluyendo operaciones adicionales al establecimiento criptográfico.

Se dispone de una sesión por condición energética, por lo que los datos todavía no permiten establecer una relación causal entre el ahorro Wi-Fi y el rendimiento TLS.

No se eliminaron las observaciones extremas.

### 6. Próximas actividades

- Mejorar la instrumentación temporal del benchmark.
- Registrar CPU, RAM y condiciones de red durante las pruebas.
- Repetir las condiciones experimentales en sesiones independientes.
- Realizar benchmarks de ML-KEM-768 mediante Python/liboqs.
- Aplicar análisis estadístico a los resultados completos.
