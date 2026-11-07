# Instalación y configuración de Raspberry Pi

## Proyecto PQC-EdgeLab

**Objetivo:** Documentar el procedimiento de instalación y configuración del sistema operativo de las Raspberry Pi utilizadas para evaluar criptografía poscuántica e híbrida en dispositivos con recursos limitados.

Este procedimiento permite reproducir el entorno base utilizado en los experimentos de TLS 1.3, OpenSSL y ML-KEM-768 mediante Python y liboqs.

---

## 1. Hardware utilizado

| Dispositivo | Función | Arquitectura |
|---|---|---|
| Raspberry Pi Zero 2 W Rev 1.0 | Cliente (`pqc-client`) | ARM Cortex-A53 |
| Raspberry Pi Zero W Rev 1.1 | Servidor (`pqc-server`) | ARM1176JZF-S |
| Raspberry Pi 4 Model B | Plataforma adicional prevista | ARM Cortex-A72 |

**Accesorios necesarios:**

- Dos tarjetas microSD.
- Adaptador microSD a SD o lector USB.
- Fuentes de alimentación de 5 V adecuadas para cada Raspberry.
- Computadora con Windows 11.
- Conexión Wi-Fi de 2.4 GHz.
- Raspberry Pi Imager.

## 2. Instalación de Raspberry Pi Imager

1. Acceder a https://www.raspberrypi.com/software/
2. Descargar Raspberry Pi Imager para Windows.
3. Ejecutar el instalador.
4. Aceptar la instalación de los controladores oficiales cuando Windows lo solicite.
5. Abrir Raspberry Pi Imager.

## 3. Selección del sistema operativo

Para la Raspberry Pi Zero 2 W (cliente):

- **Dispositivo:** Raspberry Pi Zero 2 W.
- **Sistema operativo:** Raspberry Pi OS (other) → Raspberry Pi OS Lite (32-bit).
- **Almacenamiento:** tarjeta microSD del cliente.

Para la Raspberry Pi Zero W (servidor):

- **Dispositivo:** Raspberry Pi Zero.
- **Sistema operativo:** Raspberry Pi OS (other) → Raspberry Pi OS Lite (32-bit).
- **Almacenamiento:** tarjeta microSD del servidor.

Se seleccionó Raspberry Pi OS Lite porque no incluye un entorno gráfico de escritorio, lo que evita servicios gráficos innecesarios.

Se mantuvo la edición de 32 bits por compatibilidad con ambas placas, especialmente con la Raspberry Pi Zero W original, cuyo procesador utiliza ARMv6.

**Precaución:** la escritura de la imagen elimina los datos existentes en la tarjeta seleccionada.

## 4. Personalización del sistema

Durante la configuración de Raspberry Pi Imager se establecieron los siguientes parámetros:

| Parámetro | Cliente | Servidor |
|---|---|---|
| Hostname | `pqc-client` | `pqc-server` |
| Usuario | `pqc` | `pqc` |
| Contraseña | Privada | Privada |
| Red Wi-Fi | Misma red local | Misma red local |
| Frecuencia Wi-Fi | 2.4 GHz | 2.4 GHz |
| País WLAN | EC | EC |
| Zona horaria | America/Guayaquil | America/Guayaquil |
| SSH | Activado | Activado |
| Autenticación SSH | Contraseña | Contraseña |
| Raspberry Pi Connect | Desactivado | Desactivado |

Las contraseñas se almacenan de forma segura y no se incluyen en el repositorio.

Se habilitó SSH para administrar las placas de manera remota, sin utilizar monitor ni teclado conectados a las Raspberry.

Raspberry Pi Connect se dejó desactivado porque no era necesario para los experimentos.

## 5. Escritura de las tarjetas microSD

1. Revisar los parámetros configurados.
2. Seleccionar la tarjeta microSD correcta.
3. Pulsar **Escribir**.
4. Confirmar el borrado de la tarjeta.
5. Esperar a que termine la escritura.
6. Completar la verificación de la imagen.
7. Expulsar la microSD de forma segura.

Este procedimiento se realiza individualmente para las dos placas.


## 6. Primer arranque

1. Insertar la microSD correspondiente en cada Raspberry Pi.
2. Conectar la alimentación al puerto `PWR IN`.
3. Esperar a que el sistema operativo complete su primer arranque.
4. Comprobar que la Raspberry se haya conectado a la red Wi-Fi configurada.

