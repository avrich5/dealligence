# Timeline Verification Report — TASK 03 Step 4

Date: 2026-06-27

Source: /Users/andriy/dealligence/out/timeline.jsonl

Total atoms: 2124


## Phase distribution

- `post_sla`: 775 (36.5%)
- `pre_sla`: 1185 (55.8%)
- `unknown`: 164 (7.7%)


## Timestamp confidence

- `exact`: 1581 (74.4%)
- `file_order`: 164 (7.7%)
- `inferred`: 379 (17.8%)


## Gate results

All gates passed. No warnings.


## Files with most undated atoms (file_order)

- 5_мин_с_Владом__34406e.txt: 43
- Agreement_discuss___ПЛАНЫ_НА_СОТРУДНИЧЕСТВО__137cfe.txt: 35
- Agreement_discuss___ИЗМЕНЕНИЯ_В_PRD__7924b5.txt: 31
- Agreement_discuss___ИЗМЕНЕНИЯ_В_ДОГОВОРЕ_О_СОТРУДНИЧЕСТВЕ__99236d.txt: 30
- Что_WhiteBIT_на_самом_деле_просит__1__e714fa.txt: 25


## Recommendations for Andriy

- Review atoms with `phase=unknown` — these have no timestamp and no file date.
- 164 atoms have no date at all (file_order). Check top files above and consider assigning approximate dates.
