# scripts/run_trinity.py

import argparse
import json
from pathlib import Path
from fx25.agents.trinity import run_trinity

def _print_or_save(out, out_path: str | None, fmt: str):
    """
    - Si fmt == json y out es dict/list -> lo imprime como JSON válido (bonito).
    - Si out_path viene, guarda el resultado a disco.
    """
    # Normalizamos a texto para imprimir
    if fmt == "json" and isinstance(out, (dict, list)):
        text = json.dumps(out, ensure_ascii=False, indent=2)
    else:
        # out ya es texto (plain/bullets/haiku) o otra cosa imprimible
        text = out if isinstance(out, str) else str(out)

    print("\n=== TRINITY SAYS ===\n")
    print(text)

    if out_path:
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        # si es JSON y es dict/list, guardamos como JSON puro
        if fmt == "json" and isinstance(out, (dict, list)):
            p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            p.write_text(text, encoding="utf-8")
        print(f"\n[guardado] {p.resolve()}")

if __name__ == "__main__":
    print("RUN_TRINITY MAIN START")

    p = argparse.ArgumentParser()
    p.add_argument("--task", required=True, help="¿Qué quieres que Trinity haga?")
    p.add_argument("--lang", default="es", help="Idioma de salida (por defecto: es)")
    p.add_argument(
        "--format",
        dest="fmt",
        default="plain",
        choices=["plain", "bullets", "haiku", "json"],
        help="Formato de salida",
    )
    p.add_argument(
        "--out",
        default="",
        help="Ruta de archivo para guardar la salida (opcional). Ej: outputs/trinity.json",
    )

    args = p.parse_args()

    out = run_trinity(args.task, lang=args.lang, fmt=args.fmt)
    _print_or_save(out, args.out or None, args.fmt)
