# TASK 02 — Сходимость онтологии (CONSENSUS)

Для: Claude Code. Прочитать CLAUDE.md, concept/00_CONCEPT.md, GROUNDTRUTH.md.
Не смешивать с реализацией других тасков.

## Цель
Сырая эмерджентная онтология (85 типов, 478 осей) → канон.
Канон типов: 8-12. Канон осей: ~30. Метод — как adaptive_answer_prompt_matrix
(много сырых → консенсус). Утверждение канона за Andriy ДО нормализации.

## Вход
- `out/atoms.jsonl` — 2124 атома.
- Сырые распределения типов/осей: `engine/inspect_atoms.py`.

## Шаги
1. Собрать полное распределение осей (about) с частотами и для каждой —
   список файлов, где встречается (для гейта «≥2 файла»).
2. LLM-проход (через orchestrator, agent=dealligence): кластеризовать 478 осей
   в ~30 канонических групп. Каждая группа: canonical_name + список сырых +
   суммарная частота. Сохранить как `analysis/ontology_axes_clusters.json`.
3. То же для типов → 8-12 канонических. `analysis/ontology_types_clusters.json`.
4. Показать Andriy маппинг таблицей. НЕ нормализовать до утверждения.
5. После утверждения: записать канон в `config/ontology.yaml`, добавить в atom.py
   нормализатор raw_label → canonical, прогнать по atoms.jsonl → atoms_canon.jsonl.

## Гейты (CHECKLIST «Gate TASK 02»)
- Канон осей покрывает ≥90% атомов.
- Каждая каноническая ось в ≥2 файлах.
- Маппинг утверждён Andriy до нормализации.
- Канон типов различим (нет смыслового схлопывания двух в один).

## Запреты
- Не выдумывать оси, которых нет в данных. Канон только агрегирует сырое.
- Не терять ключевые сигналы при схлопывании: data_sharing, internal_authority,
  execution_control, revshare обязаны сохраниться как отдельные оси.
- Не нормализовать до утверждения Andriy.

## Выход
- `analysis/ontology_axes_clusters.json`, `analysis/ontology_types_clusters.json`
- после утверждения: `config/ontology.yaml`, `out/atoms_canon.jsonl`
- session-отчёт в `reports/`.
