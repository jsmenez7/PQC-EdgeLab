#!/usr/bin/env bash
set -euo pipefail

# PQC-EdgeLab
# Instalacion experimental de ML-KEM-768
# Raspberry Pi Zero W / Zero 2 W

LIBOQS_VERSION="0.16.0"
PYTHON_OQS_VERSION="0.16.0.1"

ARCH=$(uname -m)
SOURCE_DIR="$HOME/liboqs"
INSTALL_DIR="$HOME/_oqs"
VENV_DIR="$HOME/pqc-venv"

echo "=================================="
echo "     PQC-EdgeLab - Instalador"
echo "=================================="
echo "Arquitectura: $ARCH"

EXTRA_CMAKE=()
JOBS=2

case "$ARCH" in
    armv6l)
        JOBS=1
        EXTRA_CMAKE+=(
            -DOQS_PERMIT_UNSUPPORTED_ARCHITECTURE=ON
        )
        echo "ADVERTENCIA: ARMv6 no esta soportado oficialmente."
        echo "Esta configuracion es SOLO para investigacion."
        ;;
    armv7l|aarch64)
        echo "Arquitectura detectada: $ARCH"
        ;;
    *)
        echo "Arquitectura no validada: $ARCH"
        exit 1
        ;;
esac

echo "[1/6] Instalando dependencias..."
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    libssl-dev \
    git \
    python3-venv

echo "[2/6] Descargando liboqs..."
if [ ! -d "$SOURCE_DIR/.git" ]; then
    git clone --depth 1 \
        --branch "$LIBOQS_VERSION" \
        https://github.com/open-quantum-safe/liboqs.git \
        "$SOURCE_DIR"
fi

echo "[3/6] Configurando ML-KEM-768..."
cmake -S "$SOURCE_DIR" \
    -B "$SOURCE_DIR/build" \
    -GNinja \
    -DBUILD_SHARED_LIBS=ON \
    -DOQS_MINIMAL_BUILD=KEM_ml_kem_768 \
    -DOQS_BUILD_ONLY_LIB=ON \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR" \
    "${EXTRA_CMAKE[@]}"

echo "[4/6] Compilando liboqs..."
cmake --build "$SOURCE_DIR/build" \
    --parallel "$JOBS"

cmake --install "$SOURCE_DIR/build"

echo "[5/6] Preparando Python..."
python3 -m venv "$VENV_DIR"

"$VENV_DIR/bin/python" -m pip install \
    --upgrade pip

"$VENV_DIR/bin/python" -m pip install \
    "liboqs-python==$PYTHON_OQS_VERSION"

echo "[6/6] Verificando instalacion..."
export OQS_INSTALL_PATH="$INSTALL_DIR"

"$VENV_DIR/bin/python" -c '
import oqs

assert "ML-KEM-768" in oqs.get_enabled_kem_mechanisms()

print("liboqs:", oqs.oqs_version())
print("liboqs-python:", oqs.oqs_python_version())
print("KEM:", oqs.get_enabled_kem_mechanisms())
print("INSTALACION CORRECTA")
'

echo "=================================="
echo "       Instalacion finalizada"
echo "=================================="
echo "Para activar el entorno:"
echo "source ~/pqc-venv/bin/activate"
echo 'export OQS_INSTALL_PATH=$HOME/_oqs'

