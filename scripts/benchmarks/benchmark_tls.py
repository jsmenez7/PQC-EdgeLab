
import csv
import random
import statistics
import subprocess
import time
from pathlib import Path

SERVER = "192.168.100.173:4433"
SERVER_NAME = "pqc-server.local"
CERT = str(Path.home() / "pqc-tls/server-cert.pem")

GROUPS = ["X25519", "X25519MLKEM768"]
REPETITIONS = 10
TIMEOUT = 15

OUTPUT = (
    Path.home()
    / "PQC-EdgeLab/results/raw/pilot_tls.csv"
)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)


def measure(group):
    command = [
        "openssl", "s_client",
        "-connect", SERVER,
        "-servername", SERVER_NAME,
        "-tls1_3",
        "-groups", group,
        "-ciphersuites", "TLS_AES_256_GCM_SHA384",
        "-CAfile", CERT,
        "-verify_hostname", SERVER_NAME,
        "-verify_return_error",
        "-brief",
    ]

    request = (
        "GET / HTTP/1.0\r\n"
        f"Host: {SERVER_NAME}\r\n"
        "\r\n"
    )

    start = time.perf_counter_ns()

    try:
        result = subprocess.run(
            command,
            input=request,
            text=True,
            capture_output=True,
            timeout=TIMEOUT,
        )

        elapsed = (time.perf_counter_ns() - start) / 1e6
        output = result.stdout + result.stderr

        verified = "Verification: OK" in output
        protocol = "Protocol version: TLSv1.3" in output

        if group == "X25519":
            negotiated = "Peer Temp Key: X25519," in output
        else:
            negotiated = (
                "Negotiated TLS1.3 group: X25519MLKEM768"
                in output
            )

        success = (
            result.returncode == 0
            and verified
            and protocol
            and negotiated
        )

        return elapsed, success, result.returncode

    except subprocess.TimeoutExpired:
        elapsed = (time.perf_counter_ns() - start) / 1e6
        return elapsed, False, -1


print("=== PQC-EdgeLab: TLS Benchmark Pilot ===")
print("Repeticiones por grupo:", REPETITIONS)

# Calentamiento: no se incluye en los resultados.
for group in GROUPS:
    measure(group)
    measure(group)

# Orden aleatorizado y reproducible.
sequence = GROUPS * REPETITIONS
random.Random(20261106).shuffle(sequence)

records = []
counts = {group: 0 for group in GROUPS}

for group in sequence:
    counts[group] += 1
    elapsed, success, code = measure(group)

    row = {
        "group": group,
        "repetition": counts[group],
        "elapsed_ms": round(elapsed, 3),
        "success": success,
        "exit_code": code,
    }

    records.append(row)

    print(
        group,
        f"#{counts[group]}",
        f"{elapsed:.3f} ms",
        "OK" if success else f"ERROR ({code})"
    )

with OUTPUT.open("w", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "group",
            "repetition",
            "elapsed_ms",
            "success",
            "exit_code",
        ],
    )
    writer.writeheader()
    writer.writerows(records)

print("\n=== RESUMEN ===")

for group in GROUPS:
    values = [
        r["elapsed_ms"]
        for r in records
        if r["group"] == group and r["success"]
    ]

    print(f"\n{group}")
    print(f"Exitosas: {len(values)}/{REPETITIONS}")

    if values:
        print(f"Media: {statistics.mean(values):.3f} ms")
        print(f"Mediana: {statistics.median(values):.3f} ms")
        print(f"Minimo: {min(values):.3f} ms")
        print(f"Maximo: {max(values):.3f} ms")

print("\nCSV guardado en:", OUTPUT)
