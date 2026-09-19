# Content Coverage by AMC Blueprint Area

Generated from the conditions spine (`conditions` table + `condition_id` links).
Regenerate with: `python scripts/content_reconciliation.py` (live counts) after any
seed/backfill run. Raw JSON snapshots live under `data/**/_reports/` (gitignored).

**Live DB summary** — 410 conditions across 13 specialties; 1,620 MCQs + 175 OSCEs +
26 personas + 4 EMR cases linked.

| Blueprint area | MCQ | OSCE | Persona | EMR |
|---|---|---|---|---|
| Mental Health | 593 | 18 | 1 | 0 |
| Cardiovascular Medicine | 327 | 50 | 9 | 1 |
| Gastroenterology | 184 | 25 | 0 | 0 |
| General Practice | 159 | 18 | 0 | 0 |
| Respiratory Medicine | 144 | 13 | 16 | 3 |
| Endocrinology | 108 | 0 | 0 | 0 |
| Neurology | 84 | 14 | 0 | 0 |
| Child Health | 20 | 0 | 0 | 0 |
| Emergency Medicine | 1 | 0 | 0 | 0 |
| Surgery & Procedures | 0 | 23 | 0 | 0 |
| Women's Health | 0 | 14 | 0 | 0 |

## Known coverage gaps (drive content generation)
- **Surgery & Procedures, Women's Health**: OSCE-only — no MCQs yet.
- **Endocrinology, Child Health, Emergency**: no OSCEs / thin MCQs.
- **EMR cases**: 4/43 linked — most acute presentations (anaphylaxis, aortic dissection,
  thyroid storm, etc.) have no matching seeded condition. Candidate: seed conditions from
  EMR `validation_criteria.assessment[0]` diagnoses.
- **Ophthalmology, Urology, MSK**: conditions exist (OSCE-derived) but little/no MCQ content.