### 6.1. Tiempo de espera inicial

Durante el primer arranque, Raspberry Pi OS realiza tareas de
inicialización y configuración que pueden requerir más tiempo
que un arranque habitual.

Se recomienda esperar inicialmente entre 2 y 5 minutos.
En dispositivos de menor rendimiento, como la Raspberry Pi
Zero W, puede ser conveniente esperar hasta aproximadamente
10 minutos antes de iniciar un diagnóstico más detallado.

Este intervalo es una recomendación operativa, no un tiempo
de arranque garantizado.

Durante este período pueden presentarse temporalmente
mensajes como:

- `Could not resolve hostname`: el nombre del equipo aún no
  se resuelve en la red local.
- `Connection refused`: el equipo responde en la red, pero
  el servicio SSH todavía no acepta conexiones.

Estos mensajes no implican necesariamente un fallo en la
instalación.

Se recomienda esperar aproximadamente 60 segundos antes
de repetir el intento de conexión.

Si después de unos 10 minutos el equipo continúa inaccesible,
se debe comprobar la alimentación, la conexión Wi-Fi, la
configuración SSH y la tarjeta microSD.

### 6.2. Identificación de dispositivos

Para evitar confusiones, ambas placas y sus tarjetas microSD
deben identificarse físicamente:

- CLIENT: Raspberry Pi Zero 2 W (`pqc-client`).
- SERVER: Raspberry Pi Zero W (`pqc-server`).

Una vez completado el arranque, continuar con la conexión
remota mediante SSH.

## 7. Conexión por SSH

Desde PowerShell de Windows, conectarse al cliente mediante:

`ssh pqc@pqc-client.local`

Para conectarse al servidor:

`ssh pqc@pqc-server.local`

Durante la primera conexión SSH se solicita confirmar la identidad del dispositivo mediante su huella digital.

Una vez comprobada la identidad del equipo, se acepta la conexión y se introduce la contraseña del usuario `pqc`.

Si el nombre `.local` no se resuelve, puede utilizarse la dirección IP asignada por el router.

**Nota:** las direcciones IP pueden cambiar al reinstalar el sistema operativo. No deben considerarse valores permanentes del experimento.


### 7.1. Advertencia SSH después de una reinstalación

Cuando se reinstala Raspberry Pi OS, normalmente se generan
nuevas claves de identificación SSH.

Si Windows conserva las claves antiguas, puede aparecer:

`WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!`

Antes de aceptar una clave nueva, verificar que corresponde
al dispositivo reinstalado.

Para eliminar la identificación SSH antigua del cliente,
ejecutar en PowerShell:

```powershell
ssh-keygen -R pqc-client.local
```

Para el servidor:

```powershell
ssh-keygen -R pqc-server.local
```

Después intentar nuevamente la conexión:

```powershell
ssh pqc@pqc-client.local
```

O, para el servidor:

```powershell
ssh pqc@pqc-server.local
```

Se debe comprobar la nueva huella digital SSH mediante
un medio confiable antes de aceptar la conexión.

La opción `yes` permite registrar la nueva identidad
del equipo después de verificarla.

Finalmente, introducir la contraseña del usuario `pqc`.

La eliminación de entradas antiguas de `known_hosts`
no elimina archivos ni configuraciones de las Raspberry Pi.



## 8. Verificación del sistema

Una vez establecida la conexión SSH, se debe verificar
el hardware, el sistema operativo y los recursos
disponibles de cada Raspberry Pi.

Para facilitar la reproducibilidad del experimento,
se utiliza un único bloque de comandos que recopila
la información necesaria.

### 8.1. Ejecución de los comandos de verificación

Ejecutar el siguiente bloque en las terminales SSH de
`pqc-client` y `pqc-server`:

```bash
echo "===== HARDWARE ====="
cat /proc/device-tree/model; echo

echo "===== SISTEMA OPERATIVO ====="
cat /etc/os-release

echo "===== ARQUITECTURA ====="
uname -m

echo "===== MEMORIA RAM ====="
free -h

echo "===== OPENSSL ====="
openssl version

echo "===== PYTHON ====="
python3 --version

echo "===== DIRECCION IP ====="
hostname -I

echo "===== ALMACENAMIENTO ====="
df -h /
```

Este bloque permite obtener la configuración
general del dispositivo sin ejecutar manualmente
cada comando por separado.

### 8.2. Descripción de los comandos

