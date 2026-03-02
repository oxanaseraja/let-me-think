# -*- coding: utf-8 -*-
"""
Точка входа: интервью (если нет профиля) или чат с когнитивной картой.
"""

import argparse
from pathlib import Path

from profile import load_profile, DEFAULT_PROFILE_PATH
from interview import run_interview
from chat import run_chat_loop


def main() -> None:
    parser = argparse.ArgumentParser(description="Чат-бот с когнитивной картой: интервью и чат.")
    parser.add_argument(
        "mode",
        nargs="?",
        choices=["interview", "chat", "auto"],
        default="auto",
        help="interview — только пройти опросник; chat — только чат; auto — чат, если есть профиль, иначе интервью",
    )
    parser.add_argument(
        "--profile",
        type=Path,
        default=DEFAULT_PROFILE_PATH,
        help="Путь к файлу когнитивного профиля",
    )
    args = parser.parse_args()

    if args.mode == "interview":
        run_interview(args.profile)
        return

    if args.mode == "chat":
        run_chat_loop(args.profile)
        return

    # auto
    profile = load_profile(args.profile)
    if not profile or not profile.get("system_prompt_fragment"):
        run_interview(args.profile)
        print("\nТеперь можно запустить чат: python main.py chat\n")
    else:
        run_chat_loop(args.profile)


if __name__ == "__main__":
    main()
