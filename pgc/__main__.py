"""py -3.11 -m pgc  [--simular] [--puerto COM5] [--puerto-web 8000] [--sin-tunel] [--sin-voz] [--no-abrir]"""
import sys

from pgc.arranque import main

sys.exit(main())
