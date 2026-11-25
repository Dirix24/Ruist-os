# Ruist OS

Distribución Linux basada en **Debian 13 (trixie)** con escritorio **XFCE sobre X11**, pensada para programar videojuegos, diseñar, modelar en 3D y jugar. Minimalista, oscura y optimizada para exprimir el hardware, con herramientas gráficas al estilo MX Linux.

Versión actual: **0.2 "Genesis"**.

## Qué incluye

- **Escritorio:** XFCE sobre X11 con Plank, barra superior translúcida, tema Arc-Dark e iconos Papirus-Dark.
- **Navegador:** Firefox ESR desde Debian Trixie, con localización en español.
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
| `ruist-perf` | TLP: perfil de corriente, automático o de batería. Estado de memoria, ZRAM y energía. |
| `ruist-git` | Abre una copia local en Gitg para revisar historial, ramas y cambios, y crear commits. |
| `ruist-kernel` | Gestiona el metapaquete estable `linux-image-amd64` y conserva kernels anteriores |
| `ruist-update` | Actualiza el sistema con apt |
| `ruist-maintenance cleanup` | Mantenimiento con confirmación de APT antes de retirar paquetes |
| `ruist-info` | Logo de Ruist OS y características del equipo (fastfetch) |
| `ruist-detect` | Inventario de hardware de solo lectura; `--json` ofrece datos estructurados |
| `ruist-desktop` | Abre los ajustes nativos de fondo, iconos, tema, efectos y pantallas de XFCE |
| `ruist-profile` | Instala perfiles APT combinables y permite retirar solo paquetes que instaló el perfil |

`ruist-detect` usa sysfs y `/proc` para el inventario básico. `lspci`/`modinfo`, `glxinfo`, `vulkaninfo`, `lsblk`, `xrandr`, `wpctl` y `pactl` añaden detalles cuando están disponibles. La falta de una herramienta se muestra como no verificada; el inventario no instala ni cambia controladores y no infiere fallos de firmware solo por detectar un dispositivo.

Los perfiles `universal`, `gaming`, `development`, `architecture`, `productivity`, `desktop-plasma` y `desktop-lxqt` son opcionales y no se incluyen en la ISO base. Se pueden combinar con `ruist-profile install gaming development`; APT muestra los cambios y pide confirmación. Antes del particionado, Calamares ofrece XFCE, Plasma o LXQt, el tema claro u oscuro de XFCE y grupos opcionales de aplicaciones. XFCE y ambos temas están disponibles sin conexión. Plasma, LXQt y los grupos de aplicaciones necesitan Internet. LightDM abre el escritorio seleccionado si se descargó correctamente y conserva XFCE como alternativa. `ruist-profile remove gaming` solo propone retirar paquetes que el propio perfil instaló y conserva paquetes compartidos por otros perfiles. Las dependencias quedan instaladas y se pueden revisar con APT antes de cualquier limpieza. Si Gaming instala Steam, habilita i386 para descargar sus bibliotecas de 32 bits; esa arquitectura se conserva para que otros programas i386 sigan funcionando.

`ruist-kernel` solo ofrece el metapaquete estable de Debian para amd64/i386. Instalarlo no elimina versiones anteriores: GRUB conserva esas entradas como alternativa de arranque. No ofrece kernels externos ni promete mejoras de rendimiento.

### Escritorio y límite conocido

