#!/bin/sh
cd "$(dirname "$0")"
exec python3 src/game.py "$@"
