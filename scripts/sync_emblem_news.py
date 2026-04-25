"""Extrait les N derniers blocs de version du CHANGELOG.md et les reformate en
TextMeshPro pour le Custom Menu Item d'Emblem. Relancer ce script apres chaque
mise a jour du CHANGELOG pour synchroniser le texte affiche dans le menu."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"
OUTPUT_DIR = ROOT / "BepInEx" / "plugins" / "Emblem" / "Menu"
OUTPUT = OUTPUT_DIR / "News.txt"

N_VERSIONS = 3

TITLE_COLOR = "#73C8FF"
VERSION_COLOR = "#FF8B00"
DATE_COLOR = "#808080"
SECTION_COLOR = "#73C8FF"
REMOVED_COLOR = "#FF6B6B"
ADDED_COLOR = "#6BFF9C"
DEFAULT_COLOR = "#E6E6E6"
SEPARATOR_COLOR = "#404040"

SECTION_COLORS = {
    "Notes": DEFAULT_COLOR,
    "Changed": SECTION_COLOR,
    "Added": ADDED_COLOR,
    "Removed": REMOVED_COLOR,
    "Fixed": SECTION_COLOR,
    "Pending": "#FFB86B",
}


def extract_versions(text: str, limit: int) -> list[tuple[str, str, str]]:
    """Retourne jusqu'a `limit` tuples (version, date, body)."""
    blocks = re.findall(
        r"^##\s*\[([^\]]+)\][^\n]*?-\s*(\d{4}-\d{2}-\d{2})\s*\n(.*?)(?=^##\s*\[|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not blocks:
        raise SystemExit("No version block found in CHANGELOG.md")
    return [(v.strip(), d.strip(), b.strip()) for v, d, b in blocks[:limit]]


def format_body(body: str) -> str:
    lines: list[str] = []
    for raw in body.splitlines():
        line = raw.rstrip()
        if not line:
            if lines and lines[-1] != "":
                lines.append("")
            continue

        section_match = re.match(r"^###\s+(.+)$", line)
        if section_match:
            label = section_match.group(1).strip()
            key = label.split()[0]
            color = SECTION_COLORS.get(key, SECTION_COLOR)
            if lines and lines[-1] != "":
                lines.append("")
            lines.append(f"<b><color={color}>{label.upper()}</color></b>")
            continue

        bullet_match = re.match(r"^-\s+(.+)$", line)
        if bullet_match:
            content = bullet_match.group(1).strip()
            lines.append(f"  <color={DEFAULT_COLOR}>•</color> {content}")
            continue

        lines.append(line)

    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def format_version_block(version: str, date: str, body: str) -> str:
    header = (
        f"<size=28><b><color={VERSION_COLOR}>v{version}</color></b></size>"
        f"  <size=16><color={DATE_COLOR}>{date}</color></size>\n"
    )
    return header + format_body(body)


def main() -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    versions = extract_versions(text, N_VERSIONS)

    banner = (
        f"<size=38><b><color={TITLE_COLOR}>LETHAL RELOADED NEWS</color></b></size>\n"
        f"<size=14><color={DATE_COLOR}>Latest {len(versions)} updates</color></size>\n\n"
    )
    separator = f"\n\n<color={SEPARATOR_COLOR}>────────────────────────────────</color>\n\n"

    body = separator.join(format_version_block(v, d, b) for v, d, b in versions)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(banner + body + "\n", encoding="utf-8")
    shown = ", ".join(f"v{v}" for v, _, _ in versions)
    print(f"Wrote {OUTPUT} ({shown})")


if __name__ == "__main__":
    main()
