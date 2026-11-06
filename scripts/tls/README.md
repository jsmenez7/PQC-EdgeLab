# TLS 1.3 clásico e híbrido con OpenSSL

## Proyecto PQC-EdgeLab

Implementación experimental de TLS 1.3 entre dos
Raspberry Pi utilizando OpenSSL 3.5.7.

Se evalúan dos grupos de intercambio de claves:

- X25519: criptografía clásica.
- X25519MLKEM768: intercambio híbrido clásico y
  poscuántico.

## 1. Arquitectura del experimento

Cliente:
- Raspberry Pi Zero 2 W
- Hostname: pqc-client

Servidor:
- Raspberry Pi Zero W Rev 1.1
- Hostname: pqc-server

Ambos utilizan Raspberry Pi OS Lite.

## 2. Verificar OpenSSL

Ejecutar en ambas Raspberry:

```bash
openssl version
```

Comprobar que los grupos están disponibles:

```bash
openssl list -tls1_3 -tls-groups
```

Se requiere soporte para X25519 y X25519MLKEM768.

## 3. Preparar certificado de laboratorio

En pqc-server:

```bash
mkdir -p ~/pqc-tls
cd ~/pqc-tls
```

Generar un certificado autofirmado:

```bash
openssl req -x509 -newkey rsa:2048 -keyout server-key.pem -out server-cert.pem -sha256 -days 30 -nodes -subj "/CN=pqc-server" -addext "subjectAltName=DNS:pqc-server.local"
```

La clave privada no debe subirse al repositorio.

Para verificar la identidad del servidor en las
pruebas posteriores, copiar el certificado público
al cliente.

En pqc-client:

```bash
mkdir -p ~/pqc-tls
scp pqc@pqc-server.local:~/pqc-tls/server-cert.pem ~/pqc-tls/
```

## 4. Experimento A: TLS clásico

En pqc-server:

```bash
cd ~/pqc-tls
openssl s_server -accept 4433 -cert server-cert.pem -key server-key.pem -tls1_3 -groups X25519 -www
```

En pqc-client:

```bash
openssl s_client -connect pqc-server.local:4433 -servername pqc-server.local -tls1_3 -groups X25519 -CAfile ~/pqc-tls/server-cert.pem -verify_hostname pqc-server.local -verify_return_error -brief
```

Verificar que se negoció TLS 1.3 con X25519.

Detener el servidor mediante Ctrl+C.

## 5. Experimento B: TLS híbrido

En pqc-server:

```bash
cd ~/pqc-tls
openssl s_server -accept 4433 -cert server-cert.pem -key server-key.pem -tls1_3 -groups X25519MLKEM768 -www
```

En pqc-client:

```bash
openssl s_client -connect pqc-server.local:4433 -servername pqc-server.local -tls1_3 -groups X25519MLKEM768 -CAfile ~/pqc-tls/server-cert.pem -verify_hostname pqc-server.local -verify_return_error -brief
```

Resultado esperado:

- Conexión TLS 1.3 establecida.
- Grupo negociado: X25519MLKEM768.
- Certificado verificado correctamente.

## 6. Consideraciones

OpenSSL 3.5 incorpora soporte nativo para ML-KEM
y grupos híbridos TLS 1.3.

El certificado RSA utilizado proporciona
autenticación clásica. El establecimiento híbrido
de claves no implica autenticación poscuántica.

Este experimento demuestra interoperabilidad
criptográfica; no constituye todavía un benchmark
formal de rendimiento.

Los tiempos, consumo de RAM y CPU se evaluarán
posteriormente mediante pruebas repetidas.
```