| Comando | Función |
|---|---|
| `cat /proc/device-tree/model; echo` | Identifica el modelo y la revisión de la Raspberry Pi. |
| `cat /etc/os-release` | Muestra la distribución y versión del sistema operativo. |
| `uname -m` | Identifica la arquitectura reportada por el sistema. |
| `free -h` | Muestra la memoria RAM y swap disponible, utilizada y libre. |
| `openssl version` | Consulta la versión de OpenSSL instalada. |
| `python3 --version` | Identifica la versión de Python 3. |
| `hostname -I` | Obtiene las direcciones IP asignadas al dispositivo. |
| `df -h /` | Muestra la capacidad, espacio utilizado y disponible de la partición raíz. |
| `echo` | Imprime encabezados para organizar la salida de las verificaciones. |

### 8.3. Registro de los resultados

Los resultados obtenidos deben registrarse por
separado para cada Raspberry Pi, indicando:

- Modelo y revisión del dispositivo.
- Arquitectura del sistema.
- Versión del sistema operativo.
- Versión de OpenSSL.
- Versión de Python.
- Memoria RAM total y disponible.
- Memoria swap utilizada.
- Dirección IP local.
- Almacenamiento disponible.

Estos datos permiten caracterizar las plataformas
experimentales y establecer las condiciones iniciales
antes de instalar las bibliotecas criptográficas.

### 8.4. Consideraciones experimentales

La disponibilidad de memoria RAM puede variar
según los procesos activos y el tiempo transcurrido
desde el arranque del sistema.

Por esta razón, las verificaciones iniciales
deben registrarse antes de instalar `liboqs` y
`liboqs-python`.

Estas mediciones caracterizan el entorno base.
No constituyen por sí solas benchmarks del
rendimiento criptográfico.

Las versiones de software y los resultados
deben comprobarse nuevamente después de cada
reinstalación del sistema operativo.


## 9. Verificación de conectividad

Con las dos Raspberry conectadas a la misma red, realizar pruebas de comunicación ICMP.

Desde el cliente, ejecutar:

`ping -c 4 <IP_DEL_SERVIDOR>`

Desde el servidor:

`ping -c 4 <IP_DEL_CLIENTE>`

Reemplazar los valores entre corchetes angulares por las direcciones IP reales.

Registrar la pérdida de paquetes y los tiempos de respuesta.

La prueba inicial del laboratorio consiguió comunicación bidireccional con 0 % de pérdida de paquetes en cuatro solicitudes por dirección.


## 10. Instalación del entorno criptográfico

Una vez completadas las verificaciones del sistema operativo,
la arquitectura y la conectividad entre ambas Raspberry Pi,
se procede a instalar el entorno experimental de criptografía
poscuántica.

El proyecto utiliza:

- liboqs 0.16.0.
- liboqs-python 0.16.0.1.
- Python 3.13.5.
- OpenSSL 3.5.7.
- Algoritmo ML-KEM-768.

Para facilitar la reproducción del experimento, se desarrolló
un script Bash que automatiza la instalación y compilación de
las bibliotecas necesarias.

### 10.1. Descarga del repositorio

Desde una computadora con Windows 11:

1. Acceder al repositorio privado `PQC-EdgeLab` en GitHub.
2. Seleccionar **Code → Download ZIP**.
3. Extraer el archivo ZIP descargado.
4. Identificar la carpeta que contiene el código fuente.

En el equipo utilizado para este experimento, la carpeta
extraída se encuentra en:

`C:\Users\<USUARIO>\Downloads\PQC-EdgeLab-main\PQC-EdgeLab-main`

La ruta puede variar dependiendo del nombre del usuario,
la ubicación de descarga y el procedimiento de extracción.

Para evitar utilizar rutas personales, los comandos siguientes
emplean la variable `$HOME` de PowerShell.

### 10.2. Verificación de la carpeta descargada

Abrir PowerShell en Windows y definir la ubicación del
repositorio:

```powershell
$repoDir = "$HOME\Downloads\PQC-EdgeLab-main\PQC-EdgeLab-main"
```

Comprobar que el script de instalación esté disponible:

```powershell
Test-Path "$repoDir\setup\setup_raspberry.sh"
```

Resultado esperado:

```text
True
```

Si aparece `False`, verificar la ubicación de la carpeta
extraída y modificar `$repoDir` según corresponda.

### 10.3. Transferencia mediante SCP

