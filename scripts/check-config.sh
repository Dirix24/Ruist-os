#!/bin/bash
# Compatibilidad: conserva la ruta histórica scripts/check-config.sh.
# La implementación única vive en tools/check-config.sh.
set -u
ROOT=$(cd "$(dirname "$0")/.." && pwd) || exit 1
exec "$ROOT/tools/check-config.sh" "$@"
