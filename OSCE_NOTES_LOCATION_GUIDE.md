# OSCE Notes Location Guide
## Dr. Amir Methodology-Based OSCE Preparation Materials

**Created:** 2026-05-27
**Last Updated:** 2026-05-27

---

## 📍 Quick Answer

Your OSCE notes based on Dr. Amir Soufi's methodology are located at:

```
/home/dev/Development/irStudy/ICRP_OSCE_Preparation/
```

---

## 📚 What's Included

### 1. Study Notes (106 files total)

**Format:** Both Markdown (.md) and HTML (.html) for easy viewing

#### Medicine (27+ files)
Located in: `ICRP_OSCE_Preparation/Medicine/`

- **Cardiovascular:** History taking, physical examination, ECG interpretation
- **Respiratory:** History, examination techniques, breath sounds
- **GI System:** Abdominal pain differentials, bleeding, examination
- **Neurology:** Headache, weakness, limb examination, cranial nerves
- **Endocrinology:** Diabetes management, thyroid examination
- **Emergency:** Anaphylaxis, seizure management protocols
- **Dermatology:** History and examination techniques

#### Psychiatry
Located in: `ICRP_OSCE_Preparation/Psychiatry/`

- Mental state examination
- Suicide risk assessment
- Psychiatric history taking
- AMC-specific psychiatry stations

#### Surgery
Located in: `ICRP_OSCE_Preparation/Surgery/`

- Surgical examination techniques
- Pre-operative assessment
- Common surgical presentations

#### Paediatrics
Located in: `ICRP_OSCE_Preparation/Paediatrics/`

- Paediatric examination adaptations
- Common paediatric presentations
- Growth and development assessment

#### Obstetrics & Gynaecology
Located in: `ICRP_OSCE_Preparation/ObGyn/`

- Obstetric history and examination
- Gynaecological assessment
- Pregnancy-related stations

#### Ethics & Communication
Located in: `ICRP_OSCE_Preparation/Ethics_Communication/`

- Breaking bad news
- Informed consent
- Ethical dilemmas
- Cross-cultural communication

---

## 🎯 Dr. Amir Methodology Framework

