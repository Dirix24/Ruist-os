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
| `ruist-info` | Resumen del sistema |

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
.github/workflows/
  build-iso.yml         Compila la ISO en GitHub Actions
```

## Compilar la ISO

La forma recomendada es GitHub Actions: **Actions → Compilar ISO de Ruist OS → Run workflow**. Primero se ejecutan las comprobaciones y, si pasan, se compila y se publica la ISO como artefacto. También se recompila cada domingo.

A mano, en un Debian trixie con permisos de root:

```sh
sudo apt install live-build debootstrap squashfs-tools xorriso
tools/check-config.sh
sudo lb build
```

## Hoja de ruta

- Probar la ISO en el portátil (ASUS X550LC) y medir el consumo de memoria en reposo (objetivo: unos 950 MB).
- Driver NVIDIA 390xx para tarjetas antiguas (Debian trixie ya no lo incluye).
- Separar la configuración en una base común y una capa por escritorio, para publicar también una edición con **GNOME**.
- Página web del proyecto.
