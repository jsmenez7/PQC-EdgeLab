# PQC-EdgeLab — Registro 04: evaluación de recursos y configuración reducida de Raspberry Pi

**Fecha de cierre de esta etapa:** 7 de noviembre de 2026  
**Estado:** evaluación exploratoria finalizada; conclusiones provisionales pendientes de análisis estadístico exhaustivo sobre archivos originales  
**Ámbito:** Raspberry Pi Zero 2 W (`pqc-client`, ARMv7l) y Raspberry Pi Zero W (`pqc-server`, ARMv6l)

> **Alcance de este documento.** Este registro consolida las salidas de terminal y resúmenes numéricos de las sesiones experimentales proporcionados durante el desarrollo de PQC-EdgeLab. La comprobación definitiva de cada observación, los metadatos y las distribuciones completas debe realizarse sobre los archivos CSV y TXT originales antes de enviar un artículo científico. Se conservan los ensayos fallidos como incidencias y se excluyen de las comparaciones de rendimiento.

## 1. Objetivo y contexto

Evaluar una posible reducción de recursos de sistema sin comprometer la funcionalidad de las pruebas de criptografía postcuántica (PQC): (i) TLS 1.3 clásico `X25519`, (ii) TLS 1.3 híbrido `X25519MLKEM768` con OpenSSL y (iii) ML-KEM-768 mediante `liboqs-python`, tanto localmente como mediante TCP entre placas.

Se exploraron dos intervenciones **temporales y reversibles**: detener `bluetooth.service` y detener `udisks2.service`. No se alteraron los servicios críticos de conectividad (`ssh`, `NetworkManager`, `wpa_supplicant`, `avahi-daemon`). El ahorro energético de Wi-Fi permaneció en `Power save: off` durante los ensayos TLS de comparación. Los experimentos se realizaron a través de red Wi-Fi; la conectividad inalámbrica es una fuente de variabilidad.

## 2. Entorno y herramientas

| Característica | Cliente | Servidor |
|---|---|---|
| Equipo | Raspberry Pi Zero 2 W | Raspberry Pi Zero W |
| Arquitectura | ARMv7l | ARMv6l |
| Sistema | Raspberry Pi OS Lite / Raspbian 13 (Trixie), 32 bits | Raspberry Pi OS Lite / Raspbian 13 (Trixie), 32 bits |
| Memoria total reconocida, `free -m` | ~424 MiB | ~426 MiB |
| OpenSSL | 3.5.7 | 3.5.7 |
| Biblioteca PQC | `liboqs` 0.16.0; `liboqs-python` 0.16.0.1 | `liboqs` 0.16.0; `liboqs-python` 0.16.0.1 |
| Interconexión | Wi-Fi 2,4 GHz; nombres `.local` | Wi-Fi 2,4 GHz; nombres `.local` |

En el servidor ARMv6 se utilizó una compilación experimental de `liboqs` con permiso explícito para una arquitectura no soportada oficialmente. Los resultados de esta plataforma no constituyen certificación ni garantía general de soporte.

**Instrumentación TLS del cliente:** `scripts/benchmarks/benchmark_tls_resources.sh`, usando `/usr/bin/time` (GNU time 1.9), `timeout 15`, `openssl s_client`, y comprobación del éxito de conexión, verificación del certificado y grupo TLS negociado. Se registraron `user_s`, `system_s`, `elapsed_s`, `maxrss_kib`, `exit_code` y `verified` en CSV.

**Precisión de las métricas:** `elapsed_s` corresponde a la ejecución completa del comando cliente —incluidos arranque de procesos, E/S, red y cierre—, **no** a la duración aislada del handshake. `user_s + system_s` es tiempo de CPU consumido por el comando monitorizado y sus procesos hijos, no porcentaje de CPU. `maxrss_kib` es el máximo conjunto residente observado por la herramienta, **no** un incremento de memoria exclusivo de ML-KEM ni la RAM total del sistema. La resolución mostrada por GNU time es relativamente gruesa para conexiones cortas.

## 3. Experimento de Bluetooth: recursos del cliente TLS

### 3.1 Diseño

