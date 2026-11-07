# TLS 1.3 Benchmarks

This directory contains scripts for measuring the
performance of classical and hybrid TLS 1.3
connections on resource-constrained Raspberry Pi devices.

## Experimental configurations

- Classical TLS: X25519.
- Hybrid TLS: X25519MLKEM768.
- Cryptographic library: OpenSSL 3.5.7.
- TLS version: 1.3.
- Cipher suite: TLS_AES_256_GCM_SHA384.

## Hardware

- Client: Raspberry Pi Zero 2 W (ARMv7).
- Server: Raspberry Pi Zero W (ARMv6).

## Pilot experiment

The initial pilot includes 10 measurements per
cryptographic group.

The script measures total client process execution
time, including TLS connection establishment,
request transmission and termination.

These results do not represent pure cryptographic
execution time or isolated TLS handshake latency.

## Execution

On the server, start the TLS test service according
to scripts/tls/README.md.

On the client, execute:

```bash
python3 scripts/benchmarks/benchmark_tls.py
```

The script writes its output to:

`results/raw/pilot_tls.csv`

## Experimental status

- Initial pilot: completed.
- Formal benchmarks: pending.
- CPU and RAM profiling: pending.
- Statistical analysis: pending.


## Configurable TLS Benchmark

The script `benchmark_tls_configurable.py` allows researchers
to evaluate classical and hybrid TLS 1.3 connections without
modifying the source code.

### Available parameters

| Parameter | Description | Default |
|---|---|---|
| `--repetitions` | Measurements per group | 100 |
| `--server` | TLS server hostname and port | pqc-server.local:4433 |
| `--server-name` | TLS server identity for SNI and certificate verification | pqc-server.local |
| `--cert` | Trusted server certificate | ~/pqc-tls/server-cert.pem |
| `--seed` | Randomization seed | 20261106 |
| `--timeout` | Connection timeout in seconds | 15 |
| `--warmups` | Warm-up connections per group | 2 |
| `--output` | Output CSV path | Automatically generated |

### Example executions

Small validation:

```bash
python3 scripts/benchmarks/benchmark_tls_configurable.py --repetitions 2
```

Standard experiment:

```bash
python3 scripts/benchmarks/benchmark_tls_configurable.py --repetitions 100
```

Custom configuration:

```bash
python3 scripts/benchmarks/benchmark_tls_configurable.py \
  --repetitions 200 \
  --server pqc-server.local:4433 \
  --seed 12345 \
  --warmups 5
```

### Measurement scope

The benchmark measures the total execution time of the
OpenSSL client process, including process startup, TLS
connection establishment, network communication and
termination.

It does not isolate cryptographic execution time or
TLS handshake latency.

Each measurement is recorded in a CSV file. The script
generates unique output filenames to preserve previous
results.

### Validation

The configurable benchmark was functionally validated
on a Raspberry Pi Zero 2 W client communicating with a
Raspberry Pi Zero W server.

Validation included 2 and 100 repetitions per TLS group.

Both X25519 and X25519MLKEM768 completed their
respective tests successfully.

CPU, memory and isolated handshake measurements remain
pending.

