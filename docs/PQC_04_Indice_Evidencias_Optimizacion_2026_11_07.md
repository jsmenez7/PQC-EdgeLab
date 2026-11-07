# PQC-EdgeLab — Índice de evidencias de optimización (Registro 04)

**Fecha de corte:** 7 de noviembre de 2026 (Ecuador, UTC−05:00)  
**Equipos:** `pqc-client` (Raspberry Pi Zero 2 W, ARMv7l) y `pqc-server` (Raspberry Pi Zero W, ARMv6l)  
**Estado:** catálogo de evidencias y auditoría inicial; análisis estadístico definitivo pendiente de ejecutar sobre los CSV originales.  
**Documento asociado:** [Registro técnico de optimización](PQC_04_Optimizacion_Recursos_Raspberry_2026_11_07.md).

## 1. Propósito y alcance

Este índice identifica los archivos producidos al evaluar la detención temporal de `bluetooth.service` y `udisks2.service`, y **separa explícitamente las ejecuciones válidas, las pruebas piloto y las incidencias**. Las clasificaciones proceden de las salidas de terminal y comprobaciones de `exit_code`/`verified` registradas durante el proyecto. No equivalen a una nueva auditoría independiente de los bytes de todos los archivos originales.

**Rutas locales de respaldo en Windows:**

```text
C:\Users\Jorge\Downloads\PQC-Resultados\Optimizacion_20261107\
├── cliente\system\
│   ├── baseline_pqc-client_20261106_223131.txt
│   ├── estado_reducido_pqc-client_20261107_004929.txt
│   ├── bt_off_ram_20261106_235353.txt
│   └── tls_resources\
├── servidor\system\
│   ├── baseline_pqc-server_20261106_223142.txt
│   ├── estado_reducido_pqc-server_20261107_004933.txt
│   ├── bt_off_ram_20261106_235357.txt
│   └── server_resources\
└── scripts\
    └── benchmark_tls_resources.sh
```

Las rutas de los archivos individuales se expresan relativas a `cliente/system/tls_resources/` o `servidor/system/server_resources/`, según se indica en cada sección. No se presupone que todo este respaldo esté subido a GitHub.

## 2. Registro de series TLS completas — usar para análisis de recursos

En cada serie: 50 conexiones `X25519` y 50 conexiones `X25519MLKEM768`, con grupos alternados dentro del ensayo. El cliente utilizó `scripts/benchmarks/benchmark_tls_resources.sh`. Las seis series fueron reportadas como **100/100 verificadas** mediante `exit_code=0` y `verified=1`.

| ID | Fecha/hora de inicio | Bluetooth | CSV del cliente | Verificadas | Uso previsto |
|---|---|---|---|---:|---|
| BT-ON-1 | 2026-11-06 23:28 | ON | `bt_on_20261106_232855_104189058.csv` | 100/100 | Serie exploratoria ON–OFF–OFF–ON |
| BT-OFF-1 | 2026-11-06 23:39 | OFF | `bt_off_20261106_233955_112735109.csv` | 100/100 | Serie exploratoria ON–OFF–OFF–ON |
| BT-OFF-2 | 2026-11-06 23:44 | OFF | `bt_off_20261106_234410_346256452.csv` | 100/100 | Serie exploratoria ON–OFF–OFF–ON |
| BT-ON-2 | 2026-11-06 23:59 | ON | `bt_on_20261106_235931_640355639.csv` | 100/100 | Serie exploratoria ON–OFF–OFF–ON |
| SRV-ON-1 | 2026-11-07 00:10 | ON | `bt_on_20261107_001013_219441284.csv` | 100/100 | Instrumentación simultánea del servidor |
| SRV-OFF-1 | 2026-11-07 00:13 | OFF | `bt_off_20261107_001356_966094756.csv` | 100/100 | Instrumentación simultánea del servidor |

**Total de series completas auditadas en terminal: 6 × 100 = 600 conexiones válidas**, correspondientes a 300 con Bluetooth ON y 300 con Bluetooth OFF. Este total **no incluye** pilotos, pruebas individuales, ni anteriores experimentos TLS con otra instrumentación.

Los pares `SRV-ON-1` y `SRV-OFF-1` también tienen lecturas del proceso `openssl s_server` en el equipo ARMv6, descritas más abajo. No mezclar su CPU del servidor (diferencia de ticks en un intervalo) con el CPU del cliente reportado por GNU `time`.