Se ejecutaron cuatro series completas en orden temporal **ON-1 → OFF-1 → OFF-2 → ON-2**. Cada serie incluyó 50 conexiones TLS `X25519` y 50 conexiones `X25519MLKEM768`, con orden alternado dentro de cada repetición. En las cuatro series, la auditoría de `exit_code=0` y `verified=1` confirmó **400/400 conexiones válidas**. La secuencia es una exploración temporal, no un experimento aleatorizado por bloques; por tanto, los cambios coincidentes no prueban causalidad.

### 3.2 Duración de ejecución del cliente

| Serie | Estado Bluetooth | X25519 media (ms) | X25519 mediana (ms) | Híbrido media (ms) | Híbrido mediana (ms) |
|---|---|---:|---:|---:|---:|
| ON-1 | ON | 209,4 | 190 | 202,8 | 190 |
| OFF-1 | OFF | 209,0 | 190 | 186,2 | 180 |
| OFF-2 | OFF | 193,0 | 190 | 185,6 | 180 |
| ON-2 | ON | 270,0 | 200 | 321,4 | 190 |

En ON-2 se observaron 4/50 conexiones clásicas y 2/50 híbridas que superaron los 500 ms. El máximo híbrido fue **5,21 s**, frente a máximos de 0,36 s, 0,23 s y 0,26 s en ON-1, OFF-1 y OFF-2, respectivamente. La media de ON-2 está afectada por la cola de latencia. Estas observaciones se mantuvieron por ser conexiones verificadas.

### 3.3 CPU y RSS del cliente

| Serie | CPU media X25519 (ms) | CPU media híbrida (ms) | RSS mediana X25519 (KiB) | RSS mediana híbrida (KiB) |
|---|---:|---:|---:|---:|
| ON-1 | 57,0 | 58,2 | 7580 | 7580 |
| OFF-1 | 57,8 | 56,8 | 7580 | 7580 |
| OFF-2 | 57,4 | 55,4 | 7580 | 7580 |
| ON-2 | 59,0 | 57,6 | 7580 | 7580 |

**Interpretación:** no se detectó una reducción consistente y reproducible de CPU o RSS del cliente con Bluetooth desactivado. Aunque las medianas híbridas fueron 180 ms en ambas series OFF frente a 190 ms en ambas ON, la variabilidad de red y las diferencias temporales impiden atribuir causalidad a Bluetooth.

### 3.4 Comparación adicional durante instrumentación del servidor

Se realizaron **dos series adicionales** de 100 conexiones verificadas cada una, una con Bluetooth ON y otra con OFF, mientras se tomaban lecturas de CPU del servidor.

| Condición | Grupo | Tiempo medio cliente (ms) | CPU media cliente (ms) | RSS media cliente (KiB) |
|---|---|---:|---:|---:|
| ON | X25519 | 217,4 | 56,0 | 7564,5 |
| ON | X25519MLKEM768 | 202,4 | 60,6 | 7555,9 |
| OFF | X25519 | 218,0 | 54,8 | 7563,6 |
| OFF | X25519MLKEM768 | 224,8 | 61,8 | 7565,4 |

Esta comparación adicional tampoco respalda una mejora consistente del tiempo de ejecución cuando Bluetooth está desactivado.

## 4. Recursos del proceso TLS del servidor ARMv6

En el servidor, el proceso `openssl s_server` se mantuvo activo con **PID 4109** en ambos intervalos, y se midieron los ticks de CPU de `/proc/4109/stat`, con `CLK_TCK=100`.

| Condición | Ticks antes | Ticks después | CPU proceso durante intervalo | Ventana observada |
|---|---:|---:|---:|---|
| Bluetooth ON | 848 | 1656 | 8,08 s | 00:10:02–00:10:44 |
| Bluetooth OFF | 1656 | 2466 | 8,10 s | 00:13:47–00:14:39 |

Diferencia OFF frente a ON: **+0,02 s (+0,25 %)** durante sendos lotes de 100 conexiones (50 clásicas + 50 híbridas). La diferencia es muy pequeña, y las ventanas de observación no tuvieron exactamente la misma duración. El cálculo es **CPU agregada del servidor durante la ventana**; no separa operaciones criptográficas por grupo ni aísla la carga de fondo. Las lecturas RSS del proceso fueron 8260→8264 KiB en ON y 8264→8264 KiB en OFF; `VmHWM` es el pico acumulado desde el arranque del proceso, no por conexión.

