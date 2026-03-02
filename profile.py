# -*- coding: utf-8 -*-
"""
Хранение и загрузка когнитивного профиля (ответы опросника + свободный текст + сгенерированный фрагмент для системного промпта).
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any

from questionnaire import QUESTIONS, get_question_by_id, FREE_FORM_PROMPT

PROFILE_FILENAME = "cognitive_profile.json"
DEFAULT_PROFILE_PATH = Path(__file__).resolve().parent / PROFILE_FILENAME


def _serialize_options(options: list) -> list[dict]:
    return [
        {"value": o.value, "label": o.label, "description": getattr(o, "description", None)}
        for o in options
    ]


def answers_to_text(answers: dict[str, str]) -> str:
    """Превращает ответы опросника в читаемый текст для передачи в LLM."""
    lines = []
    for q in QUESTIONS:
        val = answers.get(q.id)
        if not val:
            continue
        for opt in q.options:
            if opt.value == val:
                lines.append(f"- {q.text}\n  Ответ: {opt.label}")
                break
    return "\n".join(lines) if lines else "Нет ответов."


def build_profile(
    answers: dict[str, str],
    free_form: str,
    system_prompt_fragment: str,
    *,
    profile_path: Path = DEFAULT_PROFILE_PATH,
) -> dict[str, Any]:
    """Собирает полный профиль для сохранения."""
    return {
        "version": 1,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "answers": answers,
        "free_form_prompt": FREE_FORM_PROMPT,
        "free_form_text": (free_form or "").strip(),
        "system_prompt_fragment": system_prompt_fragment.strip(),
    }


def save_profile(profile: dict[str, Any], path: Path = DEFAULT_PROFILE_PATH) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


def load_profile(path: Path = DEFAULT_PROFILE_PATH) -> dict[str, Any] | None:
    path = Path(path)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_system_prompt_fragment(profile: dict[str, Any] | None) -> str:
    """Возвращает готовый фрагмент для вставки в системный промпт. Если профиля нет — пустая строка."""
    if not profile:
        return ""
    return profile.get("system_prompt_fragment", "").strip()
