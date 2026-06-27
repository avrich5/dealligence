# TASK 05 — State Vector сделки

Для: Claude Code на skufs-mac-mini.
Читать первым: CLAUDE.md → PROGRESS.md → GROUNDTRUTH.md → DECISIONS.md → этот файл.
Не смешивать с TASK 06.

## Контекст и концепция

State Vector — снимок состояния сделки на момент времени по трём ортогональным
измерениям (DECISIONS.md 2026-06-27):

  ЧТО  — предмет договора: что поставляется, на каких условиях, за что платят.
  КАК  — процесс исполнения: механизм, интерфейс, сроки, контроль.
  КТО  — состояние отношений: доверие, полномочия, позиции сторон.

Правовая рамка (NDA, SLA) — точки перегиба на временной оси, меняющие динамику
всех трёх измерений. sla_signed = точка перегиба сигмоиды обязательств.

КАК измеряется относительно последней согласованной версии PRD. Отклонение
фактического КАК от PRD → 0 — операционный критерий успеха интеграции.

Входные данные:
- `out/timeline.jsonl` — 2124 атома с phase/side/modality/about_canon
- `out/detector_results.jsonl` — статусы осей (resolved/observed_absent/unresolved)
- `config/ontology.yaml` — 74 канонические оси с описаниями
- `config/detector_config.json` — exclude_sources, closure_signals
- PRD-файлы в corpus_txt/ (9 файлов, 2026-03-19 → 2026-05-07)

## Шаг 1 — Классификация осей по измерениям (scripts/task05_1_classify_axes.py)

Вход: `config/ontology.yaml` + `out/detector_results.jsonl`
Выход: `config/axes_dimensions.json`

Применить классификацию из DECISIONS.md:

ЧТО: scope, revshare, deliverables, roi, data_sharing, data_usage, data_ownership,
  ip_ownership, capability, use_case, purpose, marketing, rebates, capital,
  trading_modes, spot_vs_futures, hedging, position_sizing, slippage_data,
  ai_model, strategy_recommendation, product_feature, exclusivity

КАК: execution_control, timeline, architecture, implementation, execution, testing,
  signal_delivery, sse_connection, user_flow, api_availability, session_lifecycle,
  latency_target, uptime, maintenance, incident_management, security, data_source,
  entry_point, sl_tp_invisibility, responsibility_split, requirements, documentation,
  resources, improvement, performance_metrics, information_provision

КТО: trust, internal_authority, cooperation, communication, meeting, team,
  contact, party, location, ma_transition, partnership

LEGAL: agreement, confidentiality, liability, dispute_resolution, term, risk,
  regulatory_compliance, governing_law, force_majeure, assignment, legal,
  remedy, platform_discretion, terminology

Формат axes_dimensions.json:
```json
{
  "what": ["scope", "revshare", ...],
  "how": ["execution_control", "timeline", ...],
  "who": ["trust", "internal_authority", ...],
  "legal": ["agreement", "confidentiality", ...]
}
```

Вывести в stdout: таблицу dimension / count / топ-3 оси по declared_count.

## Шаг 2 — Извлечение PRD-требований (scripts/task05_2_extract_prd.py)

Вход: `corpus_txt/` — PRD-файлы (фильтр по списку ниже) + `out/timeline.jsonl`
Выход: `analysis/prd_requirements.json`

PRD-файлы в хронологическом порядке:
1. `profit_radar_mvp_integration_requirements__210f26.txt` — 2026-03-19 (Влад, первые требования)
2. `profit_radar_ai_strategy_integration_prd__e90b29.txt` — 2026-04-10 (Влад, основной PRD)
3. `Agreement_discuss___ИЗМЕНЕНИЯ_В_PRD__7924b5.txt` — 2026-04-23 (правки по встрече)
4. `PRD___Vlad_Hryhoriev_short__c6503c.txt` — 2026-05-07 (сокращённая версия)
5. `wb_call_analysis_PRD___Vlad_Hryhoriev__62ba60.txt` — 2026-05-07 (анализ звонка)

Для каждого файла — LLM-вызов через orchestrator:
Промпт: «Извлеки список конкретных технических требований из этого PRD-документа.
Каждое требование — одна строка. Формат: {"requirement": "...", "axis": "...",
"side": "WB|MMI|both", "status_in_text": "proposed|agreed|rejected|unclear"}.
Только то, что явно написано. Не выводи из контекста.»

