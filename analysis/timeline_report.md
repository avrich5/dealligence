# Timeline Verification Report — TASK 03 Step 4

Date: 2026-06-27

Source: /Users/andriy/dealligence/out/timeline.jsonl

Total atoms: 2124


## Phase distribution

- `post_sla`: 584 (27.5%)
- `pre_sla`: 989 (46.6%)
- `unknown`: 551 (25.9%)


## Timestamp confidence

- `exact`: 1194 (56.2%)
- `file_order`: 551 (25.9%)
- `inferred`: 379 (17.8%)


## Gate results

### Warnings

- WARNING: 551 atoms (25.9%) have phase=unknown (threshold 20.0%).



## Files with most undated atoms (file_order)

- PRD___Vlad_Hryhoriev_short__c6503c.txt: 76
- Ageement_discuss___1__47b7f4.txt: 64
- Влад_синк__0fcba7.txt: 57
- Ageement_discuss___3__451e87.txt: 46
- WhiteBit___ProfitRadar_MVP__Claude__55d82d.txt: 46
- 5_мин_с_Владом__34406e.txt: 43
- Agreement_discuss___ПЛАНЫ_НА_СОТРУДНИЧЕСТВО__137cfe.txt: 35
- Agreement_discuss___ИЗМЕНЕНИЯ_В_PRD__7924b5.txt: 31
- Agreement_discuss___ИЗМЕНЕНИЯ_В_ДОГОВОРЕ_О_СОТРУДНИЧЕСТВЕ__99236d.txt: 30
- WB_Dima_Vlad__aad065.txt: 27


## Recommendations for Andriy

- Review atoms with `phase=unknown` — these have no timestamp and no file date.
- phase=unknown exceeds 20.0% threshold. Consider checking undated files manually or adding file_date overrides.
- 551 atoms have no date at all (file_order). Check top files above and consider assigning approximate dates.