### Original Name
**"Dr. Amir Methodology"** (after Dr. Amir Soufi's teaching approach)

### Renamed To
**"9-Principle OSCE Framework"** or **"Structured OSCE Methodology"**

### Core Framework: The 5 Ps

Every physical examination follows this universal structure:

1. **P**reparation
   - Wash hands (alcohol gel or soap)
   - Introduce yourself professionally
   - Explain the examination
   - Gain consent

2. **P**osition
   - Position patient appropriately for the examination
   - Ensure patient comfort
   - Optimize lighting and privacy

3. **P**ermission
   - Ask permission before each step
   - Ensure patient comfort throughout
   - Offer chaperone when appropriate

4. **P**erform
   - Systematic examination using frameworks
   - Appropriate exposure and draping
   - Communicate findings as you go

5. **P**resent
   - Summarize findings to examiner
   - Propose differential diagnoses
   - Suggest management plan

### Additional Frameworks Used

**HIPJAP** (Cardiovascular Examination):
- **H**ands
- **I**nspection (general, precordium)
- **P**ulse
- **J**VP (Jugular Venous Pressure)
- **A**pex beat
- **P**alpation, Percussion, Auscultation

**IPTAP** (Respiratory Examination):
- **I**nspection (general, chest)
- **P**alpation (trachea, expansion, tactile fremitus)
- **T**actile fremitus / Trachea
- **A**uscultation (breath sounds, vocal resonance)
- **P**ercussion

---

## 🎓 Key Features of the Notes

### 1. AMC Clinical Exam Focus
- **High-yield content** marked with ⭐⭐⭐
- **Frequency indicators** (appears in 80%+ of exams)
- **Study priority levels** (CRITICAL, HIGH, MEDIUM)
- **Australian medical context** throughout

### 2. Structured Approach
- **Time allocation:** 8-10 minutes per station
- **Systematic frameworks** for all examinations
- **Examiner communication** scripts
- **Presentation templates**

### 3. Clinical Integration
- **Australian guidelines** (eTG, Therapeutic Guidelines)
- **PBS medication codes** included
- **Real clinical scenarios**
- **Evidence-based management**

### 4. Multimedia Resources
- **Video demonstrations** (Stanford Medicine 25, Geeky Medics)
- **Audio examples** (heart sounds, breath sounds)
- **Visual aids** for examination techniques

---

## 📖 Master Index Files

### 1. START_HERE.md
**Location:** `ICRP_OSCE_Preparation/START_HERE.md`

Quick start guide with:
- Overview of all materials
- Study schedule recommendations
- Exam day checklist
- Resource prioritization

### 2. Master OSCE Index
**Location:** `ICRP_OSCE_Preparation/00_MASTER_INDEX_AMC_CLINICAL_OSCE.md`

Complete catalog of all OSCE stations:
- Organized by specialty
- Difficulty ratings
- Time requirements
- Cross-references

### 3. Video Resources
**Location:** `ICRP_OSCE_Preparation/00_VIDEO_RESOURCES_MASTER_LIST.md`

50+ curated video demonstrations:
- Stanford Medicine 25
- Geeky Medics OSCE Guides
- Oxford Medical Education
- Australian-specific resources

---

## 💾 Database OSCEs (For Application)

### Location
```
/home/dev/Development/irStudy/data/osces/
```

### Files Available
- `cardiology_50_osces.json` - 50 cardiology OSCE scenarios
- `respiratory_50_osces.json` - 50 respiratory scenarios
- `psychiatry_40_osces.json` - 40 psychiatry scenarios
- `missing_topics_comprehensive_osces.json` - Additional coverage

### Database Status
✅ **Already imported:** 225 OSCEs in database

**Distribution:**
- Cardiology: 64 OSCEs
- Respiratory: 52 OSCEs
- Psychiatry: 46 OSCEs
- General Practice: 33 OSCEs
- Gastroenterology: 17 OSCEs
- Neurology: 8 OSCEs
- Obstetrics/Gynaecology: 2 OSCEs
- Surgery: 2 OSCEs
- Paediatrics: 1 OSCE

### OSCE Structure
Each OSCE includes:
```json
{
  "osce_id": "CARD-001",
  "patient_scenario": {
    "demographics": {...},
    "chief_complaint": "...",
    "history_presenting_illness": "..."
  },
  "management_plan": {
    "immediate": [...],
    "investigations": [...],
    "treatment": [...]
  },
  "marking_criteria": {...},
  "learning_objectives": [...],
  "references": [...]
}
```

---

## 🔍 How to Use These Notes

### For Study
1. **Start with START_HERE.md** for orientation
2. **Review the Master Index** to identify high-yield topics
3. **Study by specialty** using the folder structure
4. **Watch video demonstrations** before attempting practice
5. **Practice with mock stations** regularly

### For Practice
1. **Read the scenario** from study notes
2. **Watch video demonstration** if available
3. **Practice examination** following 5 Ps framework
4. **Time yourself** (8-10 minutes)
5. **Review marking criteria** and self-assess

### For Application Access
The OSCE scenarios are accessible through:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8001/api/v1/osces
- **Database:** PostgreSQL (irstudy_medical.osces table)

---

## 📊 Content Coverage

### Examination Types
- ✅ Cardiovascular examination
- ✅ Respiratory examination
- ✅ Abdominal examination
- ✅ Neurological examination (cranial nerves, upper/lower limb)
- ✅ Musculoskeletal examination
- ✅ ENT examination
- ✅ Thyroid examination
- ✅ Lymph node examination
- ✅ Peripheral vascular examination
- ✅ Dermatology examination

### History Taking
- ✅ Presenting complaint frameworks
- ✅ System-specific histories
- ✅ Pain assessment (SOCRATES)
- ✅ Red flag identification
- ✅ Social and functional history

### Clinical Skills
- ✅ ECG interpretation
- ✅ Vital signs interpretation
- ✅ Emergency management protocols
- ✅ Prescription writing
- ✅ Patient education

### Communication Skills
- ✅ Breaking bad news
- ✅ Informed consent
- ✅ Cultural sensitivity
- ✅ Interpreter use
- ✅ Difficult conversations

---

## 🎯 Exam Preparation Tips (Dr. Amir Method)

### 1. Systematic Practice
- Practice each examination 10-15 times
- Use the exact same sequence every time
- Time yourself consistently
- Practice presentation out loud

### 2. Framework Mastery
- Memorize 5 Ps framework
- Learn specialty-specific frameworks (HIPJAP, IPTAP)
- Practice introducing each framework to patient
- Never skip steps

### 3. High-Yield Focus
- Prioritize ⭐⭐⭐ content (80% of exam coverage)
- Master common presentations first
- Review Australian guidelines thoroughly
- Know PBS medication codes for common drugs

### 4. Mock Exams
- Complete full mock OSCEs weekly
- Practice with peers or mentors
- Get feedback on communication style
- Review performance and adjust

---

## 📱 Accessing in Your Application

### Web Interface
1. Open browser to: http://localhost:5173
2. Navigate to "OSCE Practice" section
3. Select specialty or difficulty
4. Practice with timed scenarios
5. Review marking criteria and feedback

### API Access
```bash
# Get all OSCEs
curl http://localhost:8001/api/v1/osces

# Get by specialty
curl http://localhost:8001/api/v1/osces?specialty=cardiology

# Get specific OSCE
curl http://localhost:8001/api/v1/osces/CARD-001
```

---

## 📝 Sample Note Structure

Every note follows this format:

```markdown
# [Topic Name] OSCE Notes
## AMC Clinical / ICRP NSW Preparation

---

## 🎯 AMC EXAM FREQUENCY INDICATOR
[⭐⭐⭐ HIGH-YIELD] - frequency and importance

---

## 📺 RECOMMENDED VIDEO DEMONSTRATIONS
[Links to relevant videos]

---

## THE 5 Ps FRAMEWORK
[Universal examination structure]

---

## [EXAMINATION NAME]

### 1. PREPARATION (60 seconds)
[Specific steps for this examination]

### 2. POSITION
[Patient positioning instructions]

### 3. PERMISSION
[Consent and comfort scripts]

### 4. PERFORM - SYSTEMATIC EXAMINATION
[Detailed step-by-step examination]

### 5. PRESENT
[Presentation template and common findings]

---

## COMMON FINDINGS AND INTERPRETATION
[Clinical findings with significance]

---

## DIFFERENTIAL DIAGNOSES
[Common differentials by presentation]

---

## MANAGEMENT PRINCIPLES
[Australian guidelines-based management]
```

---

## 🔄 Updates and Maintenance

### Last Content Update
- **Date:** May 21, 2026
- **Content:** OSCE scenarios regenerated with PBS codes
- **Coverage:** 225 OSCEs across 9 specialties

### Methodology Document
Original methodology guide renamed:
- **Old name:** `DR_AAMIR_METHODOLOGY_GUIDE.html`
- **New name:** `OSCE_METHODOLOGY_GUIDE.html`
- **Location:** `ICRP_OSCE_Preparation/` (if exists)

---

## 💡 Quick Tips

### For Quick Reference
- Keep `00_MASTER_INDEX_AMC_CLINICAL_OSCE.md` open during study
- Use HTML versions for better formatting in browser
- Print high-yield checklists for revision

### For Practice
- Use `Mock_Stations/` folder for timed practice
- Record yourself practicing examinations
- Practice with different "patients" to adapt communication

### For Exam Day
- Review 5 Ps framework morning of exam
- Practice hand hygiene technique
- Rehearse introduction script
- Remember: systematic approach > finding everything

---

## 📞 Additional Resources

### External Links (in notes)
- Stanford Medicine 25: https://stanfordmedicine25.stanford.edu
- Geeky Medics: https://geekymedics.com
- Oxford Medical Education: https://oxfordmedicaleducation.com
- Therapeutic Guidelines (eTG): https://tg.org.au

### Australian Medical Resources
- AMC Clinical Examination: https://www.amc.org.au
- RACGP Red Book: https://www.racgp.org.au
- PBS Information: https://www.pbs.gov.au

---

**Summary:** Your comprehensive OSCE preparation materials based on Dr. Amir Soufi's methodology are in `/home/dev/Development/irStudy/ICRP_OSCE_Preparation/` with 106 files covering all major specialties, examination techniques, and clinical scenarios. The structured 5 Ps framework and specialty-specific protocols (HIPJAP, IPTAP) provide systematic approaches for AMC Clinical exam success.

**Database:** 225 OSCE scenarios are already imported and accessible through your application at http://localhost:5173

---

*For questions or updates to these materials, refer to the conversation logs in `archive/conversations/` or the project README.*
