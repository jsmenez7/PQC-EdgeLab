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

1. Insertar la microSD correspondiente en cada Raspberry.
2. Conectar la alimentación al puerto `PWR IN`.
3. Esperar a que el sistema complete el primer arranque.
4. Comprobar que la Raspberry se haya conectado a la red Wi-Fi configurada.

Para evitar confusiones, ambas placas y sus tarjetas deben identificarse físicamente como CLIENT y SERVER.

## 7. Conexión por SSH

Desde PowerShell de Windows, conectarse al cliente mediante:

`ssh pqc@pqc-client.local`

Para conectarse al servidor:

`ssh pqc@pqc-server.local`

Durante la primera conexión SSH se solicita confirmar la identidad del dispositivo mediante su huella digital.

Una vez comprobada la identidad del equipo, se acepta la conexión y se introduce la contraseña del usuario `pqc`.

Si el nombre `.local` no se resuelve, puede utilizarse la dirección IP asignada por el router.

**Nota:** las direcciones IP pueden cambiar al reinstalar el sistema operativo. No deben considerarse valores permanentes del experimento.

## 8. Verificación del sistema

Después de establecer la conexión SSH, ejecutar en cada Raspberry:

**Identificar el hardware:**

`cat /proc/device-tree/model; echo`

**Comprobar la arquitectura:**

`uname -m`

**Verificar el sistema operativo:**

`cat /etc/os-release`

**Consultar memoria RAM:**

`free -h`

**Obtener la dirección IP:**

`hostname -I`

**Comprobar OpenSSL:**

`openssl version`

**Verificar Python:**

`python3 --version`

**Consultar el almacenamiento disponible:**

`df -h /`

La configuración inicial comprobada del laboratorio utilizó Raspbian GNU/Linux 13 (Trixie), Python 3.13.5 y OpenSSL 3.5.7. Estas versiones deben verificarse nuevamente después de cada reinstalación.

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

Una vez comprobado el funcionamiento del sistema operativo, se instalarán las bibliotecas y dependencias necesarias para los experimentos.

El repositorio incluye el instalador:

`setup/setup_raspberry.sh`

Este script prepara:

- Herramientas de compilación.
- liboqs 0.16.0.
- liboqs-python 0.16.0.1.
- Entorno virtual Python.
- Implementación mínima de ML-KEM-768.

La Raspberry Pi Zero W ARMv6 requiere habilitar experimentalmente `OQS_PERMIT_UNSUPPORTED_ARCHITECTURE=ON`.

La compilación en ARMv6 no cuenta con soporte oficial de liboqs y se utiliza exclusivamente con fines de investigación.

El script automatizado deberá validarse tras la reinstalación limpia antes de declararlo completamente reproducible.

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