`ruist-desktop` abre las herramientas de configuración mantenidas por XFCE. Desde ellas se elige una imagen personal como fondo y se ajustan temas, iconos, efectos y pantallas; XFCE guarda esos cambios en la sesión del usuario. La identidad actual usa Arc-Dark, Papirus-Dark, fondos de Ruist y el logotipo oficial proporcionado por el propietario. Xfdesktop permite mover y ordenar los iconos, pero su herramienta de organización automática no ofrece una opción documentada para centrar el grupo de iconos. El centrado automático queda pendiente de una prueba técnica de un gestor de iconos compatible o un componente propio, sin sustituir Xfdesktop. [Manual de Xfdesktop en Debian trixie](https://manpages.debian.org/trixie/xfdesktop4/xfdesktop.1.en.html).

## Estructura

```
config/
  package-lists/        Paquetes de la ISO base
  hooks/live/           Scripts que se ejecutan al construir la ISO (apariencia, limpieza, Flathub...)
  includes.chroot/      Archivos que se copian tal cual al sistema (/etc, /usr/local/bin...)
    usr/share/ruist/profiles/  Catálogos opcionales para Ruist Profile
  archives/             Repositorios de apt
tools/
  check-config.sh       Comprueba sintaxis, XML y JSON (sin red)
  check-packages.sh     Comprueba que todos los paquetes existen en trixie
  make-wallpaper.py     Genera el fondo y el emblema neón a partir del logotipo oficial
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

La instalación base de Calamares usa los paquetes de la ISO y elimina de la copia instalada la cuenta Live, su acceso sudo y su inicio automático. Calamares comprueba la conexión con Debian antes de instalar los extras. En XFCE se puede cambiar el tema desde **Ruist Center → Configuración del escritorio**. Plasma y LXQt conservan sus herramientas nativas de personalización.

**Ruist Git** abre copias locales en Gitg. Para crear una copia del repositorio oficial desde la terminal:

```sh
git clone https://github.com/Dirix24/Ruist-os.git
```

## Hoja de ruta

Consulta [ROADMAP.md](ROADMAP.md) para ver el estado de las pruebas y los pasos pendientes para una versión estable.

## Arranque y restauración

Plymouth muestra el emblema animado de Ruist OS durante el arranque gráfico. Si necesitas ver los mensajes del kernel, pulsa Esc o quita `splash` de la línea de arranque de GRUB.

Abre **Ruist Center → Puntos de restauración (Timeshift)** para elegir el destino y crear una instantánea manual. En ext4, como el disco actual del ASUS X550LC, elige **RSYNC**. Puedes activar un calendario en Timeshift si lo deseas. Timeshift está pensado para restaurar el sistema. Guarda tus documentos y partidas en una copia aparte.

Para jugar, instala Steam o Lutris desde Ruist Store. El perfil Gaming añade GameMode y MangoHud. La compatibilidad de Proton depende del juego, su sistema antitrampas y el controlador gráfico.


## Cambiar de escritorio y revisar controladores

En el primer inicio, **Bienvenido a Ruist OS** abre **Hardware y controladores** o **Instalar o cambiar de escritorio**. También puedes volver a abrir ambas herramientas desde Ruist Center o el menú de aplicaciones.

Cuando eliges un escritorio en Ruist Center, queda guardado en tu cuenta. Guarda tu trabajo y cierra sesión para abrirlo. Si todavía no está instalado, el gestor lo descarga desde Debian y lo guarda al terminar. El selector de LightDM también te permite cambiar de sesión. XFCE está incluido para instalar sin Internet.

En **Controladores de Ruist OS**, el inventario muestra los módulos activos. Los controladores propietarios y el firmware se eligen por separado. El inventario distingue lo que se detecta de lo que se ha podido verificar.


## Tienda gráfica

**Tienda de programas** abre GNOME Software de Debian, con catálogo AppStream, búsqueda, instalación, desinstalación y actualizaciones. La ficha de cada aplicación indica si procede de Debian o Flathub. **Paquetes y herramientas Ruist** conserva el acceso a Synaptic y a la instalación guiada de Steam.


## Personalización y rendimiento

Desde **Ruist Center → Personalizar XFCE** puedes elegir los fondos Azul Neón, Violeta y Minimal, usar una imagen propia, ajustar Plank y cambiar entre modo claro y oscuro. Las preferencias se guardan por usuario.

Debian incluye el microcódigo para CPU Intel y AMD. TLP ajusta los perfiles según la alimentación, ZRAM se dimensiona según la memoria y el sistema programa TRIM para unidades y sistemas de archivos que lo admiten. **Modo de rendimiento** muestra memoria, ZRAM, discos y el estado de TLP. Las mejoras en autonomía y FPS se deben medir en cada equipo.

El sistema incluye audio Bluetooth con PipeWire y herramientas de impresión y escaneo de Debian. **Ruist Center → Impresoras** abre el administrador de impresoras.
