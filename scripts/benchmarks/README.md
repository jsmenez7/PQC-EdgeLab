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
