import os
import socket
import struct
import hashlib
import oqs

SERVER_IP = os.environ.get("PQC_SERVER_HOST", "pqc-server.local")
PORT = int(os.environ.get("PQC_MLKEM_PORT", "5000"))
ALGORITHM = "ML-KEM-768"


def send_data(sock, data):
    sock.sendall(struct.pack("!I", len(data)))
    sock.sendall(data)


def recv_exact(sock, size):
    data = b""

    while len(data) < size:
        chunk = sock.recv(size - len(data))

        if not chunk:
            raise ConnectionError(
                "Conexion cerrada inesperadamente"
            )

        data += chunk

    return data


def recv_data(sock):
    length = struct.unpack("!I", recv_exact(sock, 4))[0]
    return recv_exact(sock, length)


print("=== CLIENTE ML-KEM-768 ===")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:

    print("Conectando con servidor...")

    client.connect((SERVER_IP, PORT))

    print("Conectado")

    public_key = recv_data(client)

    print(
        "Clave publica recibida:",
        len(public_key),
        "bytes"
    )

    with oqs.KeyEncapsulation(ALGORITHM) as kem:

        ciphertext, shared_secret = kem.encap_secret(
            public_key
        )

        print(
            "Ciphertext generado:",
            len(ciphertext),
            "bytes"
        )

        send_data(client, ciphertext)

        print("Ciphertext enviado")

        digest = hashlib.sha256(
            shared_secret
        ).hexdigest()

        print("SHA-256 del secreto:")
        print(digest)

print("Cliente finalizado")

