"""
Gestió de descàrrega i cache local de PDFs oficials del CTE.

Estratègia de cache:
  1. Per cada PDF, guarda localment: {key}.pdf + {key}.meta.json
  2. El meta guarda: url, last_modified, etag, data_baixada, mida
  3. Cada X hores (CHECK_INTERVAL_H) fa HEAD request per verificar si hi ha canvis
  4. Si ETag o Last-Modified han canviat → re-descarrega
  5. Si el servidor no retorna capçaleres de versió → compara mida del fitxer
"""

import json
import logging
import time
from pathlib import Path
from datetime import datetime, timedelta

import requests

from config import CTE_BASE_URL, CTE_DOCUMENTS, CACHE_DIR

logger = logging.getLogger(__name__)

CHECK_INTERVAL_H = 24          # Hores entre comprovacions de versió
REQUEST_TIMEOUT  = 30          # Segons timeout descàrrega
HEADERS = {
    "User-Agent": "CTE-IA-Tool/1.0 (arquitectura; contact: tool@example.com)"
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _meta_path(key: str) -> Path:
    return CACHE_DIR / f"{key}.meta.json"

def _pdf_path(key: str) -> Path:
    return CACHE_DIR / f"{key}.pdf"

def _load_meta(key: str) -> dict:
    p = _meta_path(key)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def _save_meta(key: str, meta: dict):
    _meta_path(key).write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def _needs_check(meta: dict) -> bool:
    """Retorna True si han passat més de CHECK_INTERVAL_H des de l'última comprovació."""
    last = meta.get("last_checked_ts", 0)
    return (time.time() - last) > CHECK_INTERVAL_H * 3600

def _full_url(url_path: str) -> str:
    return CTE_BASE_URL + url_path


# ── Lògica principal ──────────────────────────────────────────────────────────

def _head_info(url: str) -> dict:
    """Fa un HEAD request i retorna capçaleres rellevants."""
    try:
        r = requests.head(url, headers=HEADERS, timeout=REQUEST_TIMEOUT,
                          allow_redirects=True)
        r.raise_for_status()
        return {
            "etag":          r.headers.get("ETag", ""),
            "last_modified": r.headers.get("Last-Modified", ""),
            "content_length": r.headers.get("Content-Length", ""),
            "status":        r.status_code,
        }
    except requests.RequestException as e:
        logger.warning(f"HEAD request fallit per {url}: {e}")
        return {"status": 0}


def _download(url: str, dest: Path) -> bool:
    """Descarrega el PDF a dest. Retorna True si ha anat bé."""
    try:
        logger.info(f"Descarregant {url} → {dest.name}")
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT,
                         stream=True, allow_redirects=True)
        r.raise_for_status()
        dest.write_bytes(r.content)
        logger.info(f"  ✓ {len(r.content):,} bytes")
        return True
    except requests.RequestException as e:
        logger.error(f"  ✗ Error descarregant {url}: {e}")
        return False


def ensure_pdf(db_code: str, pdf_key: str, url_path: str,
               force: bool = False) -> dict:
    """
    Assegura que el PDF identificat per pdf_key és disponible i vigent.

    Retorna un dict amb:
      - path: Path al fitxer local (o None si no s'ha pogut obtenir)
      - updated: bool — True si s'ha re-descarregat
      - new_version: bool — True si el servidor tenia versió nova
      - meta: dict de metadades
      - error: str o None
    """
    key = f"{db_code.replace('-','_')}_{pdf_key}"
    pdf  = _pdf_path(key)
    meta = _load_meta(key)
    url  = _full_url(url_path)

    result = {
        "path": pdf if pdf.exists() else None,
        "updated": False,
        "new_version": False,
        "meta": meta,
        "error": None,
    }

    # ── Si no tenim el fitxer → descarregar sempre ──────────────────────────
    if not pdf.exists() or force:
        ok = _download(url, pdf)
        if ok:
            head = _head_info(url)
            new_meta = {
                "db": db_code, "key": pdf_key, "url": url_path,
                "etag": head.get("etag", ""),
                "last_modified": head.get("last_modified", ""),
                "content_length": head.get("content_length", ""),
                "file_size": pdf.stat().st_size,
                "downloaded_at": datetime.utcnow().isoformat(),
                "last_checked_ts": time.time(),
            }
            _save_meta(key, new_meta)
            result.update({"path": pdf, "updated": True, "meta": new_meta})
        else:
            result["error"] = f"No s'ha pogut descarregar {url}"
        return result

    # ── Fitxer existeix: comprovar versió si toca ──────────────────────────
    if not _needs_check(meta) and not force:
        # Cache vigent, no cal comprovar
        return result

    head = _head_info(url)
    meta["last_checked_ts"] = time.time()

    if head["status"] == 0:
        # Servidor no accessible, usar cache existent
        logger.warning(f"  Servidor no accessible per {key}, usant cache")
        _save_meta(key, meta)
        return result

    # Detectar canvis per ETag, Last-Modified o mida
    changed = False
    if head.get("etag") and head["etag"] != meta.get("etag", ""):
        changed = True
        logger.info(f"  ETag canviat per {key}")
    elif head.get("last_modified") and head["last_modified"] != meta.get("last_modified", ""):
        changed = True
        logger.info(f"  Last-Modified canviat per {key}")
    elif head.get("content_length"):
        remote_size = int(head["content_length"])
        local_size  = pdf.stat().st_size
        if abs(remote_size - local_size) > 1024:  # diferència > 1KB
            changed = True
            logger.info(f"  Mida canviada per {key}: {local_size} → {remote_size}")

    if changed:
        ok = _download(url, pdf)
        if ok:
            meta.update({
                "etag":          head.get("etag", ""),
                "last_modified": head.get("last_modified", ""),
                "content_length": head.get("content_length", ""),
                "file_size":     pdf.stat().st_size,
                "downloaded_at": datetime.utcnow().isoformat(),
                "last_checked_ts": time.time(),
            })
            _save_meta(key, meta)
            result.update({
                "path": pdf, "updated": True,
                "new_version": True, "meta": meta,
            })
        else:
            result["error"] = f"Re-descàrrega fallida, s'usa versió en cache"
    else:
        _save_meta(key, meta)
        logger.debug(f"  Cache vigent per {key}")

    return result


