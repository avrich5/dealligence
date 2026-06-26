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

## 5. Что НЕ установлено (честные пробелы)
- Подписана ли встречная сторона SLA — неизвестно (копия не прислана). Гипотеза
  Andriy: юристы не отдают из-за двойного смысла для регулятора. UNTESTED.
- observed_absent почти пуст (3) — детектор declared/observed ещё не построен.
  Текущие 3 — внутрифайловые, не межвременные.
