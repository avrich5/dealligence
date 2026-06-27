# TASK 04 — Детектор declared/observed

Для: Claude Code на skufs-mac-mini.
Читать первым: CLAUDE.md → PROGRESS.md → GROUNDTRUTH.md → DECISIONS.md → этот файл.
Не смешивать с TASK 05.

## Контекст

Есть `out/timeline.jsonl` — 2124 атома с полями:
  deal_id, seq, timestamp, timestamp_confidence, phase, side, type_canon,
  about_canon, modality, raw_text, source_file.

Модальности: declared 2047, done 68, observed_absent 3, denied 3, unknown 3.
Детектор ищет declared-атомы без парного done по той же оси позже по таймлайну.

Верифицированные кандидаты из GROUNDTRUTH §7:
- revshare: 101 declared, 1 done → ожидается observed_absent
- execution_control: 187 declared, 5 done → ожидается расхождение по стороне

## Архитектура (из DECISIONS.md и GROUNDTRUTH §6)

Детектор трёхпозиционный:
- `resolved` — declared + парный done после него по seq
- `observed_absent` — declared + closure signal + нет парного done
- `unresolved` — declared + нет closure signal (открытое обязательство)

Closure signal для оси: подписанный документ, дата go-live, технический факт,
явный отказ. Для revshare closure = SLA подписан (sla_signed anchor).
Для execution_control closure = PRD от Влада (2026-05-07).

## Конфигурация

`config/detector_config.json` — создать перед запуском:

```json
{
  "deal_id": "wb_mmi_2024",
  "exclude_sources": [
    "1853__AGR_Profit_Radar_SLA_IN_RPOCESS_r2__3562bc.txt",
    "1853__AGR_Profit_Radar_SLA_IN_RPOCESS_r2_RU__b142f1.txt",
    "1853__AGR_Profit_Radar_SLA_IN_RPOCESS_r3__98e320.txt",
    "DRAFT__Profit_Radar_SLA_REVSHARE__d79067.txt",
    "DRAFT__Profit_Radar_SLA_REVSHARE___PR_notes__e14d43.txt",
    "Profit_Radar_SLA_with_final_edits__c52ce4.txt",
    "Profit_Radar_SLA_with_sign__2ec5aa.txt"
  ],
  "closure_signals": {
    "revshare": {"type": "anchor", "anchor": "sla_signed"},
    "execution_control": {"type": "file_date", "date": "2026-05-07"},
    "data_sharing": {"type": "anchor", "anchor": "sla_signed"},
    "scope": {"type": "none"}
  },
  "min_declared_count": 2
}
```

Логика exclude_sources: SLA-черновики содержат только declared по природе
(юридический текст), включение в детектор искусственно завышает unresolved.
Решение зафиксировано в DECISIONS.md 2026-06-27.

## Шаг 1 — Построение детектора (scripts/task04_1_build_detector.py)

Вход: `out/timeline.jsonl` + `config/detector_config.json`
Выход: `out/detector_results.jsonl`

Алгоритм для каждой оси (about_canon):
1. Взять все declared-атомы по оси (исключая exclude_sources).
2. Для каждого declared — искать done-атом по той же оси с seq > declared.seq.
3. Определить closure_signal для оси из конфига.
4. Присвоить статус:
   - есть парный done → `resolved`
   - нет парного done + closure_signal пройден → `observed_absent`
   - нет парного done + нет closure_signal → `unresolved`

Формат записи в detector_results.jsonl:
```json
{
  "deal_id": "wb_mmi_2024",
  "about_canon": "revshare",
  "status": "observed_absent",
  "declared_count": 101,
  "done_count": 1,
  "resolved_count": 1,
  "observed_absent_count": 0,
  "unresolved_count": 100,
  "closure_signal": "sla_signed",
  "closure_date": "2026-04-28",
  "top_declared": [...],
  "top_done": [...]
}
```

Вывести в stdout: таблицу осей, отсортированную по declared_count desc.
Топ-10 осей по числу declared. Для каждой: статус, declared/done counts.

## Шаг 2 — Верификация кандидатов (scripts/task04_2_verify_candidates.py)

Вход: `out/detector_results.jsonl` + `out/timeline.jsonl`
Выход: `analysis/detector_report.md`

Для топ-5 осей по declared_count:
- Показать по 3 примера declared (raw_text + source_file + seq)
- Показать все done (raw_text + source_file + seq)
- Вывести вывод детектора (статус + обоснование)

Проверить верифицированные кандидаты из GROUNDTRUTH §7:
- revshare: ожидается observed_absent
- execution_control: ожидается расхождение declared vs done по стороне

Если результат расходится с GROUNDTRUTH — выделить как UNEXPECTED и
не корректировать автоматически: требует решения Andriy.

## Шаг 3 — Парето-тест (scripts/task04_3_pareto_test.py)

Вход: `out/detector_results.jsonl` + `GROUNDTRUTH.md` (§7)
Выход: stdout

Взять топ-3 сигнала детектора по критичности (observed_absent > unresolved,
внутри — по declared_count).

Для каждого проверить: упомянута ли эта ось и этот статус в GROUNDTRUTH §7
до запуска детектора?

Вывести:
- KNOWN: ось была в GROUNDTRUTH до запуска
- NEW: ось не была в GROUNDTRUTH — детектор добавил ценность

Если ≥1 NEW — Парето-критерий выполнен (зафиксировано в DECISIONS.md 2026-06-27).

## Гейты (бинарные)

- [ ] `out/detector_results.jsonl` содержит записи для всех осей с declared_count ≥ 2?
- [ ] revshare получил статус observed_absent (верификация GROUNDTRUTH §7)?
- [ ] execution_control показывает расхождение declared/done?
- [ ] Ни один атом из exclude_sources не попал в подсчёт?
- [ ] Парето-тест выполнен: выведен результат KNOWN/NEW для топ-3 сигналов?

## Что НЕ делать

- Не корректировать GROUNDTRUTH автоматически — только фиксировать расхождения.
- Не добавлять новые closure_signals без решения Andriy.
- Не объединять declared и done разных осей (scope ≠ execution_control).
- Не считать SLA-черновики — они в exclude_sources.
- Не писать скрипты в /tmp.

## Выход сессии

- `config/detector_config.json`
- `out/detector_results.jsonl`
- `analysis/detector_report.md`
- session-отчёт в `reports/session_YYYY-MM-DD_task04.md`
- одна строка в PROGRESS.md
