"""TEMPORARY RSS instrumentation for the Render free-tier (512 MB) tuning.

Logs the process current resident set size at key points of the document
pipeline (before render, after render, after PDF generation, after email) so
the peak footprint can be read straight from the Render logs.

Portable by design: reads /proc/self/status (Linux/Render) first, then
falls back to psutil when installed, and degrades to an informational log
line on platforms where neither is available.

This module and every `log_rss` call site are meant to be removed once the
memory budget is confirmed.
"""

import logging

logger = logging.getLogger(__name__)


def _current_rss_kb() -> int | None:
    """Current resident set size in KiB, or None when unavailable."""
    try:
        with open("/proc/self/status", "r", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1])
    except Exception:  # noqa: BLE001 - non-Linux / restricted environments
        pass
    try:
        import psutil

        return int(psutil.Process().memory_info().rss / 1024)
    except Exception:  # noqa: BLE001 - psutil not installed
        return None


def log_rss(label: str) -> int | None:
    """Log current RSS in MiB at INFO and return it in KiB (or None)."""
    kb = _current_rss_kb()
    if kb is None:
        logger.info("RSS [%s]: unavailable on this platform", label)
        return None
    logger.info("RSS [%s]: %.1f MiB", label, kb / 1024.0)
    return kb