Para evitar configurar credenciales de GitHub en las
Raspberry Pi, los archivos se transfieren desde Windows
utilizando SCP sobre SSH.

**Transferencia al cliente (`pqc-client`):**

Ejecutar en PowerShell de Windows:

```powershell
scp -r "$repoDir" "pqc@pqc-client.local:~/"
```

**Transferencia al servidor (`pqc-server`):**

```powershell
scp -r "$repoDir" "pqc@pqc-server.local:~/"
```

Durante la transferencia se solicitará la contraseña SSH
del usuario `pqc` de la Raspberry correspondiente.

La carpeta transferida conservará inicialmente el nombre
`PQC-EdgeLab-main`.

SCP permite transferir los archivos de forma cifrada,
sin necesidad de instalar Git en las Raspberry Pi
únicamente para obtener el repositorio.

### 10.4. Organización del repositorio

Conectarse mediante SSH a la Raspberry correspondiente.

Para el cliente:

```powershell
ssh pqc@pqc-client.local
```

Para el servidor:

```powershell
ssh pqc@pqc-server.local
```

Los siguientes comandos se ejecutan dentro de la terminal
Linux de cada Raspberry, no en PowerShell de Windows.

En una instalación limpia, renombrar la carpeta transferida:

```bash
mv ~/PQC-EdgeLab-main ~/PQC-EdgeLab
```

Si ya existe una carpeta llamada `PQC-EdgeLab`, revisar
su contenido antes de ejecutar el comando anterior para
evitar crear directorios anidados.

Comprobar la estructura del proyecto:

```bash
ls -la ~/PQC-EdgeLab
ls -lh ~/PQC-EdgeLab/setup/
```

La estructura esperada es:

```text
PQC-EdgeLab/
├── README.md
├── .gitignore
├── docs/
├── scripts/
│   ├── mlkem/
│   └── tls/
└── setup/
    └── setup_raspberry.sh
```

### 10.5. Verificación del script de instalación

Antes de ejecutar el instalador, comprobar su sintaxis:

```bash
bash -n ~/PQC-EdgeLab/setup/setup_raspberry.sh
```

Si el comando no muestra errores, Bash no ha detectado
problemas de sintaxis en el archivo.

Esta comprobación no garantiza por sí sola el
funcionamiento de todas las operaciones del instalador.

### 10.6. Instalación automatizada

El script `setup_raspberry.sh` identifica la arquitectura
del dispositivo y configura la compilación según el
hardware detectado.

**En `pqc-client`:**

```bash
set -o pipefail
bash ~/PQC-EdgeLab/setup/setup_raspberry.sh 2>&1 | tee ~/pqc-setup-client.log
```

**En `pqc-server`:**

```bash
set -o pipefail
bash ~/PQC-EdgeLab/setup/setup_raspberry.sh 2>&1 | tee ~/pqc-setup-server.log
```

El instalador realiza las siguientes operaciones:

1. Detectar la arquitectura del procesador.
2. Instalar dependencias de compilación.
3. Descargar liboqs 0.16.0.
4. Configurar una compilación mínima de ML-KEM-768.
5. Compilar e instalar la biblioteca compartida.
6. Crear un entorno virtual Python.
7. Instalar liboqs-python 0.16.0.1.
8. Verificar las versiones y los algoritmos habilitados.

Para reducir la demanda de memoria durante la
compilación, el script utiliza:

- ARMv7: dos procesos de compilación.
- ARMv6: un proceso de compilación.

La Raspberry Pi Zero W utiliza ARMv6, una arquitectura
no soportada oficialmente por liboqs 0.16.0.

Por este motivo, el instalador habilita experimentalmente:

```text
OQS_PERMIT_UNSUPPORTED_ARCHITECTURE=ON
```

Esta configuración se utiliza exclusivamente con fines
de investigación y no garantiza las propiedades de
seguridad necesarias para un despliegue de producción.

La instalación puede tardar varios minutos,
especialmente en la Raspberry Pi Zero W.

Los registros `pqc-setup-client.log` y
`pqc-setup-server.log` permiten conservar la salida
original de cada instalación.

### 10.7. Verificación de la instalación

Una vez finalizada la ejecución, el instalador debe
mostrar las versiones de las bibliotecas y los
algoritmos disponibles.

Resultado esperado:

```text
liboqs: 0.16.0
liboqs-python: 0.16.0.1
KEM: ('ML-KEM-768',)
INSTALACION CORRECTA
```