## 3. Pilotos, intentos inválidos y archivos excluidos

Todos estos archivos se conservan para trazabilidad, pero **no se incorporan a las seis series completas**.

| Archivo (`cliente/system/tls_resources/`) | Observaciones | Clasificación | Motivo / uso |
|---|---:|---|---|
| `baseline_bt_on_20261106_224611.csv` | 0 | Inválido | Primera copia del bucle quedó incompleta; solo cabecera |
| `bt_on_20261106_225145_399416964.csv` | 0 | Inválido | Variable especial `GROUPS` impidió ejecutar el bucle; solo cabecera |
| `bt_on_20261106_225545_773427193.csv` | 4/4 verificadas | Piloto válido | Verificación de funcionamiento tras cambiar `GROUPS` por `TLS_GROUPS` |
| `bt_off_20261106_233407_469793476.csv` | 0/100 verificadas | Inválido | El servidor TLS no estaba iniciado; conservar con `error_*.log` |
| `bt_on_20261107_003511_985287305.csv` | 4/4 verificadas | Piloto válido | TLS clásico e híbrido con `udisks2` temporalmente detenido |

**Pilotos válidos: 8 conexiones en dos archivos (4 + 4)**, analizados únicamente como comprobaciones funcionales/instrumentales. Los dos archivos de cabecera vacía y el ensayo con 100 conexiones sin verificación se excluyen de todas las estadísticas de rendimiento. Los numerosos `error_*.log` pertenecen al ensayo inválido y se conservan sin confundirse con incidencias de las seis series válidas.

También se practicaron conexiones TLS individuales durante la preparación de GNU `time`; sus archivos `X25519_recursos.txt`, `X25519MLKEM768_recursos.txt` y logs asociados son evidencia piloto y **no pertenecen a las 600 observaciones**.

## 4. Medición de recursos del servidor (ARMv6)

Carpeta `servidor/system/server_resources/`:

| Conjunto | Archivos | Qué demuestra |
|---|---|---|
| Línea base auxiliar | `bt_on_before.txt` | Estado puntual del servidor antes del ensayo instrumentado |
| CPU/RAM Bluetooth ON | `bt_on_run1_before.txt`, `bt_on_run1_after.txt` | PID 4109; 848→1656 ticks, `CLK_TCK=100` ⇒ **8,08 s** de CPU acumulada en el intervalo |
| CPU/RAM Bluetooth OFF | `bt_off_run1_before.txt`, `bt_off_run1_after.txt` | Mismo PID; 1656→2466 ticks ⇒ **8,10 s** de CPU acumulada en el intervalo |
| Exploración `udisks2` | `udisks2_test_20261107_003002.txt` | Servicio y PSS/RSS, `MemAvailable` ON→OFF, continuidad de SSH/red/TLS |

**Limitación:** las ventanas ON y OFF tienen duraciones diferentes, y los ticks representan CPU total del proceso en cada ventana, no el coste aislado del algoritmo ni el CPU de cada conexión. No se demostró ahorro significativo de CPU por desactivar Bluetooth.

## 5. Capturas del estado del sistema y configuración reducida

| Equipo | Archivo de línea base | Estado con Bluetooth OFF | Estado reducido final |
|---|---|---|---|
| Cliente | `baseline_pqc-client_20261106_223131.txt` | `bt_off_ram_20261106_235353.txt` | `estado_reducido_pqc-client_20261107_004929.txt` |
| Servidor | `baseline_pqc-server_20261106_223142.txt` | `bt_off_ram_20261106_235357.txt` | `estado_reducido_pqc-server_20261107_004933.txt` |

En el estado reducido final documentado: `udisks2=inactive`, `bluetooth=active`, `ssh=active`, `NetworkManager=active`, ahorro energético Wi-Fi desactivado y `throttled=0x0` en ambas placas. Se verificaron ML-KEM-768 localmente, intercambio ML-KEM mediante TCP y conexiones TLS clásicas/híbridas durante las pruebas funcionales. Los registros de texto no sustituyen los logs de todas esas operaciones.

La memoria `MemAvailable` varió entre lecturas al detener/restaurar servicios; **no hay un ahorro neto reproducible de memoria confirmado**. Las métricas RSS/PSS de `udisksd` tampoco son una predicción directa del aumento de RAM disponible.

