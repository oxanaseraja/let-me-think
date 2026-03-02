# -*- coding: utf-8 -*-
"""
Фаза 1: интервью — вопросы опросника + свободное описание, затем генерация когнитивной карты через LLM и сохранение профиля.
"""

from pathlib import Path

from questionnaire import (
    QUESTIONS,
    FREE_FORM_PROMPT,
    format_question_for_display,
    parse_answer_choice,
)
from profile import (
    DEFAULT_PROFILE_PATH,
    answers_to_text,
    build_profile,
    save_profile,
    get_system_prompt_fragment,
)
from llm import complete


SYSTEM_SUMMARY_PROMPT = """Ты — помощник, который по ответам пользователя на опросник и его свободному описанию формирует краткую «когнитивную карту» для другого LLM.

Задача: написать один связный фрагмент текста (2–5 абзацев), который будет вставлен в системный промпт бота-объяснятеля. По этому фрагменту бот должен понимать:
- в каком порядке подавать материал (правила/примеры, общая картина/шаги);
- какой уровень формальности и детализации предпочитает пользователь;
- как обращаться с терминами, аналогиями, повторениями;
- какие приёмы помогают (паттерны, инварианты, структуры, списки и т.п.), а что мешает.

Пиши от третьего лица («Пользователь лучше усваивает…», «Важно явно…») или в виде инструкций боту («При объяснении сначала…»). Без вводных фраз вроде «Вот когнитивная карта». Только сам текст для системного промпта."""


def run_interview(profile_path: Path = DEFAULT_PROFILE_PATH) -> bool:
    """Задаёт вопросы, собирает свободный текст, вызывает LLM для сводки, сохраняет профиль. Возвращает True при успехе."""
    print("\n=== Когнитивная карта: интервью ===\n")
    print("Ответь на вопросы, выбрав номер варианта (или введи номер + свой комментарий при желании).\n")

    answers: dict[str, str] = {}

    for i, q in enumerate(QUESTIONS, 1):
        print(format_question_for_display(q, i))
        while True:
            raw = input("Твой выбор (номер или текст): ").strip()
            choice = parse_answer_choice(raw, q)
            if choice is not None:
                answers[q.id] = choice
                break
            print("Неверный ввод, выбери номер варианта или точное значение (например rules_first).")

    print("\n" + "=" * 60)
    print(FREE_FORM_PROMPT)
    print("(Можно оставить пустым или написать несколько абзацев. Заверши ввод пустой строкой или дважды Enter.)\n")
    free_lines: list[str] = []
    while True:
        line = input()
        if line == "" and free_lines and free_lines[-1] == "":
            break
        free_lines.append(line)
    free_form = "\n".join(l for l in free_lines if l.strip()).strip()

    answers_text = answers_to_text(answers)
    user_content = "Ответы на опросник:\n\n" + answers_text
    if free_form:
        user_content += "\n\nСвободное описание пользователя:\n\n" + free_form

    print("\nГенерирую когнитивную карту...")
    fragment = complete(
        [
            {"role": "system", "content": SYSTEM_SUMMARY_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.4,
    )

    if not fragment:
        print("Не удалось получить ответ от модели. Сохраняю профиль с ручным фрагментом — его можно отредактировать в JSON.")
        fragment = (
            "Учитывай ответы пользователя из опросника и его свободное описание при объяснениях. "
            "Предпочитай структуру, паттерны и явные формулировки."
        )

    profile = build_profile(answers, free_form, fragment, profile_path=profile_path)
    save_profile(profile, profile_path)
    print(f"\nПрофиль сохранён: {profile_path}")
    print("\nФрагмент для системного промпта (начало):")
    print("-" * 40)
    print(fragment[:500] + ("..." if len(fragment) > 500 else ""))
    print("-" * 40)
    return True
