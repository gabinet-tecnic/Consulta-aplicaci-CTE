"""
CTE·IA Flask Server
===================
Servidor local que proporciona:
  GET  /                     → Serveix l'HTML principal
  POST /api/analyze          → Anàlisi IA de la descripció (DB genèric)
  POST /api/validate-si      → Validació DB-SI amb PDF oficial
  GET  /api/cache-status     → Estat de la cache de PDFs
  POST /api/refresh-pdfs     → Força re-descàrrega de tots els PDFs
  GET  /api/health           → Health check

Arrenca amb: python app.py
"""

import logging
import os
import shutil
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from config import FLASK_PORT, FLASK_DEBUG, STATIC_DIR, CACHE_DIR
from pdf_manager import cache_status, check_all_updates, ensure_db_pdfs
import ai_analyzer

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if FLASK_DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── App Flask ─────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=str(STATIC_DIR))
CORS(app, resources={r"/api/*": {"origins": "*"}})


# ── Rutes principals ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serveix l'HTML principal des de /static."""
    html_file = STATIC_DIR / "CTE_ia_validacio_SI.html"
    if html_file.exists():
        return send_file(str(html_file))
    # Fallback: cerca a la carpeta pare
    parent_html = STATIC_DIR.parent.parent / "html" / "CTE_ia_descriptor.html"
    if parent_html.exists():
        return send_file(str(parent_html))
    return (
        "<h1>CTE·IA</h1>"
        "<p>Posa l'HTML a <code>static/CTE_ia_validacio_SI.html</code></p>"
        "<p><a href='/api/health'>Health check</a> · "
        "<a href='/api/cache-status'>Estat PDFs</a></p>",
        200,
    )


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(str(STATIC_DIR), filename)


# ── Health check ──────────────────────────────────────────────────────────────

@app.route("/api/health")
def health():
    from config import ANTHROPIC_API_KEY, CTE_DOCUMENTS
    pdfs = cache_status()
    available = sum(1 for p in pdfs if p["available"])
    return jsonify({
        "status":    "ok",
        "api_key":   bool(ANTHROPIC_API_KEY),
        "pdfs_available": available,
        "pdfs_total":     len(pdfs),
        "cache_dir": str(CACHE_DIR),
    })


# ── Estat i gestió de la cache ────────────────────────────────────────────────

@app.route("/api/cache-status")
def api_cache_status():
    """Retorna l'estat de tots els PDFs en cache."""
    return jsonify({
        "status": "ok",
        "pdfs": cache_status(),
    })


@app.route("/api/refresh-pdfs", methods=["POST"])
def api_refresh_pdfs():
    """
    Comprova si hi ha actualitzacions als PDFs oficials.
    Si force=true al body, re-descarrega tots independentment.
    """
    body  = request.get_json(silent=True) or {}
    force = body.get("force", False)
    db    = body.get("db")  # opcional: refrescar només un DB

    if force:
        # Buidar cache i re-descarregar
        from config import CTE_DOCUMENTS
        dbs_to_refresh = [db] if db else list(CTE_DOCUMENTS.keys())
        results = []
        for db_code in dbs_to_refresh:
            res = ensure_db_pdfs(db_code, primary_only=True)
            for key, r in res.items():
                results.append({
                    "db":      db_code,
                    "key":     key,
                    "updated": r.get("updated", False),
                    "error":   r.get("error"),
                })
        return jsonify({"status": "ok", "results": results})
    else:
        # Comprovació suau (respecta interval de 24h)
        events = check_all_updates()
        return jsonify({
            "status": "ok",
            "updates_found": len([e for e in events if e["event"] == "updated"]),
            "events": events,
        })


# ── Endpoint 1: Anàlisi general ───────────────────────────────────────────────

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """
    Rep: { description: str, api_key?: str }
    Retorna: { interpretation, tipologia, selectedIds, db_reasoning, usage }
    """
    body = request.get_json(silent=True)
    if not body or not body.get("description"):
        return jsonify({"error": "Camp 'description' obligatori"}), 400

    description = body["description"].strip()
    if len(description) < 10:
        return jsonify({"error": "Descripció massa curta"}), 400

    api_key = body.get("api_key") or None

    logger.info(f"[analyze] descripció: {description[:80]}…")

    # Assegurar PDF DB-SI disponible en background (no bloqueja)
    try:
        from pdf_manager import ensure_pdf
        from config import CTE_DOCUMENTS
        si_pdf_cfg = next(
            p for p in CTE_DOCUMENTS["DB-SI"]["pdfs"] if p["primary"]
        )
        ensure_pdf("DB-SI", si_pdf_cfg["key"], si_pdf_cfg["url"])
    except Exception as e:
        logger.warning(f"No s'ha pogut pre-carregar PDF SI: {e}")

    result = ai_analyzer.analyze(description, api_key_override=api_key)

    if result.get("error"):
        return jsonify(result), 500

    return jsonify(result)