## 6. Diccionario de datos del CSV de recursos TLS

| Campo | Interpretación |
|---|---|
| `repetition` | Índice de la pareja de conexiones en una serie (1–50 en series completas) |
| `group` | `X25519` o `X25519MLKEM768` |
| `user_s`, `system_s` | Tiempo de CPU de usuario y sistema, en segundos, medido por GNU `time` |
| `elapsed_s` | Duración total del comando, en segundos; **no** handshake aislado |
| `maxrss_kib` | Pico RSS reportado por GNU `time`, en KiB, correspondiente a la ejecución instrumentada |
| `exit_code` | Código de retorno de la ejecución instrumentada |
| `verified` | Bandera de validación TLS y grupo esperado (1 = verificado; 0 = no verificado) |

**Criterio operativo de observación válida:** `exit_code == 0` **y** `verified == 1`. Además, antes de analizar una serie, comprobar 100 filas de datos, 50 por grupo, las ocho columnas requeridas, valores numéricos y ausencia de datos faltantes. Un `EXIT_CODE=0` del *script* por sí solo no acredita que todas las conexiones sean correctas.

## 7. Comprobación local reproducible desde PowerShell

La siguiente comprobación recorre **solo** las seis series completas respaldadas en Windows. Muestra recuentos, sin alterar los archivos. Si la ruta de respaldo cambia, ajustarla antes de ejecutar.

```powershell
$root = "$HOME\Downloads\PQC-Resultados\Optimizacion_20261107\cliente\system\tls_resources"
$files = @(
    'bt_on_20261106_232855_104189058.csv',
    'bt_off_20261106_233955_112735109.csv',
    'bt_off_20261106_234410_346256452.csv',
    'bt_on_20261106_235931_640355639.csv',
    'bt_on_20261107_001013_219441284.csv',
    'bt_off_20261107_001356_966094756.csv'
)

foreach ($name in $files) {
    $path = Join-Path $root $name
    $rows = @(Import-Csv -LiteralPath $path)
    $valid = @($rows | Where-Object {
        $_.exit_code -eq '0' -and $_.verified -eq '1'
    })
    $classic = @($valid | Where-Object { $_.group -eq 'X25519' })
    $hybrid = @($valid | Where-Object { $_.group -eq 'X25519MLKEM768' })
    "{0}: filas={1}; verificadas={2}; X25519={3}; hibrido={4}" -f `
       $name, $rows.Count, $valid.Count, $classic.Count, $hybrid.Count
}
```

Para una auditoría científica integral aún faltaría incluir hashes SHA-256 de los archivos originales, metadatos de versiones, distribución completa de métricas, valores extremos y análisis de sensibilidad entre sesiones.

## 8. Criterios para subir evidencias a GitHub

1. **Versionar:** este índice, el [informe técnico](PQC_04_Optimizacion_Recursos_Raspberry_2026_11_07.md), y `scripts/benchmarks/benchmark_tls_resources.sh` (si aún no está subido).
2. **Revisar antes de versionar:** CSV válidos completos y, opcionalmente, pilotos; conservar nombres sin alteraciones. Preferir una carpeta documentada de datos (p. ej., `results/system/tls_resources/`) si el repositorio y `.gitignore` lo permiten.
3. **Conservar en respaldo, no mezclar en estadísticas:** CSV inválido y logs de error. Si se publican con fines de trazabilidad, ponerlos bajo una carpeta `invalid/` claramente identificada, revisados para evitar filtración de datos sensibles.
4. **No subir:** claves privadas TLS, secretos, contraseñas, rutas sensibles adicionales, ni certificados privados. Revisar el contenido antes de cualquier publicación.

## 9. Conclusión del registro

Las seis series TLS completas reúnen **600 conexiones verificadas según las auditorías de terminal**; los pilotos válidos son adicionales. Se confirmó la compatibilidad funcional de la configuración sin `udisks2` en las operaciones comprobadas, pero **no se demostró** una aceleración estable ni un ahorro reproducible de memoria del sistema al detener Bluetooth o `udisks2`. Esta separación entre evidencia funcional, observaciones de recursos y conclusiones causales se debe mantener en cualquier informe al profesor o manuscrito para conferencia.
