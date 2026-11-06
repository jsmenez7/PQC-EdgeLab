# PQC-EdgeLab

### Experimental Evaluation of Post-Quantum and Hybrid Cryptography on Resource-Constrained Raspberry Pi Devices

PQC-EdgeLab is an experimental research project focused on implementing and evaluating post-quantum cryptography (PQC) and hybrid TLS 1.3 communications on resource-constrained embedded devices.

The project investigates the feasibility and computational cost of deploying ML-KEM-768 and hybrid key establishment mechanisms on legacy Raspberry Pi platforms.

## 1. Research Objectives

The main objectives are:

- Implement classical and hybrid TLS 1.3 communications using OpenSSL.
- Implement ML-KEM-768 using Python and liboqs.
- Validate post-quantum key establishment between physical Raspberry Pi devices.
- Measure execution time, CPU utilization, memory consumption, and communication overhead.
- Investigate the impact of resource optimization on cryptographic performance.
- Develop reproducible experiments for future scientific analysis.

## 2. Experimental Hardware

| Device | Architecture | Role |
|---|---|---|
| Raspberry Pi Zero W Rev 1.1 | ARMv6, 32-bit | Server |
| Raspberry Pi Zero 2 W Rev 1.0 | ARMv7, 32-bit OS | Client |
| Raspberry Pi 4 Model B | To be verified | Additional experimental platform |

The two Raspberry Pi Zero devices have 512 MB of physical RAM.

The Raspberry Pi 4 is available but has not yet been integrated into the experiments.

## 3. Software Environment

The initial experiments were successfully conducted using:

| Component | Version |
|---|---|
| Operating System | Raspberry Pi OS Lite / Raspbian 13 (Trixie) |
| Python | 3.13.5 |
| OpenSSL | 3.5.7 |
| liboqs | 0.16.0 |
| liboqs-python | 0.16.0.1 |
| GCC | 14.2.0 |

The software environment is being prepared for reproducible installation and testing.

## 4. Cryptographic Implementations

### 4.1 Native OpenSSL Implementation

Two TLS 1.3 key establishment configurations have been successfully tested:

**Classical TLS 1.3**
- Key exchange group: X25519
- Protocol: TLS 1.3

**Hybrid Post-Quantum TLS 1.3**
- Key exchange group: X25519MLKEM768
- Classical component: X25519
- Post-quantum component: ML-KEM-768
- Protocol: TLS 1.3

Both configurations successfully established connections between the Raspberry Pi Zero 2 W client and the Raspberry Pi Zero W server.

OpenSSL 3.5.7 provides native support for the hybrid TLS group.

### 4.2 Python and liboqs Implementation

A separate experimental implementation uses:

- Python 3.13.5
- liboqs-python 0.16.0.1
- liboqs 0.16.0
- ML-KEM-768

The implementation performs:

1. Key pair generation.
2. Public key transmission.
3. Secret encapsulation.
4. Ciphertext transmission.
5. Secret decapsulation.
6. Shared secret verification.

The client and server successfully derived identical shared secrets over a TCP connection.

ML-KEM-768 parameters:

| Parameter | Size |
|---|---|
| Public key | 1184 bytes |
| Ciphertext | 1088 bytes |
| Shared secret | 32 bytes |

This Python implementation demonstrates ML-KEM-based key establishment. It does not implement TLS 1.3 or a complete authenticated hybrid protocol.

## 5. Repository Structure

```text
PQC-EdgeLab/
├── README.md
├── .gitignore
├── docs/
│   └── metodologia.md
├── scripts/
│   ├── mlkem/
│   │   ├── server_mlkem.py
│   │   └── client_mlkem.py
│   └── tls/
│       └── README.md
├── setup/
│   └── setup_raspberry.sh
└── results/ (planned)
```

## 6. Installation

An automated installation script has been prepared for Raspberry Pi Zero W and Raspberry Pi Zero 2 W.

From the repository root:

```bash
bash setup/setup_raspberry.sh
```

The script is designed to:

- Install required dependencies.
- Download liboqs 0.16.0.
- Compile a minimal ML-KEM-768 configuration.
- Create a Python virtual environment.
- Install liboqs-python 0.16.0.1.
- Verify the installation.

The automated script still requires validation after a clean system installation.

## 7. Running the Python Experiment

On both Raspberry Pi devices, activate the environment:

```bash
source ~/pqc-venv/bin/activate
export OQS_INSTALL_PATH=$HOME/_oqs
```

Start the server:

```bash
python scripts/mlkem/server_mlkem.py
```

Then start the client on the other device:

```bash
python scripts/mlkem/client_mlkem.py
```

Note: The current client script uses a laboratory-specific server IP address, which must be updated to match the network configuration.

For TLS experiments, see:

[scripts/tls/README.md](scripts/tls/README.md)

## 8. Experimental Status

### Completed in the initial laboratory setup

- [x] Raspberry Pi OS Lite configuration.
- [x] SSH connectivity and local network communication.
- [x] Classical TLS 1.3 handshake using X25519.
- [x] Hybrid TLS 1.3 handshake using X25519MLKEM768.
- [x] liboqs and liboqs-python installation.
- [x] Local ML-KEM-768 validation.
- [x] ML-KEM-768 client-server key establishment.
- [x] Shared secret verification.

### Planned

- [ ] Reproduce the experiments after clean installation.
- [ ] Benchmark ML-KEM key generation, encapsulation, and decapsulation.
- [ ] Benchmark classical and hybrid TLS handshakes.
- [ ] Measure CPU and memory utilization.
- [ ] Analyze network communication overhead.
- [ ] Evaluate resource optimization.
- [ ] Conduct comparative statistical analysis.
- [ ] Evaluate the Raspberry Pi 4 platform.

## 9. Experimental Methodology

The project follows an experimental proof-of-concept approach.

Initial experiments validate the feasibility of classical and post-quantum cryptographic operations on constrained hardware.

Subsequent performance evaluation will use controlled experiments and repeated measurements to compare computational and communication costs.

The experimental methodology and reproducibility procedures will be documented in:

[docs/metodologia.md](docs/metodologia.md)

## 10. Security Considerations

The Raspberry Pi Zero W uses ARMv6, which is not officially supported by liboqs 0.16.0.

The experimental compilation requires:

```bash
-DOQS_PERMIT_UNSUPPORTED_ARCHITECTURE=ON
```

This configuration is intended exclusively for research and testing. It must not be considered production-secure.

Additional limitations:

- The custom Python TCP demonstration does not authenticate the communicating parties.
- The initial TLS experiments used a self-signed RSA certificate.
- Hybrid key establishment does not imply post-quantum authentication.
- Private keys, credentials, and shared secrets must never be committed to the repository.

## 11. References

- NIST FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard.
- Open Quantum Safe: https://openquantumsafe.org/
- liboqs: https://github.com/open-quantum-safe/liboqs
- liboqs-python: https://github.com/open-quantum-safe/liboqs-python
- OpenSSL: https://www.openssl.org/

## 12. Research Status

This repository is under active experimental development.

Initial cryptographic functionality has been validated on physical Raspberry Pi hardware. Performance measurements, resource optimization, and further reproducibility testing are pending.
