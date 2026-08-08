import re
from datetime import date, timedelta
from unicodedata import combining, normalize

from todo_list_service.domain.models.todo import TodoStatus

_TITLE_PREFIXES = (
    r"ajoute(?:r)?(?:\s+une)?(?:\s+tache|\s+todo)?(?:\s+pour)?",
    r"cree(?:r)?(?:\s+une)?(?:\s+tache|\s+todo)?(?:\s+pour)?",
    r"je\s+dois",
    r"il\s+faut(?:\s+que\s+je)?",
    r"pense\s+a",
    r"rappelle(?:\s+moi)?(?:\s+de)?",
)
_RELATIVE_DATE_PATTERNS = (
    r"\bapres\s+demain\b",
    r"\bdemain\b",
    r"\baujourd\s+hui\b",
)
_CANCEL_MARKERS = (
    "annule",
    "annuler",
    "laisse tomber",
    "stop",
    "abandonne",
    "abandonner",
    "finalement non",
)


def normalize_user_text(raw: str) -> str:
    decomposed = normalize("NFKD", raw.casefold())
    normalized = "".join(character for character in decomposed if not combining(character))
    return re.sub(r"[^a-z0-9]+", " ", normalized).strip()


def parse_status(raw: str) -> TodoStatus | None:
    normalized = normalize_user_text(raw.strip())
    aliases = {
        "a faire": TodoStatus.TODO,
        "todo": TodoStatus.TODO,
        "en cours": TodoStatus.WIP,
        "wip": TodoStatus.WIP,
        "termine": TodoStatus.DONE,
        "done": TodoStatus.DONE,
    }
    if normalized in aliases:
        return aliases[normalized]

    for status in TodoStatus:
        if status.value == normalized:
            return status
    return None


def parse_relative_due_date(raw: str, today: date | None = None) -> date | None:
    normalized = normalize_user_text(raw)
    reference_date = today or date.today()
    if "apres demain" in normalized:
        return reference_date + timedelta(days=2)
    if "demain" in normalized:
        return reference_date + timedelta(days=1)
    if "aujourd hui" in normalized:
        return reference_date
    return None


def is_cancel_request(raw: str) -> bool:
    normalized = normalize_user_text(raw)
    return any(marker in normalized for marker in _CANCEL_MARKERS)


def extract_title_hint(raw: str) -> str | None:
    normalized = normalize_user_text(raw)
    without_prefix = normalized
    for prefix in _TITLE_PREFIXES:
        without_prefix = re.sub(rf"^{prefix}\s+", "", without_prefix)

    without_date = without_prefix
    for pattern in _RELATIVE_DATE_PATTERNS:
        without_date = re.sub(pattern, "", without_date)

    title = re.sub(r"\s+", " ", without_date).strip()
    return title if title else None
