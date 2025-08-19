import re
import os
import unicodedata

README = "README.md"
OUT_DIR = "Capitulos"

# ---------- Utilidades ----------
def slugify(text: str) -> str:
    # Quitar acentos y caracteres no ASCII
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    # Reemplazar no-alfa/num por guiones
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-")
    # Evitar nombres vacíos
    return text or "capitulo"

def limpiar_texto(texto: str) -> str:
    # 1) 3+ saltos seguidos -> 2 (un solo párrafo en blanco)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    # 2) Remover espacios/tabs al inicio de cada línea
    texto = re.sub(r'^[ \t]+', '', texto, flags=re.MULTILINE)
    return texto

# Detectores de encabezados "capítulo"
RE_TITULO = re.compile(r'^#\s+El\s+Constelario\s+de\s+Nia\s*$', re.IGNORECASE)
RE_PREFACIO = re.compile(r'^###\s+Prefacio\s*$', re.IGNORECASE)
RE_ULTIMO = re.compile(r'^###\s+El\s+ultimo\s+ronroneo\s*$', re.IGNORECASE)  # sin acentos para comparar robusto
RE_ULTIMO_ACC = re.compile(r'^###\s+El\s+último\s+ronroneo\s*$', re.IGNORECASE)
RE_EPILOGO = re.compile(r'^###\s+Epilogo\s+—\s+.+$', re.IGNORECASE)          # sin acento
RE_EPILOGO_ACC = re.compile(r'^###\s+Epílogo\s+—\s+.+$', re.IGNORECASE)
RE_CAPITULO = re.compile(r'^###\s+Cap[ií]tulo\s+([1-9]\d*)\s+—\s+(.+)$', re.IGNORECASE)

def tipo_de_encabezado(linea: str):
    """Devuelve (tipo, meta) o (None, None).
       tipos: 'titulo', 'prefacio', 'ultimo', 'epilogo', 'capitulo'
       meta: dict con info útil (numero, titulo, etc.)
    """
    raw = linea.rstrip()

    if RE_TITULO.match(raw):
        return "titulo", {"texto": raw.lstrip("# ").strip()}

    if RE_PREFACIO.match(raw):
        return "prefacio", {"texto": "Prefacio"}

    if RE_ULTIMO.match(raw) or RE_ULTIMO_ACC.match(raw):
        return "ultimo", {"texto": "El último ronroneo"}

    m = RE_EPILOGO.match(raw) or RE_EPILOGO_ACC.match(raw)
    if m:
        # Extraer todo después de "### Epílogo — "
        texto = raw.split("—", 1)[1].strip() if "—" in raw else "Epilogo"
        return "epilogo", {"texto": f"Epilogo — {texto}"}

    m = RE_CAPITULO.match(raw)
    if m:
        n, titulo = m.group(1), m.group(2).strip()
        return "capitulo", {"n": int(n), "titulo": titulo}

    return None, None

def nombre_archivo(tipo: str, meta: dict) -> str:
    if tipo == "titulo":
        return f"00 - Titulo - {slugify(meta['texto'])}.md"
    if tipo == "prefacio":
        return f"000 - Prefacio.md"
    if tipo == "ultimo":
        return f"998 - El ultimo ronroneo.md"
    if tipo == "epilogo":
        # Quitar el prefijo "Epilogo — " para el slug
        texto = meta["texto"].split("—", 1)[-1].strip() if "—" in meta["texto"] else meta["texto"]
        return f"999 - Epilogo - {slugify(texto)}.md"
    if tipo == "capitulo":
        n = meta["n"]
        return f"{n:03d} - {slugify(meta['titulo'])}.md"
    # Fallback
    return f"{slugify(meta.get('texto','capitulo'))}.md"

def extraer_capitulos(texto: str):
    """
    Devuelve lista de dicts: { 'tipo':..., 'meta':..., 'contenido': '...' }
    Split por encabezados que definimos como inicio de capítulo.
    """
    lineas = texto.splitlines(keepends=True)
    indices = []
    headers = []

    for i, linea in enumerate(lineas):
        if linea.startswith("#"):
            tipo, meta = tipo_de_encabezado(linea)
            if tipo:
                indices.append(i)
                headers.append((tipo, meta))

    capitulos = []
    if not indices:
        return capitulos

    for idx, (tipo, meta) in zip(indices, headers):
        # rango hasta el próximo encabezado o fin
        start = idx
        # Buscar siguiente índice
        siguiente_indices = [j for j in indices if j > idx]
        end = siguiente_indices[0] if siguiente_indices else len(lineas)
        contenido = "".join(lineas[start:end]).rstrip() + "\n"
        capitulos.append({"tipo": tipo, "meta": meta, "contenido": contenido})

    return capitulos

def guardar_capitulos(caps):
    os.makedirs(OUT_DIR, exist_ok=True)
    for cap in caps:
        fname = nombre_archivo(cap["tipo"], cap["meta"])
        ruta = os.path.join(OUT_DIR, fname)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(cap["contenido"])
    return len(caps)

# ---------- Flujo principal ----------
def main():
    # Leer README
    with open(README, "r", encoding="utf-8") as f:
        original = f.read()

    # Limpiar
    limpio = limpiar_texto(original)

    # Guardar README limpio
    with open(README, "w", encoding="utf-8") as f:
        f.write(limpio)

    # Extraer y guardar capítulos
    caps = extraer_capitulos(limpio)
    cantidad = guardar_capitulos(caps)

    print(f"README limpiado. Capítulos detectados y guardados: {cantidad} en '{OUT_DIR}/' ✅")

if __name__ == "__main__":
    main()
