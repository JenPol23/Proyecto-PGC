"""Atajo de compatibilidad: el servidor está en el paquete pgc (py -3.11 -m pgc).

Uso (igual que siempre):
    py -3.11 servidor.py                 # busca la mano por USB; si no, simulada
    py -3.11 servidor.py --simular       # fuerza modo simulado
    py -3.11 servidor.py --puerto COM5   # puerto fijo de la mano
    py -3.11 servidor.py --sin-tunel     # solo red local (sin HTTPS)
    py -3.11 servidor.py --sin-voz       # no carga Whisper (arranque rápido)

Páginas:  /  (celular de los jurados)   /pantalla  (proyector)
"""
import sys

from pgc.arranque import main

if __name__ == "__main__":
    sys.exit(main())
