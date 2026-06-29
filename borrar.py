from pathlib import Path
import shutil

# Carpeta del proyecto
SOURCE_ROOT = Path(r"C:\dynamic-assessment-api\app")

# Carpeta donde está este script
SCRIPT_DIR = Path(__file__).parent

# Carpeta destino
DEST_DIR = SCRIPT_DIR / "archivos_para_ia"
DEST_DIR.mkdir(exist_ok=True)

contador = 0

for archivo in SOURCE_ROOT.rglob("*.py"):
    # Ignorar cualquier archivo dentro de __pycache__
    if "__pycache__" in archivo.parts:
        continue

    # Ruta relativa respecto a SOURCE_ROOT
    relativa = archivo.relative_to(SOURCE_ROOT)

    # Construir un nombre único
    # models/course.py -> models__course.txt
    nuevo_nombre = "__".join(relativa.with_suffix("").parts) + ".txt"

    destino = DEST_DIR / nuevo_nombre

    # Copiar el contenido agregando la ruta original al inicio
    with open(archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    encabezado = (
        f"# Archivo original: {relativa.as_posix()}\n\n"
    )

    with open(destino, "w", encoding="utf-8") as f:
        f.write(encabezado)
        f.write(contenido)

    contador += 1

print(f"Se copiaron {contador} archivos a:")
print(DEST_DIR)