**Interpretación:** no hay evidencia de una mejora reproducible del consumo de CPU del servidor causada por detener Bluetooth en este escenario.

## 5. Exploración de `udisks2.service`

Se observó que `udisksd` estaba activo en ambas Raspberry, sin unidades externas de almacenamiento identificadas por `lsblk`; el sistema usaba microSD y swap mediante `zram`. Se detuvo temporalmente con `sudo systemctl stop udisks2.service`. No se ejecutó `disable` ni `mask`.

### 5.1 Cliente ARMv7

| Secuencia | Estado `udisks2` | `MemAvailable` (KiB) |
|---|---|---:|
| ON-1 | Activo | 317196 |
| OFF-1 | Inactivo | 319452 |
| ON-2 | Activo | 317660 |
| OFF-2 | Inactivo | 316668 |

El primer paso OFF mostró **+2256 KiB**, pero el segundo OFF mostró **−992 KiB** respecto del ON precedente. Por consiguiente, **no quedó establecido un ahorro reproducible de `MemAvailable`**. Se confirmó que SSH y NetworkManager continuaron activos durante el ensayo.

### 5.2 Servidor ARMv6

Antes de detener el servicio, las métricas del proceso `udisksd` incluyeron `Rss=9676 kB`, `Pss≈4147–4150 kB`, `Private_Clean=2456 kB`, `Private_Dirty=340 kB` y `Swap=1068 kB`. La suma privada residente fue **2796 KiB**; RSS y PSS no equivalen al ahorro neto del sistema.

| Secuencia | Estado `udisks2` | `MemAvailable` (KiB) |
|---|---|---:|
| ON-1 | Activo | 310676 |
| OFF | Inactivo | 311632 |
| ON-2 | Activo | 313080 |

Aunque la primera detención mostró **+956 KiB**, al restaurar el servicio aumentó de nuevo `MemAvailable` **+1448 KiB**. Por tanto, tampoco aquí se puede atribuir la variación exclusivamente a `udisks2`. El servidor OpenSSL permaneció escuchando en el puerto 4433; SSH y NetworkManager continuaron activos.

**Conclusión de la exploración:** detener `udisks2` fue funcionalmente viable en los ensayos descritos, pero las lecturas de memoria disponible no permitieron cuantificar un ahorro neto reproducible. La PSS documenta memoria atribuida proporcionalmente al proceso, no una estimación garantizada del beneficio por desactivación.

## 6. Validación funcional con configuración reducida

Se mantuvo `bluetooth.service` activo y `udisks2.service` inactivo en ambas Raspberry. El ahorro energético Wi-Fi siguió desactivado. Se verificó lo siguiente:

| Prueba | Evidencia | Resultado |
|---|---|---|
| TLS 1.3 `X25519` | Piloto de 2 conexiones | 2/2 verificadas |
| TLS 1.3 `X25519MLKEM768` | Piloto de 2 conexiones | 2/2 verificadas |
| ML-KEM-768 local, cliente ARMv7 | KeyGen / Encaps / Decaps | Correcto |
| ML-KEM-768 local, servidor ARMv6 | KeyGen / Encaps / Decaps | Correcto |
| ML-KEM-768 cliente-servidor sobre TCP, puerto 5000 | Coincidencia del hash SHA-256 del secreto compartido | Correcto |
| Servicios esenciales | SSH y NetworkManager | Permanecieron activos |

ML-KEM-768 produjo claves públicas de **1184 bytes**, encapsulados de **1088 bytes** y secretos compartidos de **32 bytes**, coincidentes entre implementaciones locales; el intercambio TCP produjo el mismo hash de secreto en cliente y servidor. Esta demostración TCP confirma el establecimiento del secreto en ese ensayo, **no** autenticación completa del canal, protección integral frente a ataques de intermediario ni seguridad equivalente a TLS.

Los registros de estado reducido capturados el 07/11/2026 a las 00:49 incluyeron `udisks2=inactive`, `bluetooth=active`, `ssh=active`, `NetworkManager=active`, Wi-Fi power save OFF, `throttled=0x0` y OpenSSL 3.5.7 en ambas placas.

## 7. Incidencias y exclusiones