La instalación se considera satisfactoria cuando
el proceso termina sin errores y presenta el
resultado esperado.

### 10.8. Activación del entorno Python

Para utilizar las bibliotecas criptográficas en
una sesión SSH, ejecutar:

```bash
source ~/pqc-venv/bin/activate
export OQS_INSTALL_PATH=$HOME/_oqs
```

Comprobar que Python pueda acceder a ML-KEM-768:

```bash
python -c "import oqs; print(oqs.get_enabled_kem_mechanisms())"
```

Resultado esperado:

```text
('ML-KEM-768',)
```

La activación del entorno virtual y la variable
`OQS_INSTALL_PATH` deben configurarse nuevamente
al iniciar una nueva sesión de terminal, salvo
que se haya preparado una configuración persistente.

### 10.9. Validación funcional de ML-KEM-768

La correcta instalación de una biblioteca no garantiza,
por sí sola, el funcionamiento del algoritmo.

Por ello, se realiza una prueba funcional de:

- Generación de claves (KeyGen).
- Encapsulación (Encaps).
- Desencapsulación (Decaps).
- Comparación del secreto compartido.

Ejecutar con el entorno Python activado:

```bash
python - <<'PY'
import oqs

algorithm = "ML-KEM-768"

with oqs.KeyEncapsulation(algorithm) as receiver:
    public_key = receiver.generate_keypair()

    with oqs.KeyEncapsulation(algorithm) as sender:
        ciphertext, secret_sender = sender.encap_secret(
            public_key
        )

    secret_receiver = receiver.decap_secret(ciphertext)

    print("Algoritmo:", algorithm)
    print("Clave publica:", len(public_key), "bytes")
    print("Ciphertext:", len(ciphertext), "bytes")
    print("Secreto compartido:", len(secret_receiver), "bytes")
    print("Coinciden:", secret_sender == secret_receiver)
PY
```

Resultado esperado:

```text
Algoritmo: ML-KEM-768
Clave publica: 1184 bytes
Ciphertext: 1088 bytes
Secreto compartido: 32 bytes
Coinciden: True
```

Esta prueba valida localmente la operación del mecanismo
de encapsulación de claves.

No constituye una medición de rendimiento ni demuestra
por sí sola la comunicación entre las dos Raspberry Pi.


### 10.10. Estado de reproducibilidad

El procedimiento de instalación automatizada fue ejecutado
satisfactoriamente en las dos plataformas experimentales,
utilizando instalaciones limpias de Raspberry Pi OS Lite
(32-bit).

| Verificación | Raspberry Pi Zero 2 W | Raspberry Pi Zero W |
|---|---|---|
| Arquitectura | armv7l | armv6l |
| Sistema operativo | Raspbian 13 (Trixie) | Raspbian 13 (Trixie) |
| liboqs | 0.16.0 | 0.16.0 |
| liboqs-python | 0.16.0.1 | 0.16.0.1 |
| Algoritmo habilitado | ML-KEM-768 | ML-KEM-768 |
| Instalación automatizada | Correcta | Correcta |
| KeyGen, Encaps y Decaps | Correctos | Correctos |
| Coincidencia de secretos | True | True |

La validación funcional confirmó los siguientes tamaños:

- Clave pública: 1184 bytes.
- Ciphertext: 1088 bytes.
- Secreto compartido: 32 bytes.

En ambas plataformas, el secreto obtenido mediante
encapsulación coincidió con el obtenido mediante
desencapsulación.

La Raspberry Pi Zero W requirió habilitar la opción
OQS_PERMIT_UNSUPPORTED_ARCHITECTURE=ON debido a que
ARMv6 no está oficialmente soportada por liboqs 0.16.0.

Esta configuración se utiliza exclusivamente con fines
experimentales y no garantiza seguridad para producción.

Estos resultados verifican la reproducibilidad de la
instalación y del funcionamiento local de ML-KEM-768.

La validación de comunicación cliente-servidor mediante
Python y la reproducción de TLS 1.3 clásico e híbrido
se realizarán posteriormente.

Las pruebas de rendimiento, consumo de memoria y
optimización de recursos también permanecen pendientes.


### 10.11. Validación de comunicación cliente-servidor con Python

Una vez verificada la instalación de ML-KEM-768 en
ambas Raspberry Pi, se realizó una prueba de
comunicación TCP utilizando liboqs-python.

