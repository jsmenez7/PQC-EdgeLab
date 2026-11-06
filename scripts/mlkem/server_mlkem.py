import socket
import struct
import hashlib
import oqs

HOST = "0.0.0.0"
PORT = 5000
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


print("=== SERVIDOR ML-KEM-768 ===")

with oqs.KeyEncapsulation(ALGORITHM) as kem:

    public_key = kem.generate_keypair()

    print(
        "Clave publica generada:",
        len(public_key),
        "bytes"
    )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:

        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        server.bind((HOST, PORT))
        server.listen(1)

        print(f"Esperando cliente en puerto {PORT}...")

        connection, address = server.accept()

        with connection:

            print("Cliente conectado:", address)

            send_data(connection, public_key)

            print("Clave publica enviada")

            ciphertext = recv_data(connection)

            print(
                "Ciphertext recibido:",
                len(ciphertext),
                "bytes"
            )

            shared_secret = kem.decap_secret(ciphertext)

            digest = hashlib.sha256(
                shared_secret
            ).hexdigest()

            print("Secreto desencapsulado correctamente")
            print("SHA-256 del secreto:")
            print(digest)

print("Servidor finalizado")

