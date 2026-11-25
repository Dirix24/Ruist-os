# Ruist OS

| Estado | Trabajo |
|---|---|
| Verificado localmente | El inventario identifica el ASUS X550LC, i7-4500U, 9,2 GiB de RAM, Intel Haswell con i915, NVIDIA GT 720M 10de:1140, Wi-Fi Ralink RT3290 con rt2800pci y SSD SATA. Ruist Performance lee la memoria y el estado de TLP. |
| Verificado con pruebas de código | Tema claro aplicado a un árbol XFCE de prueba y selección de sesión XFCE, Plasma X11 y LXQt según los archivos de sesión. Validación de YAML, XML y listas de paquetes. |
| Implementado, pendiente de instalación de prueba | Instalador con selección previa de escritorio, apariencia y aplicaciones. Limpieza de la cuenta Live. Git y Gitg en la ISO base. Identidad Ruist Neon. ZRAM limitada por RAM y perfiles con TLP. |
| Implementado, pendiente de prueba de arranque | Tema animado de Plymouth, Firefox ESR de Debian y Timeshift accesible desde Ruist Center. |
| Pendiente | ISO híbrida, arranque BIOS/UEFI, instalación offline, instalación online con cada escritorio, cifrado y arranque dual. Tras reiniciar, comprobar la ausencia de la cuenta Live, el archivo sudoers y el autologin Live. |
| Pendiente | Pruebas físicas de arranque, suspensión, batería, temperatura, pantalla externa, sonido, OpenGL/Vulkan y Wi-Fi en el ASUS X550LC. Medir memoria, disco y tiempo de arranque. Mantener Intel i915 como configuración inicial y verificar el comportamiento de la GT 720M con Nouveau antes de considerar otras opciones. |
| Pendiente | Integrar el registro reversible para los grupos elegidos en Calamares. Ampliar Ruist Drivers, Recovery y Welcome. Verificar actualización, tienda, recuperación y perfiles completos en una instalación. |
| Pendiente | Publicar una versión estable después de las pruebas. |
| Implementado, pendiente de prueba gráfica | Plank en XFCE/X11 con accesos iniciales, panel superior translúcido y locales UTF-8 español e inglés en Live. |
| En evaluación | Sesión Wayland ligera con Labwc y un dock de Waybar. Comparar RAM en reposo y validar aceleración Intel y arranque en VirtualBox antes de usarla por defecto. |

Las observaciones del portátil corresponden a su sistema actual. Para probar Ruist OS, usar una máquina virtual y un disco desechable. Repetir la instalación con red desactivada y activada. Verificar en cada caso la sesión elegida, el tema, los paquetes y la cuenta creada.
