# PROGRESS — состояние проекта (единый источник «где мы»)

Обновляется по одной строке за сессию. Статус: ✅ DONE | 🔄 IN PROGRESS | ⏳ PENDING | ❌ BLOCKED.

| Этап | Критерий DONE (бинарный) | Статус | Дата | Доказ |
|---|---|---|---|---|
| TASK 01 — Setup | Структура, git, remote, CLAUDE/README/concept | 🔄 IN PROGRESS | 2026-06-26 | каркас поднят, remote pending |
| Ingest | Все форматы → corpus_txt, дедуп по stem | ✅ DONE | 2026-06-26 | 34 файла, _manifest.tsv |
| Атомизация корпуса | Весь корпус → out/atoms.jsonl, anti-fabrication | ✅ DONE | 2026-06-26 | 2124 атома, $0.1155 |
| TASK 02 — Сходимость онтологии | 478 осей → канон ~30, 85 типов → 8-12, утверждено Andriy | ⏳ PENDING | — | — |
| TASK 03 — Таймлайн | Все атомы с timestamp/порядком, разложены по времени | ⏳ PENDING | — | — |
| TASK 04 — Детектор declared/observed | ≥1 declared без парного факта найден и верифицирован | ⏳ PENDING | — | — |
| TASK 05 — causal_rules сделки | Каждая ось State Vector ← атомы, audit trail | ⏳ PENDING | — | — |
| TASK 06 — State Vector + траектория | Вектор на сегодня + динамика по таймлайну | ⏳ PENDING | — | — |

**Текущий блокер:** remote github не создан (нужен пустой репо avrich5/dealligence или PAT).
**Следующий шаг:** TASK 02 (сходимость онтологии) — данные готовы (2124 атома).
