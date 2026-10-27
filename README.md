# Ruist OS

Distribución Linux basada en **Debian 13 (trixie)** con escritorio **XFCE sobre X11**, pensada para programar videojuegos, diseñar, modelar en 3D y jugar. Minimalista, oscura y optimizada para exprimir el hardware, con herramientas gráficas al estilo MX Linux.

Versión actual: **0.2 "Genesis"**.

## Qué incluye

- **Escritorio:** XFCE sin Wayland, tema Arc-Dark, iconos Papirus-Dark, panel fino.
- **Navegador:** Brave por defecto, con Rewards, Wallet, VPN y asistente de IA desactivados.
- **Rendimiento:** zram, ajustes de memoria y red, planificador de disco según el tipo de disco, CPU al máximo con corriente y en ahorro con batería (TLP). `ruist-perf` cambia de modo a mano.
- **Desarrollo:** perfil opcional con gcc, clang, cmake, ninja, gdb, Git, Python, Node y bibliotecas SDL2, GLFW, Vulkan y OpenAL.
- **Juegos:** perfil opcional con GameMode, MangoHud, Lutris, Steam y Wine; habilita i386 para Steam cuando hace falta.
- **Diseño y 3D:** perfil opcional con FreeCAD, OpenSCAD, Blender, GIMP e Inkscape.
- **Instalador:** Calamares instala la base incluida en la ISO sin exigir conexión; las actualizaciones se hacen después desde Ruist Update.

## Herramientas propias

| Comando | Para qué sirve |
|---|---|
| `ruist-center` | Panel de control: actualizar, tienda, drivers, rendimiento, limpieza e información |
| `ruist-drivers` | Gestor de drivers: NVIDIA (con `nvidia-detect`), Wi-Fi, microcódigo, firmware e impresoras |
| `ruist-software` | Tienda de programas: instala, busca, consulta y desinstala aplicaciones APT y Flatpak |
| `ruist-perf` | Modo de rendimiento: `rendimiento`, `equilibrado`, `ahorro`, `estado` |
| `ruist-kernel` | Gestiona el metapaquete estable `linux-image-amd64` y conserva kernels anteriores |
| `ruist-update` | Actualiza el sistema con apt |
| `ruist-maintenance cleanup` | Mantenimiento con confirmación de APT antes de retirar paquetes |
| `ruist-info` | Logo de Ruist OS y características del equipo (fastfetch) |
| `ruist-detect` | Inventario de hardware de solo lectura; `--json` ofrece datos estructurados |
| `ruist-desktop` | Abre los ajustes nativos de fondo, iconos, tema, efectos y pantallas de XFCE |
| `ruist-profile` | Instala perfiles APT combinables y permite retirar solo paquetes que instaló el perfil |

`ruist-detect` usa sysfs y `/proc` para el inventario básico. `lspci`/`modinfo`, `glxinfo`, `vulkaninfo`, `lsblk`, `xrandr`, `wpctl` y `pactl` añaden detalles cuando están disponibles. La falta de una herramienta se muestra como no verificada; el inventario no instala ni cambia controladores y no infiere fallos de firmware solo por detectar un dispositivo.

Los perfiles `universal`, `gaming`, `development`, `architecture`, `productivity`, `desktop-plasma` y `desktop-lxqt` son opcionales y no se incluyen en la ISO base. Se pueden combinar con `ruist-profile install gaming development`; APT muestra los cambios y pide confirmación. Calamares ofrece XFCE (incluido en la ISO), Plasma o LXQt después de instalar la base. Plasma y LXQt requieren Internet en ese paso; si no hay conexión, se conserva XFCE y se pueden añadir después desde Ruist Center. `ruist-profile remove gaming` solo propone retirar paquetes que el propio perfil instaló y conserva paquetes compartidos por otros perfiles. Las dependencias quedan instaladas y se pueden revisar con APT antes de cualquier limpieza. Si Gaming instala Steam, habilita i386 para descargar sus bibliotecas de 32 bits; esa arquitectura se conserva para que otros programas i386 sigan funcionando.

