"""Configuración de la base de datos SQLite para la aplicación de empleados."""

from pathlib import Path
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

CARPETA_DATOS = Path(__file__).parent / "datos"
CARPETA_DATOS.mkdir(exist_ok=True)

RUTA_BASE_DATOS = CARPETA_DATOS / "empleados.db"

motor = create_engine(f"sqlite:///{RUTA_BASE_DATOS}", connect_args={"check_same_thread": False})
SesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)


class Base(DeclarativeBase):
    pass


def obtener_sesion() -> Generator[Session, None, None]:
    """Provee una sesión de base de datos por solicitud."""
    sesion = SesionLocal()
    try:
        yield sesion
    finally:
        sesion.close()
