#!/usr/bin/env python3
"""
GaitSense Demo Session Recorder
YC Application Summer 2026

Records a terminal session, strips ANSI codes, and emits a structured
Markdown transcript ready for direct upload to the YC application.

YC Summer 2026 confirmed limits:
  - 1 min video  : co-founder introduction
  - 3 min / 100 MB video : product demo
  - 25 MB .md    : agent workflow transcript  ← this script targets this field

Usage
-----
  python demo/record_session.py start              # begin recording
  python demo/record_session.py stop               # finalise + write .md
  python demo/record_session.py check              # size check vs 25 MB
  python demo/record_session.py process <raw.log>  # post-process existing log

Transcripts land in demo/transcripts/gaitsense_demo_<timestamp>.md
The raw capture uses the Unix script(1) utility (standard on Linux/macOS).
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ── Constants ─────────────────────────────────────────────────────────────────

TRANSCRIPT_DIR = Path(__file__).parent / "transcripts"
RAW_LOG_PATH   = TRANSCRIPT_DIR / ".raw_session.log"
PID_FILE       = TRANSCRIPT_DIR / ".recorder.pid"

YC_LIMIT_BYTES = 25 * 1024 * 1024  # 25 MB — confirmed for YC Summer 2026 .md field
WARN_THRESHOLD = 0.80

# Known agent names for section-header detection
_AGENTS = {
    "loss-setter", "pinn-compiler", "layer-setter", "pinn-executor",
    "pinn-monitor", "physics-reviewer", "train-sum", "bill-drafter",
    "judicial-clerk", "attorney-a", "attorney-b", "attorney-A", "attorney-B",
    "simulator-operator", "uart-reader", "plotter", "police",
    "plot-orchestrator", "pinn-validator", "pinn-archivist", "doc-processor",
    "pinn-grid-controller", "sw-advisor", "hw-advisor", "synthetic-data-generator",
}

# ── ANSI / control-character stripping ────────────────────────────────────────

_ANSI_RE = re.compile(
    r"""
    \x1b
    (?:
        \[[0-9;?]*[A-Za-z]
      | \][^\x07\x1b]*(?:\x07|\x1b\\)
      | [()][AB012]
      | [PX^_].*?\x1b\\
      | [NOPQRSTUVWXYZ\\[\]^_`]
      | [@-Z\\-_]
    )
    | \r(?!\n)
    | \x08+
    | \x07
    """,
    re.VERBOSE,
)

def strip_ansi(text: str) -> str:
    clean = _ANSI_RE.sub("", text)
    clean = re.sub(r"\n{3,}", "\n\n", clean)
    return clean


# ── Markdown structuring ──────────────────────────────────────────────────────

# Patterns that identify section boundaries in the cleaned output
_ACT_RE         = re.compile(r"^#+\s*Act\s+\d", re.IGNORECASE)
_AGENT_RE       = re.compile(
    r"^(?:Agent|Subagent)?\s*[→>]\s*([a-z][a-z0-9\-]+)\b", re.IGNORECASE
)
_PROMPT_RE      = re.compile(r"^\$\s+|^>\s+")
_VIOLATION_RE   = re.compile(r"VIOLATION|CONSTITUTIONAL POLICE REPORT", re.IGNORECASE)
_BILL_RE        = re.compile(r"^###?\s*BILL:", re.IGNORECASE)
_RULING_RE      = re.compile(r"^\*\*Justice\s+rules?\b|^RULING:", re.IGNORECASE)
_CASE_LAW_RE    = re.compile(r"case law|case_law", re.IGNORECASE)
_CODE_FENCE_RE  = re.compile(r"^```")

def _looks_like_agent_header(line: str) -> str | None:
    """Return agent name if the line is an agent-launch announcement, else None."""
    m = _AGENT_RE.match(line.strip())
    if m and m.group(1).lower() in {a.lower() for a in _AGENTS}:
        return m.group(1)
    # Also catch "Running loss-setter..." style lines
    for name in _AGENTS:
        if re.search(rf"\b{re.escape(name)}\b", line, re.IGNORECASE):
            if any(kw in line.lower() for kw in ("running", "launched", "agent:", "→", ">")):
                return name
    return None


def _to_markdown(clean_text: str, timestamp: str, host: str) -> str:
    """
    Convert stripped terminal output to structured Markdown.

    Strategy:
      - Wrap the whole session in a top-level document header.
      - Detect Act boundaries, agent launches, constitutional events, and
        engineer prompts; promote them to Markdown headings / callout blocks.
      - Everything else goes into fenced code blocks so the raw terminal
        output is preserved verbatim but visually contained.
    """
    lines   = clean_text.splitlines()
    out     = []
    in_code = False  # are we inside a ``` block in the source?

    def flush_code(buf: list[str]) -> list[str]:
        if not buf:
            return []
        stripped = [l for l in buf if l.strip()]
        if not stripped:
            return []
        return ["```", *buf, "```", ""]

    code_buf: list[str] = []

    def emit_code_buf():
        nonlocal code_buf
        out.extend(flush_code(code_buf))
        code_buf = []

    # ── Document header ──
    out.append(f"# GaitSense Constitutional AI Demo — Session Transcript")
    out.append(f"**YC Application Summer 2026**  ")
    out.append(f"Recorded: {timestamp} · Host: `{host}`")
    out.append("")
    out.append("> This transcript was generated automatically from a live Claude Code")
    out.append("> session. All agent outputs, constitutional rulings, and case law")
    out.append("> entries are reproduced verbatim.")
    out.append("")
    out.append("---")
    out.append("")

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Pass through source-level code fences unchanged
        if _CODE_FENCE_RE.match(stripped):
            in_code = not in_code
            code_buf.append(line)
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # ── Act boundary ──
        if _ACT_RE.match(stripped):
            emit_code_buf()
            out.append(f"## {stripped.lstrip('#').strip()}")
            out.append("")
            i += 1
            continue

        # ── Constitutional violation block ──
        if _VIOLATION_RE.search(stripped):
            emit_code_buf()
            out.append("> **⚠ CONSTITUTIONAL EVENT**")
            # Collect the block (until blank line or next structural marker)
            block = []
            while i < len(lines):
                l = lines[i]
                if not l.strip() and block:
                    break
                block.append(l)
                i += 1
            for bl in block:
                out.append(f"> {bl}")
            out.append("")
            continue

        # ── Bill header ──
        if _BILL_RE.match(stripped):
            emit_code_buf()
            out.append(f"### {stripped.lstrip('#').strip()}")
            out.append("")
            i += 1
            continue

        # ── Justice ruling ──
        if _RULING_RE.match(stripped):
            emit_code_buf()
            out.append(f"### {stripped.lstrip('*').strip()}")
            out.append("")
            i += 1
            continue

        # ── Agent launch ──
        agent_name = _looks_like_agent_header(stripped)
        if agent_name:
            emit_code_buf()
            out.append(f"#### Agent: `{agent_name}`")
            out.append("")
            i += 1
            continue

        # ── Engineer shell prompt ──
        if _PROMPT_RE.match(stripped):
            emit_code_buf()
            out.append(f"**Engineer:** `{stripped}`")
            out.append("")
            i += 1
            continue

        # Everything else accumulates into a code block
        code_buf.append(line)
        i += 1

    emit_code_buf()
    return "\n".join(out) + "\n"


# ── File-size helpers ─────────────────────────────────────────────────────────

def _size_str(n: int) -> str:
    if n < 1024:        return f"{n} B"
    if n < 1024 ** 2:   return f"{n / 1024:.1f} KB"
    return f"{n / (1024 ** 2):.2f} MB"


def check_size(path: Path) -> dict:
    size = path.stat().st_size
    pct  = size / YC_LIMIT_BYTES * 100
    return {"path": path, "size": size, "pct": pct,
            "ok": size <= YC_LIMIT_BYTES,
            "warn": size >= YC_LIMIT_BYTES * WARN_THRESHOLD}


def print_size_report(info: dict) -> None:
    bar_width = 40
    filled    = int(min(info["pct"], 100) / 100 * bar_width)
    bar       = "█" * filled + "░" * (bar_width - filled)
    c = ("\033[32m" if info["ok"] and not info["warn"]
         else "\033[33m" if info["warn"] and info["ok"]
         else "\033[31m")
    r = "\033[0m"

    print(f"\nTranscript : {info['path']}")
    print(f"Size       : {_size_str(info['size'])} / {_size_str(YC_LIMIT_BYTES)}")
    print(f"[{c}{bar}{r}] {info['pct']:.1f} %")

    if not info["ok"]:
        print(f"\n\033[31mERROR: exceeds YC 25 MB .md upload limit.\033[0m")
        print("  Trim options:")
        print("    1. Strip per-epoch training logs (biggest contributor)")
        print("    2. Remove raw UART tables — keep SESSION_END summary only")
        print("    3. Run:  python demo/record_session.py trim <transcript.md>")
    elif info["warn"]:
        print(f"\n\033[33mWARNING: >{WARN_THRESHOLD*100:.0f}% of limit — trim before session grows.\033[0m")
    else:
        print(f"\n\033[32mOK: within YC 25 MB limit (confirmed Summer 2026).\033[0m")


# ── Trim command: remove epoch log noise ──────────────────────────────────────

_EPOCH_LINE_RE = re.compile(
    r"epoch\s+\d+.*loss|val_gyy|val_az|val_vel|val_phase|raw_physics",
    re.IGNORECASE,
)

def cmd_trim(path_str: str) -> None:
    path = Path(path_str)
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    lines    = path.read_text(encoding="utf-8").splitlines()
    kept     = []
    removed  = 0
    in_epoch = False

    for line in lines:
        if _EPOCH_LINE_RE.search(line):
            in_epoch = True
            removed += 1
            continue
        if in_epoch and line.strip() == "":
            in_epoch = False
            continue
        in_epoch = False
        kept.append(line)

    trimmed = path.with_stem(path.stem + "_trimmed")
    trimmed.write_text("\n".join(kept) + "\n", encoding="utf-8")
    info = check_size(trimmed)
    print(f"Removed {removed} epoch-log lines → {trimmed}")
    print_size_report(info)


# ── Core processing ───────────────────────────────────────────────────────────

def _process_raw(raw_path: Path, out_path: Path) -> None:
    try:
        import socket; host = socket.gethostname()
    except Exception:
        host = "unknown"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    raw_text  = raw_path.read_bytes().decode("utf-8", errors="replace")
    clean     = strip_ansi(raw_text)
    md        = _to_markdown(clean, timestamp, host)

    out_path.write_text(md, encoding="utf-8")
    print(f"Transcript written → {out_path}")


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_start() -> None:
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    if PID_FILE.exists():
        print(f"Recording already running. Run `stop` first.")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    RAW_LOG_PATH.write_text("")
    PID_FILE.write_text(f"{os.getpid()}\n{timestamp}\n")

    print(f"Recording started → {RAW_LOG_PATH}")
    print("Run the demo. When done, type `exit` or Ctrl-D, then run `stop`.\n")
    os.execlp("script", "script", "-q", "-e", str(RAW_LOG_PATH))


def cmd_stop() -> None:
    if not PID_FILE.exists():
        print("No active recording. Start with: python demo/record_session.py start")
        sys.exit(1)

    lines     = PID_FILE.read_text().strip().splitlines()
    timestamp = lines[1] if len(lines) > 1 else datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    PID_FILE.unlink()

    if not RAW_LOG_PATH.exists():
        print("Raw log not found.")
        sys.exit(1)

    out_path = TRANSCRIPT_DIR / f"gaitsense_demo_{timestamp}.md"
    _process_raw(RAW_LOG_PATH, out_path)
    RAW_LOG_PATH.unlink(missing_ok=True)
    print_size_report(check_size(out_path))


def cmd_check() -> None:
    transcripts = sorted(TRANSCRIPT_DIR.glob("gaitsense_demo_*.md"))
    if not transcripts:
        print("No transcripts found in", TRANSCRIPT_DIR)
        sys.exit(1)
    print_size_report(check_size(transcripts[-1]))


def cmd_process(raw_path_str: str) -> None:
    raw_path = Path(raw_path_str)
    if not raw_path.exists():
        print(f"File not found: {raw_path}")
        sys.exit(1)
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path  = TRANSCRIPT_DIR / f"gaitsense_demo_{timestamp}.md"
    _process_raw(raw_path, out_path)
    print_size_report(check_size(out_path))


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="GaitSense session recorder — YC Summer 2026 .md transcript",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("start",  help="Start recording")
    sub.add_parser("stop",   help="Stop and write .md transcript")
    sub.add_parser("check",  help="Size check vs 25 MB YC limit")

    p = sub.add_parser("process", help="Post-process an existing raw log")
    p.add_argument("raw_log")

    t = sub.add_parser("trim", help="Strip epoch-log noise to reduce file size")
    t.add_argument("transcript")

    args = parser.parse_args()
    {"start":   cmd_start,
     "stop":    cmd_stop,
     "check":   cmd_check,
     "process": lambda: cmd_process(args.raw_log),
     "trim":    lambda: cmd_trim(args.transcript),
    }[args.command]()


if __name__ == "__main__":
    main()
