# -*- coding: utf-8 -*-
"""
Серьёзный опросник для построения когнитивной карты пользователя.
Ответы используются для генерации фрагмента системного промпта.
"""

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class QuestionOption:
    value: str
    label: str
    description: Optional[str] = None  # для пояснения выбора (опционально)


@dataclass
class Question:
    id: str
    text: str
    options: list[QuestionOption]
    category: str = ""  # для группировки при анализе


QUESTIONS: list[Question] = [
    # --- Порядок и структура подачи материала ---
    Question(
        id="order_rules_vs_examples",
        category="order",
        text="Как тебе проще входить в новую тему?",
        options=[
            QuestionOption("rules_first", "Сначала правило/определение, потом примеры"),
            QuestionOption("examples_first", "Сначала примеры или задача, потом обобщение"),
            QuestionOption("alternating", "Чередование: мини-правило → пример → следующее правило"),
            QuestionOption("depends", "Зависит от темы, но важно явно обозначать «сейчас правило / сейчас пример»"),
        ],
    ),
    Question(
        id="abstraction_level",
        category="abstraction",
        text="Что тебе важнее увидеть в первую очередь при новом понятии?",
        options=[
            QuestionOption("pattern_invariant", "Паттерн, инвариант, общая структура — «как это устроено в целом»"),
            QuestionOption("concrete_instance", "Конкретный работающий пример или один случай"),
            QuestionOption("both_explicit", "И то и другое, но чтобы было явно разделено (сначала структура, потом пример)"),
            QuestionOption("depends_topic", "Зависит от темы (математика — структура, бытовое — пример)"),
        ],
    ),
    Question(
        id="big_picture_vs_steps",
        category="structure",
        text="Как тебе удобнее воспринимать объяснение процесса или алгоритма?",
        options=[
            QuestionOption("big_picture_first", "Сначала общая картина/цель, потом шаги"),
            QuestionOption("steps_first", "Сразу по шагам, общая картина сложится сама"),
            QuestionOption("explicit_both", "Явно и картина, и шаги; без «опустим детали» в середине"),
            QuestionOption("visual_flow", "Схема или поток (flow), текст — только пояснение к ней"),
        ],
    ),
    Question(
        id="structure_format",
        category="structure",
        text="Какой формат изложения тебе удобнее?",
        options=[
            QuestionOption("lists_headers", "Списки, пункты, подзаголовки — явная структура"),
            QuestionOption("narrative", "Связный текст-нарратив, без избыточных списков"),
            QuestionOption("mixed", "Смешанно: заголовки и списки для фактов, абзацы для связок и смысла"),
            QuestionOption("depends_length", "Зависит от объёма: короткое — текст, длинное — обязательно структура"),
        ],
    ),
    # --- Язык и точность ---
    Question(
        id="jargon",
        category="language",
        text="Как относишься к терминам и жаргону?",
        options=[
            QuestionOption("use_but_define", "Можно использовать, но первый раз — краткое определение или пример"),
            QuestionOption("plain_prefer", "Предпочитаю обычные слова; термины только если без них никак"),
            QuestionOption("terms_ok", "Термины нормально, могу гуглить; важнее точность формулировок"),
            QuestionOption("glossary_love", "Люблю, когда в конце или сбоку есть мини-глоссарий по теме"),
        ],
    ),
    Question(
        id="formality_math",
        category="language",
        text="В математике/формальных темах что ближе?",
        options=[
            QuestionOption("formal_first", "Сначала формальное определение/формула, потом словами"),
            QuestionOption("intuition_first", "Сначала интуиция/картинка, потом формализация"),
            QuestionOption("parallel", "Оба параллельно: «формально это X, то есть по сути Y»"),
            QuestionOption("no_math_skip", "Математику часто пропускаю; нужны словесные выводы и итоги"),
        ],
    ),
    Question(
        id="length_detail",
        category="detail",
        text="Какой объём объяснения тебе комфортнее?",
        options=[
            QuestionOption("concise", "Кратко: суть, один пример, без воды"),
            QuestionOption("thorough", "Подробно: все шаги, подводные камни, почему не иначе"),
            QuestionOption("tiered", "Сначала краткая суть, потом «если нужно подробнее» — раскрыть"),
            QuestionOption("depends_mood", "Зависит от настроения и срочности; лучше спросить «кратко или подробно»"),
        ],
    ),
    Question(
        id="repetition",
        category="detail",
        text="Нужно ли повторять ключевые выводы в конце блока?",
        options=[
            QuestionOption("yes_always", "Да, кратко повторить главное после объяснения"),
            QuestionOption("no_annoying", "Нет, повтор меня отвлекает"),
            QuestionOption("only_long", "Только если объяснение длинное (больше 2–3 абзацев)"),
            QuestionOption("bullet_summary", "Лучше отдельным списком «что мы узнали» в конце"),
        ],
    ),
    # --- Аналогии и связи ---
    Question(
        id="analogies",
        category="connections",
        text="Как относишься к аналогиям и сравнениям с другими областями?",
        options=[
            QuestionOption("love", "Очень помогают: «это как X в другой области»"),
            QuestionOption("careful", "Нормально, но с оговоркой «не совсем то же»"),
            QuestionOption("distract", "Часто сбивают: начинаю думать про аналогию, а не про тему"),
            QuestionOption("domain_specific", "Зависит от области: в программировании — да, в математике — осторожнее"),
        ],
    ),
    Question(
        id="connections_previous",
        category="connections",
        text="Важно ли явно связывать новое с уже изученным?",
        options=[
            QuestionOption("very", "Да, очень: «это обобщение того, что мы видели в X»"),
            QuestionOption("sometimes", "Иногда полезно, но не обязательно каждый раз"),
            QuestionOption("prefer_fresh", "Предпочитаю воспринимать тему с нуля, без отсылок"),
            QuestionOption("depends", "Зависит от темы: если продолжение — да, если новая ветка — не обязательно"),
        ],
    ),
    # --- Ошибки и неопределённость ---
    Question(
        id="mistakes_boundaries",
        category="meta",
        text="Нужно ли явно говорить «где легко ошибиться» и «где это не работает»?",
        options=[
            QuestionOption("yes_essential", "Да, это обязательно: типичные ошибки и границы применимости"),
            QuestionOption("yes_brief", "Да, но кратко, не раздувая"),
            QuestionOption("optional", "По желанию, не критично"),
            QuestionOption("after_basics", "Сначала база, потом отдельно «подводные камни»"),
        ],
    ),
    Question(
        id="uncertainty",
        category="meta",
        text="Как формулировать то, в чём нет полной определённости?",
        options=[
            QuestionOption("explicit_uncertain", "Явно: «здесь нет единого мнения» / «зависит от контекста»"),
            QuestionOption("one_view_ok", "Можно дать одну точку зрения, но не выдавать за единственную"),
            QuestionOption("avoid_uncertain", "Лучше не углубляться в спорное, пока база не твёрдая"),
            QuestionOption("show_alternatives", "Показать 2–3 подхода и коротко сравнить"),
        ],
    ),
    # --- Интерактив и темп ---
    Question(
        id="pace",
        category="interaction",
        text="Как тебе удобнее получать длинное объяснение?",
        options=[
            QuestionOption("chunks", "Небольшими порциями с паузами «понятно? идём дальше»"),
            QuestionOption("whole_then_questions", "Целиком, потом вопросы по непонятному"),
            QuestionOption("optional_dig_deeper", "Базовый уровень сразу, с возможностью «раскрой подробнее» по пунктам"),
            QuestionOption("depends", "Зависит от сложности и усталости"),
        ],
    ),
    Question(
        id="questions_back",
        category="interaction",
        text="Нужно ли, чтобы бот периодически проверял понимание вопросами?",
        options=[
            QuestionOption("yes_often", "Да, время от времени: «как бы ты сформулировал своими словами?»"),
            QuestionOption("yes_end", "В конце темы — резюмирующий вопрос или задачка"),
            QuestionOption("no_trust", "Нет, доверяю себе задать вопрос, если что"),
            QuestionOption("optional", "Опционально: «хочешь проверить понимание?»"),
        ],
    ),
    # --- Специфичные «фишки» (паттерны, инварианты и т.д.) ---
    Question(
        id="patterns_explicit",
        category="patterns",
        text="Насколько важно явно называть паттерны и инварианты?",
        options=[
            QuestionOption("very_central", "Очень: для меня это центральный способ понимания"),
            QuestionOption("helpful", "Полезно, но не обязательно каждый раз"),
            QuestionOption("sometimes", "Иногда помогает, иногда отвлекает"),
            QuestionOption("prefer_concrete", "Предпочитаю конкретику; паттерны выведу сам при необходимости"),
        ],
    ),
    Question(
        id="definitions_vs_use",
        category="patterns",
        text="Что первично при новом понятии?",
        options=[
            QuestionOption("definition_strict", "Чёткое определение, потом примеры использования"),
            QuestionOption("use_then_refine", "Как используется / что с ним делают, потом уточнение определения"),
            QuestionOption("both_side_by_side", "Определение и пример в одной связке, не разносить"),
            QuestionOption("depends", "Зависит: бытовые понятия — от использования, технические — от определения"),
        ],
    ),
]

