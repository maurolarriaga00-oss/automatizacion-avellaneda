"""Configuración del proyecto."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Lee el archivo .env y carga sus valores
load_dotenv()

URL = "https://admin.avellanedaauntoque.com/home"


def _requerida(nombre):
    """Devuelve una variable del .env o avisa claramente si falta."""
    valor = os.getenv(nombre)

    if not valor:
        raise RuntimeError(
            f"Falta la variable {nombre} en tu archivo .env"
        )

    return valor


# --- Datos de la cuenta (obligatorios) ---
USUARIO = _requerida("AAUT_USER")
PASSWORD = _requerida("AAUT_PASSWORD")

# --- Opciones (tienen un valor por defecto) ---
CSV_PRODUCTOS = Path(os.getenv("AAUT_CSV", "productos.csv"))
TIEMPO_ESPERA = int(os.getenv("AAUT_TIEMPO_ESPERA", "20"))
RECARGO_MINORISTA = int(os.getenv("AAUT_RECARGO_MINORISTA", "3000"))
