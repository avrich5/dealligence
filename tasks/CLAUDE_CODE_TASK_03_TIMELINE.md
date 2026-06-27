# TASK 03 — Таймлайн атомов

Для: Claude Code на skufs-mac-mini.
Читать первым: CLAUDE.md → GROUNDTRUTH.md → DEV_PLAN.md → этот файл.
Не смешивать с реализацией TASK 04.

## Контекст

Есть 2124 атома в `out/atoms_canon.jsonl` с полями about_canon / type_canon.
Атомы не упорядочены во времени — каждый привязан к файлу, но не к дате.
Задача: присвоить каждому атому временну́ю позицию и фазу сделки.

Выход таймлайна — основа для:
- детектора declared/observed (TASK 04)
- паттернов поведения сторон (GROUP BY deal_id / phase / side / type_canon)
- State Vector в динамике (TASK 06)

## Схема таймлайн-атома

Атом из atoms_canon.jsonl расширяется полями:

```json
{
  "deal_id": "wb_mmi_2024",
  "atom_id": "...",
  "source_file": "...",
  "timestamp": "2024-03-15",
  "timestamp_confidence": "exact | inferred | file_order",
  "seq": 1842,
  "phase": "pre_sla | post_sla | post_closure | unknown",
  "speaker": "...",
  "side": "MMI | WB | unknown",
  "type_canon": "...",
  "about_canon": "...",
  "modality": "...",
  "raw_text": "..."
}
```

**Обязательные требования к схеме:**
- `deal_id` — поле первого класса, не путь к файлу и не имплицитный синглтон.
  Значение для WB-кейса: `"wb_mmi_2024"`. При N>1 сделок — GROUP BY deal_id.
- `timestamp_confidence` — обязателен. Нет даты → не выдумывать, писать
  `"file_order"` с порядковым seq внутри файла.
- `phase` — выводится из timestamp относительно anchor-дат (см. ниже).
  Нет timestamp → phase=unknown, не угадывать.
- `seq` — глобальный порядковый номер по (timestamp, file_order, atom_order).
  Монотонный, без дыр внутри одного файла.

## Шаг 1 — Извлечение дат (scripts/task03_1_extract_dates.py)

Вход: `corpus_txt/` (все .txt файлы) + `out/atoms_canon.jsonl`
Выход: `analysis/file_dates.json`

Для каждого файла из корпуса:
- Извлечь все явные даты из текста (regex: YYYY-MM-DD, DD.MM.YYYY, месяц YYYY).
- Определить `file_date`: самую раннюю дату документа (не дату упоминания события).
  Если дат нет — null.
- Поле `date_confidence`: "explicit" (дата найдена в шапке/метаданных),
  "inferred" (дата выведена из контекста), "none".
- Не вызывать LLM на этом шаге — только regex + эвристики.

Вывести в stdout: таблицу filename / file_date / date_confidence / dates_found_count.
Файлы без дат — выделить отдельным списком.

## Шаг 2 — Anchor-даты (ручной шаг, Andriy)

После шага 1 Andriy проверяет и устанавливает anchor-даты в `config/timeline_anchors.json`:

```json
{
  "deal_id": "wb_mmi_2024",
  "anchors": {
    "sla_signed": "YYYY-MM-DD",
    "nda_signed": "YYYY-MM-DD",
    "first_contact": "YYYY-MM-DD",
    "closure": null
  },
  "phases": {
    "pre_sla":       {"from": null,         "to": "sla_signed"},
    "post_sla":      {"from": "sla_signed", "to": "closure"},
    "post_closure":  {"from": "closure",    "to": null}
  }
}
```

Claude Code создаёт шаблон этого файла после шага 1.
Andriy заполняет даты вручную — он знает, когда подписан SLA/NDA.
Без этого шага шаг 3 не запускается.

## Шаг 3 — Сборка таймлайна (scripts/task03_3_build_timeline.py)

Вход: `out/atoms_canon.jsonl` + `analysis/file_dates.json` +
      `config/timeline_anchors.json`
Выход: `out/timeline.jsonl`

Логика присвоения timestamp каждому атому:
1. Если в raw_text атома есть явная дата — использовать её (timestamp_confidence=exact).
2. Иначе — взять file_date из file_dates.json (timestamp_confidence=inferred).
3. Если file_date=null — timestamp=null, timestamp_confidence=file_order.

Логика seq:
- Сортировать по (timestamp nulls_last, source_file, atom_order_within_file).
- Присвоить seq 1..N монотонно.

Логика phase:
- Вычислить по timestamp относительно anchors из timeline_anchors.json.
- timestamp=null → phase="unknown".

Дополнить каждый атом полем deal_id="wb_mmi_2024".

Вывести в stdout:
- Распределение по phase: count и % атомов в каждой фазе.
- Количество атомов с timestamp_confidence=exact / inferred / file_order.
- Топ-5 файлов с наибольшим числом атомов без даты.

## Шаг 4 — Верификация (scripts/task03_4_verify_timeline.py)

Вход: `out/timeline.jsonl`
Выход: stdout + `analysis/timeline_report.md`

Проверки:
- [ ] Все 2124 атома присутствуют (count).
- [ ] seq монотонен, нет дыр внутри файла.
- [ ] deal_id заполнен у всех атомов.
- [ ] phase="unknown" не превышает 20% (если больше — предупреждение, не ошибка).
- [ ] Ни один атом не имеет timestamp позже сегодняшней даты.
- [ ] Для каждой фазы: есть хотя бы один атом (кроме post_closure если closure=null).

Вывести timeline_report.md: сводка по фазам, список подозрительных атомов
(противоречие timestamp vs фаза), рекомендации для шага Andriy.

## Гейты (бинарные)

После завершения всех шагов:
- [ ] `out/timeline.jsonl` содержит 2124 записи?
- [ ] Поле `deal_id` присутствует у каждого атома?
- [ ] Поле `phase` присутствует у каждого атома (включая "unknown")?
- [ ] `timestamp_confidence` присутствует у каждого атома?
- [ ] `seq` уникален и монотонен?
- [ ] Anchor-даты установлены Andriy и зафиксированы в config/timeline_anchors.json?

## Что НЕ делать

- Не выдумывать даты. Нет даты → timestamp=null, timestamp_confidence=file_order.
- Не угадывать phase без anchor-дат от Andriy.
- Не вызывать LLM для извлечения дат — только детерминированный regex.
- Не хардкодить deal_id в логике — читать из timeline_anchors.json.
- Не запускать шаг 3 до получения заполненного timeline_anchors.json.
- Не писать скрипты в /tmp.

## Выход сессии

- `analysis/file_dates.json`
- `config/timeline_anchors.json` (шаблон от Claude Code, даты от Andriy)
- `out/timeline.jsonl`
- `analysis/timeline_report.md`
- session-отчёт в `reports/session_YYYY-MM-DD_task03.md`
- одна строка в PROGRESS.md
