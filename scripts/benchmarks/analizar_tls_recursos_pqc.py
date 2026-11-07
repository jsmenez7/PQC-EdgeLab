#!/usr/bin/env python3
"""PQC-EdgeLab: auditoria reproducible de seis series TLS de recursos.

Requiere solo Python 3 (biblioteca estandar). No modifica los CSV originales.
Uso en Windows: py analizar_tls_recursos_pqc.py
O bien: py analizar_tls_recursos_pqc.py --input RUTA --output RUTA
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

COLUMNS = (
    "repetition", "group", "user_s", "system_s", "elapsed_s",
    "maxrss_kib", "exit_code", "verified",
)
GROUPS = ("X25519", "X25519MLKEM768")
# Archivo, ID, condicion, clase esperada (complete / pilot / invalid).
MANIFEST = (
    ("baseline_bt_on_20261106_224611.csv", "ERR-01", "ON", "invalid"),
    ("bt_on_20261106_225145_399416964.csv", "ERR-02", "ON", "invalid"),
    ("bt_on_20261106_225545_773427193.csv", "PIL-01", "ON", "pilot"),
    ("bt_on_20261106_232855_104189058.csv", "BT-ON-1", "ON", "complete"),
    ("bt_off_20261106_233407_469793476.csv", "ERR-03", "OFF", "invalid"),
    ("bt_off_20261106_233955_112735109.csv", "BT-OFF-1", "OFF", "complete"),
    ("bt_off_20261106_234410_346256452.csv", "BT-OFF-2", "OFF", "complete"),
    ("bt_on_20261106_235931_640355639.csv", "BT-ON-2", "ON", "complete"),
    ("bt_on_20261107_001013_219441284.csv", "SRV-ON-1", "ON", "complete"),
    ("bt_off_20261107_001356_966094756.csv", "SRV-OFF-1", "OFF", "complete"),
    ("bt_on_20261107_003511_985287305.csv", "PIL-02", "ON", "pilot"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    errors = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                return [], ["Sin cabecera"]
            if list(reader.fieldnames) != list(COLUMNS):
                errors.append("Cabecera distinta de las 8 columnas esperadas")
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        return [], [f"Error leyendo CSV: {exc}"]
    return rows, errors


def parse_valid(row: dict[str, str]) -> tuple[dict | None, str]:
    if None in row or any(row.get(c) is None for c in COLUMNS):
        return None, "Numero de columnas incorrecto"
    if row.get("group") not in GROUPS:
        return None, "Grupo TLS no reconocido"
    if row.get("exit_code", "").strip() != "0" or row.get("verified", "").strip() != "1":
        return None, "Conexion no verificada o exit_code distinto de cero"
    try:
        repetition = int(row["repetition"])
        user_s = float(row["user_s"])
        system_s = float(row["system_s"])
        elapsed_s = float(row["elapsed_s"])
        rss = int(row["maxrss_kib"])
    except (ValueError, TypeError):
        return None, "Metrica ausente o no numerica"
    if (repetition <= 0 or rss <= 0 or elapsed_s <= 0 or
            not all(math.isfinite(v) and v >= 0 for v in (user_s, system_s, elapsed_s))):
        return None, "Metrica fuera de rango o no finita"
    return {
        "repetition": repetition,
        "group": row["group"],
        "cpu_ms": 1000 * (user_s + system_s),
        "elapsed_ms": 1000 * elapsed_s,
        "maxrss_kib": rss,
    }, ""


def mean(numbers):
    return statistics.mean(numbers) if numbers else float("nan")


def median(numbers):
    return statistics.median(numbers) if numbers else float("nan")


def p95_nearest_rank(numbers):
    sorted_values = sorted(numbers)
    return sorted_values[math.ceil(0.95 * len(sorted_values)) - 1]


def metrics(data):
    elapsed = [r["elapsed_ms"] for r in data]
    cpu = [r["cpu_ms"] for r in data]
    rss = [r["maxrss_kib"] for r in data]
    return {
        "n": len(data),
        "elapsed_mean_ms": round(mean(elapsed), 3),
        "elapsed_median_ms": round(median(elapsed), 3),
        "elapsed_p95_ms": round(p95_nearest_rank(elapsed), 3),
        "elapsed_max_ms": round(max(elapsed), 3),
        "elapsed_over_500ms": sum(x > 500 for x in elapsed),
        "cpu_mean_ms": round(mean(cpu), 3),
        "cpu_median_ms": round(median(cpu), 3),
        "rss_mean_kib": round(mean(rss), 3),
        "rss_median_kib": round(median(rss), 3),
        "rss_max_kib": max(rss),
    }


def write_table(path: Path, data: list[dict], columns: tuple[str, ...]):
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)


def main() -> int:
    default_input = (Path.home() / "Downloads" / "PQC-Resultados" /
                     "Optimizacion_20261107" / "cliente" / "system" / "tls_resources")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=default_input,
                        help="Carpeta con los CSV originales respaldados en Windows")
    parser.add_argument("--output", type=Path, default=None,
                        help="Carpeta para informes (por defecto Optimizacion_20261107/analisis)")
    args = parser.parse_args()
    root = args.input.expanduser().resolve()
    dest = (args.output.expanduser().resolve() if args.output else root.parents[2] / "analisis")
    if not root.is_dir():
        print(f"ERROR: no existe la carpeta de entrada: {root}", file=sys.stderr)
        return 2
    dest.mkdir(parents=True, exist_ok=True)

    audits = []
    per_series = []
    pooled = defaultdict(list)
    file_hashes = []
    accepted = 0
    for filename, label, state, category in MANIFEST:
        source = root / filename
        if not source.exists():
            audits.append({"id": label, "filename": filename, "condition": state,
                           "expected_class": category, "classification": "MISSING",
                           "rows": 0, "verified": 0, "classic": 0, "hybrid": 0,
                           "sha256": "", "notes": "Archivo no encontrado"})
            continue
        file_hash = sha256(source)
        file_hashes.append(f"{file_hash}  {filename}")
        rows, header_errors = read_csv(source)
        valid = []
        issues = Counter()
        repeats = defaultdict(list)
        for row in rows:
            observation, reason = parse_valid(row)
            if observation is None:
                issues[reason] += 1
            else:
                valid.append(observation)
                repeats[observation["group"]].append(observation["repetition"])
        counts = Counter(r["group"] for r in valid)
        complete_valid = (
            category == "complete" and not header_errors and len(rows) == 100 and
            len(valid) == 100 and all(counts[g] == 50 for g in GROUPS) and
            all(sorted(repeats[g]) == list(range(1, 51)) for g in GROUPS)
        )
        pilot_valid = (
            category == "pilot" and not header_errors and len(rows) == 4 and
            len(valid) == 4 and all(counts[g] == 2 for g in GROUPS) and
            all(sorted(repeats[g]) == [1, 2] for g in GROUPS)
        )
        if category == "invalid":
            classification = "EXCLUDED_PREVIOUS_INCIDENT"
        elif complete_valid:
            classification = "ACCEPTED_COMPLETE"
            accepted += 1
        elif pilot_valid:
            classification = "ACCEPTED_PILOT_NOT_STATISTICS"
        else:
            classification = "REVIEW_REQUIRED"
        note_parts = header_errors + [f"{reason}: {n}" for reason, n in issues.items()]
        if classification == "REVIEW_REQUIRED":
            note_parts.append("No cumple recuentos, verificacion, columnas o repeticiones esperadas")
        audits.append({
            "id": label, "filename": filename, "condition": state,
            "expected_class": category, "classification": classification,
            "rows": len(rows), "verified": len(valid),
            "classic": counts[GROUPS[0]], "hybrid": counts[GROUPS[1]],
            "sha256": file_hash, "notes": " | ".join(note_parts),
        })
        if not complete_valid:
            continue
        for group in GROUPS:
            part = [r for r in valid if r["group"] == group]
            per_series.append({"series": label, "condition": state,
                               "filename": filename, "group": group, **metrics(part)})
            pooled[(state, group)].extend(part)

    audit_cols = ("id", "filename", "condition", "expected_class", "classification",
                  "rows", "verified", "classic", "hybrid", "sha256", "notes")
    stat_cols = ("n", "elapsed_mean_ms", "elapsed_median_ms", "elapsed_p95_ms",
                 "elapsed_max_ms", "elapsed_over_500ms", "cpu_mean_ms",
                 "cpu_median_ms", "rss_mean_kib", "rss_median_kib", "rss_max_kib")
    write_table(dest / "auditoria_archivos.csv", audits, audit_cols)
    write_table(dest / "resumen_por_serie.csv", per_series,
                ("series", "condition", "filename", "group", *stat_cols))
    conditions = []
    for state in ("ON", "OFF"):
        for group in GROUPS:
            data = pooled.get((state, group), [])
            if data:
                series_count = sum(r["condition"] == state and r["group"] == group
                                   for r in per_series)
                conditions.append({"condition": state, "group": group,
                                   "series_count": series_count, **metrics(data)})
    write_table(dest / "resumen_por_condicion.csv", conditions,
                ("condition", "group", "series_count", *stat_cols))
    (dest / "sha256_archivos_originales.txt").write_text(
        "\n".join(file_hashes) + "\n", encoding="utf-8"
    )
    lines = [
        "PQC-EdgeLab | Analisis reproducible de recursos TLS",
        f"Entrada: {root}",
        f"Salida: {dest}",
        f"Series completas aceptadas: {accepted}/6",
        f"Conexiones en series completas: {accepted * 100}",
        "",
        "AUDITORIA (pilotos e incidencias no se agregan):",
    ]
    for a in audits:
        lines.append(f"  {a['id']:10} {a['classification']:30} "
                     f"filas={a['rows']:3} verificadas={a['verified']:3}")
    lines.extend(["", "RESUMEN POR SERIE (medidas del cliente):"])
    for entry in per_series:
        lines.append(
            f"  {entry['series']:10} {entry['group']:15} n={entry['n']:2} "
            f"media={entry['elapsed_mean_ms']:7.2f} ms "
            f"mediana={entry['elapsed_median_ms']:7.2f} ms "
            f"p95={entry['elapsed_p95_ms']:7.2f} ms "
            f">500ms={entry['elapsed_over_500ms']:2} "
            f"CPU_media={entry['cpu_mean_ms']:6.2f} ms "
            f"RSS_mediana={entry['rss_median_kib']:.0f} KiB"
        )
    lines.extend(["", "RESUMEN AGRUPADO (solo descriptivo):"])
    for entry in conditions:
        lines.append(
            f"  {entry['condition']:3} {entry['group']:15} "
            f"series={entry['series_count']} n={entry['n']:3} "
            f"media={entry['elapsed_mean_ms']:.2f} ms "
            f"mediana={entry['elapsed_median_ms']:.2f} ms "
            f"CPU_media={entry['cpu_mean_ms']:.2f} ms "
            f"RSS_mediana={entry['rss_median_kib']:.0f} KiB"
        )
    lines.extend([
        "", "LIMITACIONES:",
        "- Cada conexion pertenece a una sesion experimental; no son 600 sesiones independientes.",
        "- elapsed_s mide todo el comando cliente/OpenSSL + red, NO el handshake aislado.",
        "- CPU de GNU time incluye la ejecucion instrumentada; no es porcentaje CPU ni CPU del servidor.",
        "- maxrss_kib representa pico RSS de la ejecucion, NO RAM total liberada del sistema.",
        "- Resolucion de /usr/bin/time limitada (centésimas de segundo en estos CSV).",
        "- p95 calculado por rango mas cercano: observacion en posicion ceil(0.95*n).",
        "- Diferencias ON/OFF no permiten atribucion causal sin control adicional.",
        "- Hashes SHA-256 permiten identificar los archivos originales; no prueban por si solos su origen.",
        "- Las mediciones del servidor se analizan aparte: NO se mezclan con CPU del cliente.",
        "", "Archivos de salida: auditoria_archivos.csv, resumen_por_serie.csv,",
        "resumen_por_condicion.csv, sha256_archivos_originales.txt, informe_analisis.txt.",
    ])
    text_report = "\n".join(lines) + "\n"
    (dest / "informe_analisis.txt").write_text(text_report, encoding="utf-8-sig")
    print(text_report)
    if accepted != 6:
        print("ATENCION: faltan series o no superaron la auditoria; revise auditoria_archivos.csv.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
