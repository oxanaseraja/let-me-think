# -*- coding: utf-8 -*-
"""
Фаза 2: чат с учётом когнитивной карты. Поддержка загрузки файла (путь к файлу — содержимое подставляется в контекст).
"""

from pathlib import Path
from typing import Optional

from profile import load_profile, get_system_prompt_fragment, DEFAULT_PROFILE_PATH
from llm import complete

SYSTEM_BASE = """Ты — объясняющий бот. Твоя задача — объяснять материал так, чтобы пользователю было максимально легко понять и усвоить.

Когнитивная карта пользователя (обязательно учитывай при каждом ответе):

{cognitive_map}

Объясняй любой запрос и любой приложенный материал в соответствии с этой картой. Если пользователь приложил файл — опирайся на его содержимое и излагай с учётом предпочтений пользователя."""


def read_file_content(file_path: str | Path) -> str:
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def build_messages(
    user_text: str,
    file_path: Optional[str | Path] = None,
    history: Optional[list[dict[str, str]]] = None,
) -> list[dict[str, str]]:
    """Собирает список сообщений: системное (с картой) + история + текущий запрос (с опциональным содержимым файла)."""
    content = user_text.strip()
    if file_path:
        file_content = read_file_content(file_path)
        if file_content:
            content = f"[Содержимое приложенного файла]\n\n{file_content}\n\n---\n\nЗапрос пользователя: {content}"
    messages = history or []
    messages.append({"role": "user", "content": content})
    return messages


def chat_turn(
    user_text: str,
    system_fragment: str,
    file_path: Optional[str | Path] = None,
    history: Optional[list[dict[str, str]]] = None,
    model: str = "gpt-4o-mini",
) -> tuple[str, list[dict[str, str]]]:
    """Один обмен: запрос пользователя (и опционально файл) → ответ модели. Возвращает (ответ, обновлённая история)."""
    system_content = SYSTEM_BASE.format(cognitive_map=system_fragment or "(Когнитивная карта не задана.)")
    messages = [{"role": "system", "content": system_content}] + (history or [])
    new_messages = build_messages(user_text, file_path=file_path, history=[m for m in messages if m["role"] != "system"])
    # Полная история для следующего шага: system + все user/assistant
    full = [messages[0]] + messages[1:] + [{"role": "user", "content": new_messages[-1]["content"]}]
    reply = complete([{"role": "system", "content": system_content}] + full[1:], model=model)
    if reply:
        full.append({"role": "assistant", "content": reply})
    return reply, full[1:]  # без system в возвращаемой истории


def run_chat_loop(profile_path: Path = DEFAULT_PROFILE_PATH, model: str = "gpt-4o-mini") -> None:
    profile = load_profile(profile_path)
    fragment = get_system_prompt_fragment(profile)
    if not fragment:
        print("Когнитивный профиль не найден или пуст. Сначала пройди интервью: python -m interview")
        return

    print("\n=== Чат с учётом когнитивной карты ===\n")
    print("Команды: /файл <путь> — приложить файл к следующему сообщению; /выход — выход.\n")

    history: list[dict[str, str]] = []
    pending_file: Optional[str] = None

    while True:
        try:
            prompt = "Файл к сообщению: " if pending_file else "Ты: "
            line = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nВыход.")
            break

        if not line:
            continue

        if line.startswith("/выход") or line.startswith("/exit"):
            print("Выход.")
            break

        if line.startswith("/файл ") or line.startswith("/file "):
            parts = line.split(maxsplit=1)
            if len(parts) < 2 or not parts[1].strip():
                print("Укажи путь к файлу: /файл <путь>")
                continue
            pending_file = parts[1].strip()
            print(f"Будет приложен файл: {pending_file}")
            continue

        user_text = line
        file_path = pending_file
        pending_file = None

        reply, history = chat_turn(user_text, fragment, file_path=file_path, history=history, model=model)
        print("\nБот:", reply, "\n")
