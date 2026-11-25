# Ruist OS

- Conserva Debian 13 Trixie, el kernel oficial, live-build, Calamares, AMD64 y la instalación base XFCE/X11 sin conexión.
- Valida paquetes contra Debian Trixie y separa los extras descargables de la ISO base. Las operaciones privilegiadas deben comprobar sus entradas. Mantén las interfaces gráficas como usuario normal.
- Los controladores propietarios requieren una elección explícita. Conserva una sesión gráfica de respaldo y documenta los casos de hardware heredado.
- Ejecuta `tools/check-config.sh`, `tests/check-config.sh`, `tools/check-packages.sh` y `python3 -m unittest discover -s tests -p 'test_*.py'` cuando afecten a los cambios.
- Prueba instalaciones con discos virtuales desechables. Registra los resultados de BIOS, UEFI, instalación y hardware físico por separado en ROADMAP.md.
