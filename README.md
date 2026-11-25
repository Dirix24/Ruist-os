<p align="center">
  <img src="branding/ruist-neon-mark.png" width="136" height="136" alt="Emblema Ruist Neon">
</p>

# Ruist OS

**0.2 Genesis · Debian 13 Trixie · AMD64**

Ruist OS es una distribución Linux personal para el uso diario, la programación, el diseño y los juegos. Su escritorio XFCE combina una barra superior translúcida, el dock Plank y fondos cyberpunk. El proyecto toma como referencia la base de Debian y las herramientas de administración de MX Linux.

## Qué incluye

| Área | Funciones |
| --- | --- |
| Escritorio | XFCE sobre X11 con fondos Azul Neón, Violeta y Minimal, temas claro y oscuro, y un dock personalizable. KDE Plasma y LXQt están disponibles con conexión. |
| Aplicaciones | Firefox ESR y la tienda gráfica GNOME Software, con aplicaciones de Debian y Flathub. Synaptic ofrece gestión avanzada de paquetes. |
| Hardware | Inventario de componentes y controladores activos, gestión de firmware, perfiles de energía TLP, ZRAM y TRIM en equipos compatibles. |
| Uso diario | Audio Bluetooth con PipeWire, impresión y escaneo, Gitg para repositorios y Timeshift para puntos de restauración. |
| Perfiles opcionales | Desarrollo, juegos, productividad, diseño y 3D. El perfil Gaming incluye Steam, Wine, Lutris, GameMode y MangoHud. |

## Descargar y probar

1. Abre una compilación exitosa de `main` y descarga **Artifacts → ruist-os-iso**. [Compilaciones de Ruist OS](https://github.com/Dirix24/Ruist-os/actions/workflows/build-iso.yml?query=branch%3Amain)
2. Descomprime el ZIP. En la misma carpeta, ejecuta `sha256sum -c archivo.iso.sha256`, sustituyendo el nombre por el del archivo incluido. La salida debe indicar que la ISO es correcta.
3. Monta la ISO en una máquina virtual. Para una primera prueba, asigna 2 CPU, 4 GB de RAM y un disco virtual de 25 GB.

La sesión Live usa la cuenta `ruist` con contraseña vacía. Calamares te pide crear tu propia cuenta al instalar. **XFCE** se instala sin conexión. **Plasma, LXQt y los grupos adicionales de aplicaciones** requieren Internet. Después, **Ruist Center → Instalar o cambiar de escritorio** guarda la sesión elegida para los próximos inicios.

## Desarrollo y estado

GitHub Actions valida la configuración, las pruebas y los paquetes, y compila la ISO con live-build. Las compilaciones pueden lanzarse manualmente desde el flujo **Compilar ISO de Ruist OS**. La ISO es una versión de prueba. La hoja de ruta recoge las verificaciones pendientes de instalación, controladores y restauración. [Flujo de compilación](.github/workflows/build-iso.yml) · [Hoja de ruta](ROADMAP.md)

## Créditos y licencia

Ruist OS fue creado y desarrollado con **OpenAI Codex (IA)**, bajo la dirección de **Dirix24**, que aportó la visión, las referencias visuales y las pruebas del proyecto.

El código, la configuración y la documentación originales de Ruist OS se distribuyen bajo **GNU GPL v3 o posterior** (`GPL-3.0-or-later`). Esta licencia permite usar, estudiar, modificar y redistribuir ese material conforme a sus términos. Debian, los paquetes incluidos y el material de terceros conservan sus respectivas licencias y avisos. [Texto completo de la licencia](LICENSE)