1. El primer script shell utilizó la variable especial de Bash `GROUPS` y generó CSV sin observaciones; se corrigió a `TLS_GROUPS`.
2. Una serie Bluetooth OFF de 100 registros se ejecutó cuando el servidor TLS no estaba levantado y produjo **0/100 conexiones verificadas**. **Se excluye** del análisis de rendimiento; sus CSV y logs se conservan para trazabilidad.
3. Se efectuaron pilotos de cuatro conexiones para validar instrumentación y compatibilidad; se conservan diferenciados de las series completas.
4. No se eliminaron los valores de latencia extrema de las series válidas.
5. No se deben mezclar automáticamente las series históricas de TLS con los nuevos experimentos de medición de recursos: herramientas, condiciones y definición de duración pueden ser distintas.

## 8. Archivos y respaldo

Respaldo local en Windows (verificado mediante salida de PowerShell):

```text
C:\Users\Jorge\Downloads\PQC-Resultados\Optimizacion_20261107\
├── cliente\system\
│   ├── baseline_pqc-client_20261106_223131.txt
│   ├── estado_reducido_pqc-client_20261107_004929.txt
│   └── tls_resources\
│       ├── bt_on_*.csv
│       ├── bt_off_*.csv
│       └── error_*.log
├── servidor\system\
│   ├── baseline_pqc-server_20261106_223142.txt
│   ├── estado_reducido_pqc-server_20261107_004933.txt
│   └── server_resources\
│       ├── bt_on_run1_before.txt / bt_on_run1_after.txt
│       ├── bt_off_run1_before.txt / bt_off_run1_after.txt
│       └── udisks2_test_20261107_003002.txt
└── scripts\
    └── benchmark_tls_resources.sh
```

CSV de series completas ON–OFF–OFF–ON (cliente):

```text
bt_on_20261106_232855_104189058.csv
bt_off_20261106_233955_112735109.csv
bt_off_20261106_234410_346256452.csv
bt_on_20261106_235931_640355639.csv
```

CSV de la evaluación adicional del servidor (cliente):

```text
bt_on_20261107_001013_219441284.csv
bt_off_20261107_001356_966094756.csv
```

**Exclusión principal:** `bt_off_20261106_233407_469793476.csv` (100 conexiones fallidas al no estar levantado el servidor TLS).

Para conservar reproducibilidad, versionar el script y este informe; revisar selectivamente qué CSV y qué registros de error deben almacenarse en Git. Comprobar el contenido de los registros antes de publicarlos y no versionar claves privadas, contraseñas ni material sensible.

## 9. Conclusiones y límites

1. La funcionalidad TLS clásica e híbrida, ML-KEM local y el intercambio ML-KEM por TCP **se mantuvo** en las pruebas realizadas con `udisks2` detenido en ambas placas.
2. La desactivación de Bluetooth **no mostró una reducción consistente** de CPU, RSS ni tiempo total de las conexiones TLS a lo largo de las series estudiadas.
3. Detener `udisks2` elimina un proceso con consumo medible de RSS/PSS, pero **no se demostró** un aumento reproducible de `MemAvailable` en cliente ni servidor.
4. Las métricas TLS de duración y recursos se refieren a procesos completos y contienen costes adicionales a la criptografía; el tiempo de CPU del servidor se midió agregado por lote y no separado por grupo.
5. La ausencia de mejora medible **no implica** que el método PQC sea inviable ni que la reducción de servicios carezca de valor operativo; simplemente limita las afirmaciones que pueden defenderse con estos datos.

**Estado de la fase:** evaluación exploratoria de reducción de servicios documentada y verificación funcional completada. No se recomienda anunciar un porcentaje de aceleración o ahorro de RAM como resultado demostrado. Para una publicación formal se requeriría, si el objetivo del artículo lo exige, un diseño adicional con más sesiones independientes, control de condiciones y métricas de proceso/sistema sincronizadas.

## 10. Pendientes administrativos de cierre

- Confirmar la integridad de los CSV descargados y generar, a partir de los archivos originales, un resumen reproducible de estadísticas y metadatos.
- Conservar la configuración final elegida o restaurar conscientemente servicios detenidos; el comando `systemctl stop` no implica persistencia tras reinicio.
- Incorporar este registro al repositorio y enlazarlo desde `README.md` o `docs/metodologia.md`, dejando separado el material exploratorio de cualquier análisis final para artículo.
- Registrar el `git commit` de cierre una vez revisados y seleccionados los archivos que se incluirán.
