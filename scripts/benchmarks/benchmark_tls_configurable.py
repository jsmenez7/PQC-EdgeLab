#!/usr/bin/env python3
"""PQC-EdgeLab: benchmark de procesos TLS 1.3 (no tiempo aislado de handshake)."""

import argparse
import csv
import os
import random
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

GROUPS = ("X25519", "X25519MLKEM768")
CIPHERSUITE = "TLS_AES_256_GCM_SHA384"
FIELDS = (
    "order", "group", "repetition", "timestamp_utc", "elapsed_ms",
    "success", "exit_code", "status",
)


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("debe ser al menos 1")
    return number


def nonnegative_int(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("no puede ser negativo")
    return number


def build_parser():
    parser = argparse.ArgumentParser(
        description="Benchmark TLS 1.3 clasico/hibrido de proceso completo"
    )
    parser.add_argument("--repetitions", type=positive_int, default=100,
                        help="mediciones por grupo (predeterminado: 100)")
    parser.add_argument("--server", default=os.environ.get(
        "PQC_SERVER", "pqc-server.local:4433"))
    parser.add_argument("--server-name", default="pqc-server.local",
                        help="identidad DNS usada para SNI y verificar el certificado")
    parser.add_argument("--cert", type=Path,
                        default=Path.home() / "pqc-tls/server-cert.pem")
    parser.add_argument("--seed", type=int, default=20261106)
    parser.add_argument("--timeout", type=positive_int, default=15)
    parser.add_argument("--warmups", type=nonnegative_int, default=2)
    parser.add_argument("--output", type=Path,
                        help="ruta CSV nueva; nunca sobrescribe un archivo existente")
    return parser


def measure(group, args):
    command = [
        "openssl", "s_client",
        "-connect", args.server,
        "-servername", args.server_name,
        "-tls1_3", "-groups", group,
        "-ciphersuites", CIPHERSUITE,
        "-CAfile", str(args.cert),
        "-verify_hostname", args.server_name,
        "-verify_return_error", "-brief",
    ]
    request = f"GET / HTTP/1.0\r\nHost: {args.server_name}\r\n\r\n"
    start = time.perf_counter_ns()
    try:
        result = subprocess.run(
            command, input=request, text=True, capture_output=True,
            timeout=args.timeout,
        )
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
        output = result.stdout + result.stderr
        basic_ok = all((
            "CONNECTION ESTABLISHED" in output,
            "Protocol version: TLSv1.3" in output,
            f"Ciphersuite: {CIPHERSUITE}" in output,
            "Verification: OK" in output,
            f"Verified peername: {args.server_name}" in output,
        ))
        group_ok = (
            "Peer Temp Key: X25519," in output if group == "X25519"
            else "Negotiated TLS1.3 group: X25519MLKEM768" in output
        )
        success = result.returncode == 0 and basic_ok and group_ok
        return elapsed_ms, success, result.returncode, (
            "OK" if success else "VERIFY_OR_CONNECTION_ERROR"
        )
    except subprocess.TimeoutExpired:
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
        return elapsed_ms, False, -1, "TIMEOUT"
    except OSError as error:
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
        return elapsed_ms, False, -2, f"OS_ERROR:{type(error).__name__}"


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.cert = args.cert.expanduser()
    if not args.cert.is_file():
        parser.error(f"certificado no encontrado: {args.cert}")

    if args.output is None:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tls_{run_id}_{time.time_ns()}.csv"
        args.output = Path.home() / "PQC-EdgeLab/results/raw" / filename
    args.output = args.output.expanduser()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        parser.error(f"el CSV ya existe; no se sobrescribe: {args.output}")

    print("=== PQC-EdgeLab: TLS configurable ===", flush=True)
    print(f"Servidor: {args.server}")
    print(f"Repeticiones por grupo: {args.repetitions}")
    print(f"Semilla: {args.seed} | Calentamientos por grupo: {args.warmups}")
    print("Metrica: duracion total del proceso s_client (NO handshake aislado)")

    for group in GROUPS:
        for i in range(args.warmups):
            _, ok, code, status = measure(group, args)
            if not ok:
                raise SystemExit(
                    f"Fallo en calentamiento {group} #{i + 1}: {status}, exit={code}"
                )

    rng = random.Random(args.seed)
    sequence = []
    for _ in range(args.repetitions):
        pair = list(GROUPS)
        rng.shuffle(pair)
        sequence.extend(pair)

    counts = {group: 0 for group in GROUPS}
    measurements = {group: [] for group in GROUPS}
    failures = {group: 0 for group in GROUPS}

    with args.output.open("x", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        file.flush()
        for order, group in enumerate(sequence, 1):
            counts[group] += 1
            timestamp = datetime.now(timezone.utc).isoformat()
            elapsed_ms, success, code, status = measure(group, args)
            writer.writerow({
                "order": order,
                "group": group,
                "repetition": counts[group],
                "timestamp_utc": timestamp,
                "elapsed_ms": f"{elapsed_ms:.3f}",
                "success": success,
                "exit_code": code,
                "status": status,
            })
            file.flush()
            if success:
                measurements[group].append(elapsed_ms)
            else:
                failures[group] += 1
            print(f"{order:03d} {group} #{counts[group]}: "
                  f"{elapsed_ms:.3f} ms {'OK' if success else status}",
                  flush=True)

    print("\n=== RESUMEN ===")
    for group in GROUPS:
        values = measurements[group]
        print(f"{group}: {len(values)}/{args.repetitions} exitosas, "
              f"{failures[group]} fallidas")
        if values:
            print(f"  Media: {statistics.mean(values):.3f} ms")
            print(f"  Mediana: {statistics.median(values):.3f} ms")
    print(f"CSV guardado en: {args.output}")
    if any(failures.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
