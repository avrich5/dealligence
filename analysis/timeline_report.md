# Timeline Verification Report — TASK 03 Step 4

Date: 2026-06-27

Source: /Users/andriy/dealligence/out/timeline.jsonl

Total atoms: 2124


## Phase distribution

- `post_sla`: 40 (1.9%)
- `pre_sla`: 877 (41.3%)
- `unknown`: 1207 (56.8%)


## Timestamp confidence

- `exact`: 538 (25.3%)
- `file_order`: 1207 (56.8%)
- `inferred`: 379 (17.8%)


## Gate results

### Warnings

- WARNING: 1207 atoms (56.8%) have phase=unknown (threshold 20.0%).



## Files with most undated atoms (file_order)

- 1853__AGR_Profit_Radar_SLA_IN_RPOCESS_r2__3562bc.txt: 116
- 1853__AGR_Profit_Radar_SLA_IN_RPOCESS_r2_RU__b142f1.txt: 115
- Profit_Radar_SLA_with_final_edits__c52ce4.txt: 110
- 1853__AGR_Profit_Radar_SLA_IN_RPOCESS_r3__98e320.txt: 105
- DRAFT__Profit_Radar_SLA_REVSHARE__d79067.txt: 103
- Profit_Radar_SLA_with_sign__2ec5aa.txt: 98
- PRD___Vlad_Hryhoriev_short__c6503c.txt: 76
- Ageement_discuss___1__47b7f4.txt: 64
- Влад_синк__0fcba7.txt: 57
- Ageement_discuss___3__451e87.txt: 46


## Recommendations for Andriy

- Review atoms with `phase=unknown` — these have no timestamp and no file date.
- phase=unknown exceeds 20.0% threshold. Consider checking undated files manually or adding file_date overrides.
- 1207 atoms have no date at all (file_order). Check top files above and consider assigning approximate dates.