# Свободное поле — не вопрос из списка, а отдельная подпись при сохранении
FREE_FORM_PROMPT = (
    "Опиши своими словами, как тебе удобнее всего объясняют новое: что помогает, что мешает, "
    "какие приёмы или формулировки тебе особенно заходят. Можно про паттерны, инварианты, структуры, "
    "примеры из твоего опыта — всё, что считаешь важным для твоей «когнитивной карты»."
)


def get_question_by_id(qid: str) -> Question | None:
    for q in QUESTIONS:
        if q.id == qid:
            return q
    return None


def get_options_for_question(qid: str) -> list[QuestionOption]:
    q = get_question_by_id(qid)
    return q.options if q else []


def format_question_for_display(q: Question, index: int) -> str:
    lines = [f"\n[{index}/{len(QUESTIONS)}] {q.text}", ""]
    for i, opt in enumerate(q.options, 1):
        lines.append(f"  {i}. {opt.label}")
    lines.append("")
    return "\n".join(lines)


def parse_answer_choice(raw: str, q: Question) -> str | None:
    """Возвращает value выбранной опции или None при неверном вводе."""
    raw = raw.strip()
    if not raw:
        return None
    # Попытка по номеру 1..N
    try:
        n = int(raw)
        if 1 <= n <= len(q.options):
            return q.options[n - 1].value
    except ValueError:
        pass
    # Попытка по value (например rules_first)
    for opt in q.options:
        if opt.value == raw:
            return opt.value
    return None
