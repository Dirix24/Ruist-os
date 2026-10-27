# Ruist OS

Distribución Linux basada en **Debian 13 (trixie)** con escritorio **XFCE sobre X11**, pensada para programar videojuegos, diseñar, modelar en 3D y jugar. Minimalista, oscura y optimizada para exprimir el hardware, con herramientas gráficas al estilo MX Linux.

Versión actual: **0.2 "Genesis"**.

## Qué incluye

- **Escritorio:** XFCE sin Wayland, tema Arc-Dark, iconos Papirus-Dark, panel fino.
- **Navegador:** Brave por defecto, con Rewards, Wallet, VPN y asistente de IA desactivados.
- **Rendimiento:** zram, ajustes de memoria y red, planificador de disco según el tipo de disco, CPU al máximo con corriente y en ahorro con batería (TLP). `ruist-perf` cambia de modo a mano.
- **Desarrollo:** gcc, clang, cmake, ninja, gdb, git, Python, Node y librerías de SDL2, GLFW, Vulkan y OpenAL.
- **Juegos:** gamemode, mangohud, Vulkan y Mesa. Steam y Wine desde la tienda.
- **Diseño y 3D:** Blender, GIMP e Inkscape (lista `ruist-creative`, se puede borrar para una ISO más ligera).
- **Instalador:** Calamares, que actualiza el sistema al instalar si hay internet.

## Herramientas propias

| Comando | Para qué sirve |
|---|---|
| `ruist-center` | Panel de control: actualizar, tienda, drivers, rendimiento, limpieza e información |
| `ruist-drivers` | Gestor de drivers: NVIDIA (con `nvidia-detect`), Wi-Fi, microcódigo, firmware e impresoras |
| `ruist-software` | Tienda de programas: Flathub, búsqueda en Flathub, programas de Debian y Synaptic |
| `ruist-perf` | Modo de rendimiento: `rendimiento`, `equilibrado`, `ahorro`, `estado` |
| `ruist-update` | Actualiza el sistema con apt |
| `ruist-maintenance cleanup` | Mantenimiento con confirmación de APT antes de retirar paquetes |
| `ruist-info` | Logo de Ruist OS y características del equipo (fastfetch) |
| `ruist-detect` | Inventario de hardware de solo lectura; `--json` ofrece datos estructurados |
| `ruist-desktop` | Abre los ajustes nativos de fondo, iconos, tema, efectos y pantallas de XFCE |

`ruist-detect` usa sysfs y `/proc` para el inventario básico. `lspci`/`modinfo`, `glxinfo`, `vulkaninfo`, `lsblk`, `xrandr`, `wpctl` y `pactl` añaden detalles cuando están disponibles. La falta de una herramienta se muestra como no verificada; el inventario no instala ni cambia controladores y no infiere fallos de firmware solo por detectar un dispositivo.

### Escritorio y límite conocido

`ruist-desktop` abre las herramientas de configuración mantenidas por XFCE. Desde ellas se elige una imagen personal como fondo y se ajustan temas, iconos, efectos y pantallas; XFCE guarda esos cambios en la sesión del usuario. Xfdesktop permite mover y ordenar los iconos, pero su herramienta de organización automática no ofrece una opción documentada para centrar el grupo de iconos. El centrado automático queda pendiente de una prueba técnica de un gestor de iconos compatible o un componente propio, sin sustituir Xfdesktop en esta entrega. [Manual de Xfdesktop en Debian trixie](https://manpages.debian.org/trixie/xfdesktop4/xfdesktop.1.en.html).

## Estructura

```
config/
  package-lists/        Paquetes que lleva la ISO (una lista por tema)
  hooks/live/           Scripts que se ejecutan al construir la ISO (Brave, limpieza, Flathub...)
  includes.chroot/      Archivos que se copian tal cual al sistema (/etc, /usr/local/bin...)
  archives/             Repositorios de apt
tools/
  check-config.sh       Comprueba sintaxis, XML y JSON (sin red)
  check-packages.sh     Comprueba que todos los paquetes existen en trixie
  make-wallpaper.py     Genera el fondo de pantalla (formas geométricas azules)
  make-ascii-logo.py    Convierte el logo en arte ASCII para ruist-info
branding/
  ruist-logo.png        Logo de Ruist OS (original de 512x512)
.github/workflows/
  build-iso.yml         Compila la ISO en GitHub Actions
```

## Compilar la ISO

La forma recomendada es GitHub Actions: **Actions → Compilar ISO de Ruist OS → Run workflow**. Las comprobaciones se ejecutan también en cada push y pull request; la ISO se construye cuando se inicia manualmente el workflow o cada domingo, si pasan todas las comprobaciones.

A mano, en un Debian trixie con permisos de root:

```sh
sudo apt install live-build debootstrap squashfs-tools xorriso
tools/check-config.sh
sudo rm -rf .build chroot binary cache
mkdir -p .build && touch .build/config
sudo lb build
```

Para comprobar la configuración y ejecutar las pruebas sin red ni permisos de root:

```sh
tools/check-config.sh
tests/check-config.sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Notas importantes:

- **No ejecutes `lb config`**: reescribiría los archivos de `config/`, que están escritos a mano.
- **No uses `lb clean --purge`**: borraría `config/common`, `bootstrap`, `chroot`, `binary` y `source`.
- El archivo `.build/config` lo exige `lb build` y está en `.gitignore`, por eso hay que crearlo a mano (el workflow ya lo hace).

## Probar la ISO

Funciona bien en una máquina virtual (VirtualBox o virt-manager) con 4 GB de RAM, 2 procesadores y un disco de 25 GB.

En modo live, el inicio de sesión es:

| Usuario | Contraseña |
|---|---|
| `ruist` | *(vacía: solo pulsa Enter)* |

Si el sistema pide contraseña para una acción de administrador, también vale dejarla vacía.

Al instalar con Calamares, el usuario y la contraseña los eliges tú durante la instalación.

## Hoja de ruta

- Probar la ISO en el portátil (ASUS X550LC) y medir el consumo de memoria en reposo (objetivo: unos 950 MB).
- Driver NVIDIA 390xx para tarjetas antiguas (Debian trixie ya no lo incluye).
- Separar la configuración en una base común y una capa por escritorio, para publicar también una edición con **GNOME**.
- Página web del proyecto.