En ambas Raspberry, ejecutar:

```bash
cd ~/PQC-EdgeLab
source ~/pqc-venv/bin/activate
export OQS_INSTALL_PATH=$HOME/_oqs
```

En pqc-server, iniciar el servidor:

```bash
python -u scripts/mlkem/server_mlkem.py 2>&1 | tee ~/pqc-mlkem-server.log
```

Mantener esta terminal abierta mientras espera
la conexión.

En pqc-client, ejecutar:

```bash
python -u scripts/mlkem/client_mlkem.py 2>&1 | tee ~/pqc-mlkem-client.log
```

El procedimiento intercambia una clave pública de
1184 bytes y un ciphertext de 1088 bytes.

El cliente y el servidor calculan un secreto
compartido de 32 bytes.


#### Configuración del servidor mediante hostname

Para mejorar la portabilidad del experimento, el archivo
`scripts/mlkem/client_mlkem.py` utiliza variables de entorno
en lugar de una dirección IP fija.

Por defecto, el cliente se conecta mediante:

- Hostname: `pqc-server.local`
- Puerto TCP: `5000`

El código utiliza:

```python
SERVER_IP = os.environ.get(
    "PQC_SERVER_HOST", "pqc-server.local"
)
PORT = int(os.environ.get("PQC_MLKEM_PORT", "5000"))
```

Si otro investigador necesita utilizar un servidor
diferente, puede configurar las variables desde la
terminal Linux del cliente:

```bash
export PQC_SERVER_HOST="nombre-del-servidor.local"
export PQC_MLKEM_PORT=5000
```

Estas variables son opcionales cuando se utilizan
los valores predeterminados.

#### Verificación de conectividad por hostname

Desde `pqc-client`, comprobar la resolución del nombre:

```bash
getent ahostsv4 pqc-server.local
```

Después, con el entorno Python activado y el servidor
ML-KEM escuchando, ejecutar:

```bash
python -u ~/PQC-EdgeLab/scripts/mlkem/client_mlkem.py
```

Comparar el SHA-256 del secreto compartido mostrado
por el cliente y por el servidor.

Los hashes deben coincidir exactamente dentro de una
misma ejecución.

Cada nueva ejecución genera normalmente un secreto
diferente, por lo que no se espera obtener siempre
el mismo hash.

#### Consideraciones de reproducibilidad

- Ambos dispositivos deben tener conectividad de red.
- El nombre del servidor debe resolverse correctamente.
- El servidor debe estar escuchando en el puerto 5000.
- Los archivos modificados en GitHub deben actualizarse
  también en las Raspberry cuando sea necesario.
- El protocolo Python utiliza ML-KEM-768 sobre TCP;
  no implementa TLS ni autenticación.
- No se deben publicar claves privadas ni secretos
  compartidos.

#### Resultado experimental

La comunicación se completó correctamente tras
reinstalar ambas Raspberry Pi y reconstruir el
entorno criptográfico desde el repositorio.

El hash SHA-256 del secreto compartido coincidió
en ambos extremos:

```text
dfbc842c90b964b98eef8587ad4bac20795a9c259def873d866e42d97002c82d
```

El servidor identificó la conexión procedente de
192.168.100.172.

La prueba confirma el funcionamiento del intercambio
ML-KEM-768 mediante Python/liboqs sobre TCP.

Este prototipo no implementa autenticación ni TLS 1.3
y no está destinado a comunicaciones de producción.


## 11. Consideraciones de reproducibilidad

Para futuras ejecuciones se recomienda registrar:

- Modelo y revisión de cada placa.
- Versión y arquitectura del sistema operativo.
- Versiones de Python, OpenSSL y liboqs.
- Configuración de red.
- Memoria disponible antes de ejecutar las pruebas.
- Estado de los servicios del sistema.
- Fecha y condiciones de cada experimento.

No deben publicarse contraseñas, claves privadas, credenciales ni secretos criptográficos.

## 12. Estado del procedimiento

La primera implementación del laboratorio permitió validar la comunicación entre ambas Raspberry Pi y ejecutar pruebas criptográficas con OpenSSL y liboqs.

Actualmente se está reconstruyendo el entorno a partir de instalaciones limpias para comprobar la reproducibilidad de los procedimientos documentados.

Las mediciones formales de rendimiento y la optimización de recursos se realizarán en etapas posteriores.