def ensure_db_pdfs(db_code: str, primary_only: bool = True) -> dict:
    """
    Assegura tots els PDFs d'un DB (o només el primari).
    Retorna { pdf_key: result_dict }.
    """
    db_cfg = CTE_DOCUMENTS.get(db_code, {})
    results = {}
    for pdf_cfg in db_cfg.get("pdfs", []):
        if primary_only and not pdf_cfg.get("primary", False):
            continue
        results[pdf_cfg["key"]] = ensure_pdf(
            db_code, pdf_cfg["key"], pdf_cfg["url"]
        )
    return results


def get_primary_pdf_path(db_code: str) -> Path | None:
    """Retorna el Path del PDF primari d'un DB (descarregant si cal)."""
    db_cfg = CTE_DOCUMENTS.get(db_code, {})
    for pdf_cfg in db_cfg.get("pdfs", []):
        if pdf_cfg.get("primary", False):
            res = ensure_pdf(db_code, pdf_cfg["key"], pdf_cfg["url"])
            return res.get("path")
    return None


def check_all_updates() -> list[dict]:
    """
    Comprova si hi ha actualitzacions per a tots els DBs.
    Retorna llista d'esdeveniments (actualitzat, error, etc.)
    """
    events = []
    for db_code, db_cfg in CTE_DOCUMENTS.items():
        for pdf_cfg in db_cfg.get("pdfs", []):
            if not pdf_cfg.get("primary", False):
                continue
            res = ensure_pdf(db_code, pdf_cfg["key"], pdf_cfg["url"],
                             force=False)
            if res.get("new_version"):
                events.append({
                    "db": db_code,
                    "key": pdf_cfg["key"],
                    "label": pdf_cfg["label"],
                    "event": "updated",
                    "message": f"El PDF {pdf_cfg['label']} s'ha actualitzat al servidor oficial.",
                })
            elif res.get("error"):
                events.append({
                    "db": db_code,
                    "key": pdf_cfg["key"],
                    "event": "error",
                    "message": res["error"],
                })
    return events


def cache_status() -> list[dict]:
    """Retorna l'estat de la cache per a tots els PDFs primaris."""
    status = []
    for db_code, db_cfg in CTE_DOCUMENTS.items():
        for pdf_cfg in db_cfg.get("pdfs", []):
            if not pdf_cfg.get("primary", False):
                continue
            key = f"{db_code.replace('-','_')}_{pdf_cfg['key']}"
            pdf  = _pdf_path(key)
            meta = _load_meta(key)
            status.append({
                "db":        db_code,
                "key":       pdf_cfg["key"],
                "label":     pdf_cfg["label"],
                "available": pdf.exists(),
                "size_kb":   round(pdf.stat().st_size / 1024) if pdf.exists() else 0,
                "downloaded_at": meta.get("downloaded_at", "—"),
                "last_checked":  (
                    datetime.fromtimestamp(meta["last_checked_ts"]).strftime("%d/%m/%Y %H:%M")
                    if meta.get("last_checked_ts") else "—"
                ),
                "last_modified": meta.get("last_modified", "—"),
            })
    return status