`ruist-kernel` solo ofrece el metapaquete estable de Debian para amd64/i386. Instalarlo no elimina versiones anteriores: GRUB conserva esas entradas como alternativa de arranque. No ofrece kernels externos ni promete mejoras de rendimiento.

### Escritorio y límite conocido

`ruist-desktop` abre las herramientas de configuración mantenidas por XFCE. Desde ellas se elige una imagen personal como fondo y se ajustan temas, iconos, efectos y pantallas; XFCE guarda esos cambios en la sesión del usuario. La identidad actual usa Arc-Dark, Papirus-Dark, fondos de Ruist y el logotipo oficial proporcionado por el propietario. Xfdesktop permite mover y ordenar los iconos, pero su herramienta de organización automática no ofrece una opción documentada para centrar el grupo de iconos. El centrado automático queda pendiente de una prueba técnica de un gestor de iconos compatible o un componente propio, sin sustituir Xfdesktop. [Manual de Xfdesktop en Debian trixie](https://manpages.debian.org/trixie/xfdesktop4/xfdesktop.1.en.html).

## Estructura

```
config/
  package-lists/        Paquetes de la ISO base
  hooks/live/           Scripts que se ejecutan al construir la ISO (Brave, limpieza, Flathub...)
  includes.chroot/      Archivos que se copian tal cual al sistema (/etc, /usr/local/bin...)
    usr/share/ruist/profiles/  Catálogos opcionales para Ruist Profile
  archives/             Repositorios de apt
tools/
  check-config.sh       Comprueba sintaxis, XML y JSON (sin red)
  check-packages.sh     Comprueba que todos los paquetes existen en trixie
  make-wallpaper.py     Genera el fondo de pantalla (formas geométricas azules)
  make-ascii-logo.py    Convierte el logo en arte ASCII para ruist-info
branding/
  ruist-logo.png        Logo oficial original (512x512)
  ruist-logo-mark.png   Variante transparente del símbolo para iconos
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

La tienda APT usa una lista permitida de aplicaciones y deja que APT muestre dependencias y solicite confirmación. La retirada no ejecuta `autoremove`. Flatpak se administra solo en el ámbito del usuario. El catálogo APT completo se puede consultar con Synaptic; la búsqueda ampliada usa Flathub cuando hay conexión.

Notas importantes:

- **No ejecutes `lb config`**: reescribiría los archivos de `config/`, que están escritos a mano.
- **No uses `lb clean --purge`**: borraría `config/common`, `bootstrap`, `chroot`, `binary` y `source`.
- El archivo `.build/config` lo exige `lb build` y está en `.gitignore`, por eso hay que crearlo a mano (el workflow ya lo hace).

## Probar la ISO

Configuración recomendada para probar en una máquina virtual (VirtualBox o virt-manager): 4 GB de RAM, 2 procesadores y un disco de 25 GB. La ISO todavía necesita una ejecución real en una máquina virtual.

En modo live, el inicio de sesión es:

| Usuario | Contraseña |
|---|---|
| `ruist` | *(vacía: solo pulsa Enter)* |

Si el sistema pide contraseña para una acción de administrador, también vale dejarla vacía.

Al instalar con Calamares, el usuario y la contraseña los eliges tú durante la instalación.

La instalación base de Calamares no actualiza índices APT y funciona sin conexión (`update_db: false`, `update_system: false`). La etapa opcional actualiza índices solo si hay Internet; sin conexión se omite y queda instalado XFCE. Los perfiles de aplicaciones se instalan desde Ruist Center después y necesitan conexión si los paquetes no están en caché.

## Hoja de ruta

- Añadir selección de perfiles de aplicaciones en Calamares y registrar su propiedad para que sigan siendo reversibles.
- Resolver técnicamente el centrado de iconos movibles en Xfdesktop.
- Construir la ISO y probarla en una máquina virtual y en el portátil (ASUS X550LC); medir memoria en reposo.
- Driver NVIDIA 390xx para tarjetas antiguas (Debian trixie ya no lo incluye).
- Separar la configuración en una base común y una capa por escritorio, para publicar también una edición con **GNOME**.
- Página web del proyecto.
