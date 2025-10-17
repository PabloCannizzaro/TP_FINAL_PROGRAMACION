"""Servicio de perfiles de usuario (simple).

Administra un JSON con preferencias (idioma, alto contraste, nombre validado).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict


class ServicioPerfiles:
    """Persistencia simple de preferencias de usuario."""

    def __init__(self, ruta: Path) -> None:
        self.ruta = ruta
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        if not self.ruta.exists():
            self._guardar({})

    def _leer(self) -> Dict:
        try:
            return json.loads(self.ruta.read_text("utf-8"))
        except Exception:
            return {}

    def _guardar(self, data: Dict) -> None:
        self.ruta.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def set_preferencia(self, usuario: str, clave: str, valor) -> None:
        if clave == "nombre":
            # validar con regex: letras, espacios y guiones, 2-32 chars
            if not re.fullmatch(r"[A-Za-zÀ-ÿ\- ]{2,32}", str(valor)):
                raise ValueError("Nombre inválido")
        data = self._leer()
        prefs = data.get(usuario, {})
        prefs[clave] = valor
        data[usuario] = prefs
        self._guardar(data)

    def get_prefs(self, usuario: str) -> Dict:
        data = self._leer()
        return data.get(usuario, {})

