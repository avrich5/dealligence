# GROUNDTRUTH — зафиксированная истина

Проверено по корпусу и коду 2026-06-26. Источник: ~/dealligence/ на skufs.

## 1. Корпус
- Источник: `~/dealligence/corpus_raw/` (43 файла, доставлены с MacBook из
  `/Users/andriy/Downloads/WB relashionships history/`).
- Нормализовано: `corpus_txt/` 34 файла. Манифест: `corpus_txt/_manifest.tsv`.
- Не извлечено: `WB relashionships history.pdf` (пустой скан, pdfminer 15 знаков),
  `.key` (презентация, LibreOffice txt-экспорт не сработал). Оба — сводки,
  контент дублируется. Дубли по stem (4) отброшены намеренно.

## 2. Атомы
- Мастер: `out/atoms.jsonl`, 2124 атома, 34 файла.
- Стоимость прогона: $0.1155, 70 LLM-вызовов, провайдер deepseek-chat.
- Схема атома: `engine/atom.py`. modality — единственный закрытый словарь.
- Anti-fabrication: `engine/atomizer.py` `_norm()` + проверка вхождения raw_text.

## 3. Сырая онтология (до сходимости)
- Типы: 85 уникальных. Топ: fact 609, commitment 238, claim 206, boundary 152.
- Оси (about): 478 уникальных. Топ: scope 282, execution_control 192,
  data_sharing 144, revshare 102, timeline 91, exclusivity 42, trust 41,
  internal_authority 15.
- modality: declared 2047, done 68, observed_absent 3, denied 3, unknown 3.

## 4. Ключевые факты сделки (по корпусу, не по памяти)
- SLA подписан только MMI-стороной. Подписи Носова нет, Effective Date пуст.
  Источник: `Profit Radar SLA_with_sign.pdf` стр.9.
- revshare 50% Net Trading Commission — текст SLA §5.1.
- reg.number Clear White: стр.1 = 75407221, стр.9 = 72229468 (расхождение).
- «не везде я могу последнее слово иметь» — Дима, `Дима синк.txt`.
- user_id/portfolio snapshot: устное согласие WB есть, в запросах не наблюдается.
  Источник: устное свидетельство Andriy. В корпусе текстово НЕ подтверждено.
  confidence_source=oral_andriy. Это гипотеза для детектора, не факт.
- sla_signed: 2026-04-28. Источник: oral_andriy + corroborating mtime обоих
  оригинальных файлов (Profit Radar SLA_with final edits.pages и
  Profit Radar SLA_with_sign.pdf — Apr 28 17:50 в corpus_raw на MacBook).
  Effective Date в тексте пуст — corpus-grounded дата отсутствует.
  Использовать в timeline_anchors.json с date_confidence="inferred".

## 5. Что НЕ установлено (честные пробелы)
- Подписана ли встречная сторона SLA — неизвестно (копия не прислана). Гипотеза
  Andriy: юристы не отдают из-за двойного смысла для регулятора. UNTESTED.
- observed_absent почти пуст (3) — детектор declared/observed ещё не построен.
  Текущие 3 — внутрифайловые, не межвременные.

## 6. Архитектура детектора declared/observed (сессия 2026-06-26)
Детектор трёхпозиционный, не бинарный:
- `resolved`: declared + парный done после него (есть closure signal)
- `observed_absent`: declared + closure signal + нет done
- `unresolved`: declared + нет closure signal (сделка открыта, факт не подтверждён)

Большинство из 432 осей без done — это `unresolved`, не `observed_absent`.
`unresolved` по критическим осям сам по себе информативен для переговорщика.

Closure signal — артефакт играющий роль дедлайна или подтверждения:
подписанный документ, дата go-live, технический факт, явный отказ.

## 7. Верифицированные кандидаты на разрыв (corpus-grounded, сессия 2026-06-26)
- revshare: 101 declared, 1 done («50 на 50 звучало конкретно на комитете»,
  WB__3__36b676.txt). Closure signal: SLA §5.1. Ни одного done по факту
  расчёта/выплаты. Статус: observed_absent (контракт подписан, механизм не запущен).
- execution_control: 187 declared, 5 done. Declared: «execution полностью на стороне
  MMI, нам только один API-ключ нужен». Done: WB задеплоил собственный executor
  внутри своей инфраструктуры (wb_call_analysis_PRD___Vlad_Hryhoriev__62ba60.txt).
  Расхождение по стороне исполнения — обе части corpus-grounded.
- «то, что не присылает статус апдейта, наверное, вот это минус большой» —
  Дима, Дима_синк__b1a300.txt. modality: declared | objection | side: MMI.
  Атрибуция: говорит Дима (WB), не Andriy. Факт подтверждён поиском по corpus.