Выход: для каждого PRD-файла — список требований с осью и статусом.
Последняя версия (2026-05-07) = эталон для сравнения.

Три оси оценки LLM на этом шаге:
(1) Стоимость: ~5 вызовов × ~$0.02 = ~$0.10 из $5 лимита.
(2) Риск галлюцинаций: средний — PRD структурирован, требования явные.
    Anti-fabrication: каждое требование должно содержать цитату из raw_text.
(3) Ценность: ручное извлечение 5 файлов = 2-3 часа; LLM = 5 минут.

## Шаг 3 — Сборка State Vector (scripts/task05_3_build_state_vector.py)

Вход: `out/detector_results.jsonl` + `config/axes_dimensions.json` +
      `analysis/prd_requirements.json` + `out/timeline.jsonl`
Выход: `out/state_vector.json`

Структура State Vector:

```json
{
  "deal_id": "wb_mmi_2024",
  "as_of": "2026-06-27",
  "phase": "post_sla",
  "dimensions": {
    "what": {
      "axes": {
        "scope": {
          "status": "unresolved",
          "declared": 182,
          "done": 1,
          "signal": "Крупнейший открытый пул. Предмет интеграции не закрыт фактом.",
          "top_atoms": [...]
        },
        "revshare": {...},
        ...
      },
      "summary": "..."
    },
    "how": {
      "axes": {...},
      "prd_coverage": {
        "requirements_total": 0,
        "requirements_done": 0,
        "requirements_open": 0,
        "delta_pct": 0.0
      },
      "summary": "..."
    },
    "who": {
      "axes": {...},
      "summary": "..."
    },
    "legal": {
      "phase_anchors": {
        "nda_signed": "2026-04-09",
        "sla_signed": "2026-04-28",
        "closure": null
      },
      "summary": "..."
    }
  }
}
```

Логика `signal` для каждой оси — детерминированная, не LLM:
- resolved → «Закрыто. [N] done подтверждают исполнение.»
- observed_absent → «Объявлено, closure наступил, done не зафиксирован.»
- unresolved → «Открыто. [N] declared без closure signal.»

`prd_coverage` в измерении КАК:
- Сопоставить требования из prd_requirements.json с done-атомами по оси.
- delta_pct = (requirements_done / requirements_total) × 100.
- Цель: delta_pct → 100 (отклонение КАК от PRD → 0).

LLM вызывать только для поля `summary` каждого измерения — интерпретация
агрегированного состояния, не извлечение фактов.

## Шаг 4 — Отчёт (scripts/task05_4_state_report.py)

Вход: `out/state_vector.json`
Выход: `analysis/state_vector_report.md`

Структура отчёта:
1. Фаза сделки и точки перегиба.
2. ЧТО: топ-5 осей по declared_count, статус каждой.
3. КАК: PRD coverage + топ открытых требований.
4. КТО: trust и internal_authority — агрегированный сигнал.
5. Критические разрывы (observed_absent по всем измерениям).
6. Рекомендуемые действия — LLM на основе State Vector.

## Гейты (бинарные)

- [ ] `out/state_vector.json` содержит все три измерения (what/how/who)?
- [ ] Каждая ось в state_vector имеет статус из detector_results (не придуман)?
- [ ] prd_coverage заполнен для измерения КАК?
- [ ] signal для каждой оси — детерминированный текст, не LLM?
- [ ] LLM вызван только для summary и рекомендаций, не для фактов?
- [ ] Audit trail: для каждого значения оси — ссылка на атом-источник?

## Что НЕ делать

- Не выдумывать значения осей. Нет атома — статус unknown, не догадка.
- Не смешивать оси разных измерений в одном агрегате.
- Не использовать LLM для извлечения фактов из PRD — только структурированный
  промпт с anti-fabrication (цитата обязательна).
- Не строить State Vector без prd_coverage на оси КАК.
- Не писать скрипты в /tmp.

## Выход сессии

- `config/axes_dimensions.json`
- `analysis/prd_requirements.json`
- `out/state_vector.json`
- `analysis/state_vector_report.md`
- session-отчёт в `reports/session_YYYY-MM-DD_task05.md`
- одна строка в PROGRESS.md
