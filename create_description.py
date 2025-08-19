import os
import sys
import json
import uuid

def list_files(path, exts):
    if not os.path.isdir(path):
        return []
    return sorted(
        [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.lower().split(".")[-1] in exts]
    )

def pick_cover(images):
    # Prioriza un archivo llamado cover.*
    for name in images:
        base = os.path.splitext(name)[0].lower()
        if base == "cover":
            return name
    return images[0] if images else ""

def main():
    if len(sys.argv) < 2:
        print("Uso: python create_description.py <directorio_markdown>  (ej: Capitulos)")
        sys.exit(1)

    work_dir = sys.argv[1]
    if not os.path.isdir(work_dir):
        print(f"Directorio no encontrado: {work_dir}")
        sys.exit(1)

    # Archivos
    md_files = [f for f in os.listdir(work_dir) if f.lower().endswith(".md")]
    md_files.sort()  # con prefijos 00X queda en orden

    css_dir = os.path.join(work_dir, "css")
    img_dir = os.path.join(work_dir, "images")

    css_files = list_files(css_dir, {"css"})
    img_files = list_files(img_dir, {"png", "jpg", "jpeg", "gif"})

    cover_image = pick_cover(img_files)

    # Metadatos base
    data = {
        "metadata": {
            "dc:title": "El Constelario de Nia",
            "dc:creator": "Una chica gato",
            "dc:identifier": str(uuid.uuid4()),
        },
        "cover_image": cover_image,
        "default_css": css_files,  # puede ser [] si no hay css
        "chapters": [{"markdown": f, "css": ""} for f in md_files],
    }

    out_path = os.path.join(work_dir, "description.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Generado: {out_path}")
    print(f"- Capítulos: {len(md_files)} | CSS: {len(css_files)} | Imágenes: {len(img_files)} | Cover: {cover_image or 'Ninguna'}")

if __name__ == "__main__":
    main()