# ── Endpoint 2: Validació DB-SI ───────────────────────────────────────────────

@app.route("/api/validate-si", methods=["POST"])
def api_validate_si():
    """
    Rep:
      {
        description: str,
        tipologia: "unifamiliar|plurifamiliar|terciari",
        selectedIds: [...],
        sections?: ["SI-1", "SI-3"],   // opcional: només valida les indicades
        api_key?: str
      }

    Retorna:
      {
        sections: { SI-1: {...}, ... },
        general_notes: str,
        pdf_info: str,
        usage: { input_tokens, output_tokens, cache_creation_tokens, cache_read_tokens }
      }
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Body JSON obligatori"}), 400

    description  = body.get("description", "").strip()
    tipologia    = body.get("tipologia", "plurifamiliar")
    selected_ids = body.get("selectedIds", [])
    sections     = body.get("sections")   # None → totes
    api_key      = body.get("api_key") or None

    if not description:
        return jsonify({"error": "Camp 'description' obligatori"}), 400

    valid_tipologies = {"unifamiliar", "plurifamiliar", "terciari"}
    if tipologia not in valid_tipologies:
        return jsonify({"error": f"Tipologia invàlida. Usa: {valid_tipologies}"}), 400

    logger.info(
        f"[validate-si] tipologia={tipologia} "
        f"ids={selected_ids[:3]}… "
        f"sections={sections}"
    )

    # Assegurar PDF DB-SI
    pdf_path = None
    try:
        from pdf_manager import get_primary_pdf_path
        pdf_path = get_primary_pdf_path("DB-SI")
        if pdf_path:
            logger.info(f"  PDF disponible: {pdf_path.name}")
        else:
            logger.warning("  PDF DB-SI no disponible, continuant sense PDF")
    except Exception as e:
        logger.warning(f"  Error carregant PDF: {e}")

    result = ai_analyzer.validate_si(
        description=description,
        tipologia=tipologia,
        selected_ids=selected_ids,
        target_sections=sections,
        api_key_override=api_key,
    )

    if result.get("error"):
        return jsonify(result), 500

    # Afegir informació sobre ús del cache
    usage = result.get("usage", {})
    cache_hit = usage.get("cache_read_tokens", 0) > 0
    result["cache_hit"] = cache_hit

    return jsonify(result)


# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Ruta no trobada", "available": [
        "GET /", "GET /api/health", "GET /api/cache-status",
        "POST /api/analyze", "POST /api/validate-si",
        "POST /api/refresh-pdfs",
    ]}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": f"Error intern: {e}"}), 500


# ── Arrencada ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("  CTE·IA Flask Server")
    logger.info(f"  URL: http://localhost:{FLASK_PORT}")
    logger.info(f"  Cache: {CACHE_DIR}")
    logger.info(f"  API key: {'✓ configurada' if os.getenv('ANTHROPIC_API_KEY') else '✗ MANCA (.env)'}")
    logger.info("=" * 60)

    # Pre-descàrrega del PDF DB-SI si no existeix
    try:
        logger.info("Comprovant PDF DB-SI...")
        from pdf_manager import ensure_pdf
        from config import CTE_DOCUMENTS
        si_pdf_cfg = next(
            p for p in CTE_DOCUMENTS["DB-SI"]["pdfs"] if p["primary"]
        )
        res = ensure_pdf("DB-SI", si_pdf_cfg["key"], si_pdf_cfg["url"])
        if res.get("path"):
            logger.info(f"  ✓ DB-SI disponible: {res['path'].name}")
        else:
            logger.warning(f"  ✗ DB-SI no disponible: {res.get('error')}")
    except Exception as e:
        logger.warning(f"  No s'ha pogut pre-carregar DB-SI: {e}")

    app.run(
        host="127.0.0.1",
        port=FLASK_PORT,
        debug=FLASK_DEBUG,
        use_reloader=FLASK_DEBUG,
    )
