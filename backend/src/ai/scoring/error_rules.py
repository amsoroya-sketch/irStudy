"""
Critical Error Rules for AI OSCE Scoring

Defines 20+ critical error rules that trigger auto-fail regardless of score.
Each rule represents a safety-critical violation in Australian medical practice.

SECURITY: No hardcoded credentials
CONTEXT: AMC Clinical Examination standards (Australian)
"""

from typing import Dict, List, Any, Callable
import re


class ErrorRule:
    """Represents a single critical error rule."""

    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        category: str,
        severity: str = "auto_fail",
        keywords: List[str] = None,
        patterns: List[str] = None,
        check_function: Callable = None
    ):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.category = category
        self.severity = severity
        self.keywords = keywords or []
        self.patterns = patterns or []
        self.check_function = check_function

    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary format."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "severity": self.severity
        }


# Critical Error Rules (20+ rules covering major safety domains)

CRITICAL_ERROR_RULES = [
    # ===== ACUTE CARE / RED FLAGS (CE001-CE005) =====

    ErrorRule(
        rule_id="CE001",
        name="Missed acute red flag - chest pain",
        description="Failed to order ECG for chest pain presentation (STEMI/ACS red flag)",
        category="acute_care",
        keywords=["chest pain", "cardiac", "heart"],
        patterns=[
            r"chest\s+pain",
            r"crushing\s+pain",
            r"cardiac\s+pain",
            r"heart\s+pain"
        ]
    ),

    ErrorRule(
        rule_id="CE002",
        name="Missed acute red flag - stroke symptoms",
        description="Failed to recognize or act on stroke symptoms (FAST protocol)",
        category="acute_care",
        keywords=["weakness", "slurred speech", "facial droop", "stroke"],
        patterns=[
            r"facial\s+droop",
            r"arm\s+weakness",
            r"slurred\s+speech",
            r"sudden\s+weakness"
        ]
    ),

    ErrorRule(
        rule_id="CE003",
        name="Missed acute red flag - anaphylaxis",
        description="Failed to recognize or treat anaphylaxis (life-threatening allergy)",
        category="acute_care",
        keywords=["rash", "swelling", "difficulty breathing", "throat closing"],
        patterns=[
            r"difficulty\s+breathing",
            r"throat\s+(closing|swelling)",
            r"widespread\s+rash",
            r"anaphylaxis"
        ]
    ),

    ErrorRule(
        rule_id="CE004",
        name="Missed acute red flag - severe sepsis",
        description="Failed to recognize sepsis (fever, hypotension, confusion)",
        category="acute_care",
        keywords=["fever", "confusion", "low blood pressure", "sepsis"],
        patterns=[
            r"fever.*confusion",
            r"hypotension.*fever",
            r"sepsis",
            r"septic\s+shock"
        ]
    ),

    ErrorRule(
        rule_id="CE005",
        name="Missed acute red flag - ectopic pregnancy",
        description="Failed to consider ectopic pregnancy in woman with abdominal pain",
        category="acute_care",
        keywords=["abdominal pain", "pregnant", "missed period", "vaginal bleeding"],
        patterns=[
            r"abdominal\s+pain.*pregnant",
            r"missed\s+period.*pain",
            r"ectopic\s+pregnancy"
        ]
    ),

    # ===== MEDICATION SAFETY (CE006-CE010) =====

    ErrorRule(
        rule_id="CE006",
        name="Unsafe medication - contraindicated",
        description="Prescribed contraindicated medication (e.g., beta-blocker in asthma)",
        category="medication_safety",
        keywords=["contraindicated", "allergy", "interaction", "unsafe"],
        patterns=[
            r"contraindicated",
            r"drug\s+interaction",
            r"allergic\s+to.*prescribed",
            r"beta.*blocker.*asthma"
        ]
    ),

    ErrorRule(
        rule_id="CE007",
        name="Unsafe medication - wrong dose",
        description="Prescribed dangerous dose (10x error, pediatric miscalculation)",
        category="medication_safety",
        keywords=["overdose", "wrong dose", "too much", "toxic"],
        patterns=[
            r"overdose",
            r"toxic\s+dose",
            r"10.*times",
            r"wrong\s+dose"
        ]
    ),

    ErrorRule(
        rule_id="CE008",
        name="Medication allergy not checked",
        description="Failed to ask about medication allergies before prescribing",
        category="medication_safety",
        keywords=["allergy", "allergic"],
        patterns=[
            r"did\s+not\s+ask.*allerg",
            r"forgot\s+to\s+check.*allerg",
            r"no\s+allergy\s+history"
        ]
    ),

    ErrorRule(
        rule_id="CE009",
        name="High-risk medication - no monitoring",
        description="Prescribed high-risk drug (warfarin, lithium) without monitoring plan",
        category="medication_safety",
        keywords=["warfarin", "lithium", "monitoring", "INR", "therapeutic level"],
        patterns=[
            r"warfarin.*no\s+monitoring",
            r"lithium.*no\s+monitoring",
            r"high.risk.*no\s+follow.up"
        ]
    ),

    ErrorRule(
        rule_id="CE010",
        name="Unsafe medication - pregnancy",
        description="Prescribed teratogenic medication to pregnant woman",
        category="medication_safety",
        keywords=["pregnant", "teratogenic", "contraindicated in pregnancy"],
        patterns=[
            r"pregnant.*teratogenic",
            r"pregnant.*contraindicated",
            r"ACE\s+inhibitor.*pregnant"
        ]
    ),

    # ===== CLINICAL MANAGEMENT (CE011-CE015) =====

    ErrorRule(
        rule_id="CE011",
        name="Failed to escalate emergency",
        description="Failed to call for help in life-threatening situation",
        category="clinical_management",
        keywords=["emergency", "urgent", "life-threatening", "escalate"],
        patterns=[
            r"did\s+not\s+call.*help",
            r"failed\s+to\s+escalate",
            r"no\s+emergency\s+response",
            r"did\s+not\s+activate.*emergency"
        ]
    ),

    ErrorRule(
        rule_id="CE012",
        name="No resuscitation in cardiac arrest",
        description="Failed to initiate CPR or call emergency (000) for cardiac arrest",
        category="clinical_management",
        keywords=["cardiac arrest", "not breathing", "no pulse", "collapsed"],
        patterns=[
            r"cardiac\s+arrest.*no\s+(CPR|resuscitation)",
            r"not\s+breathing.*no\s+action",
            r"collapsed.*did\s+not\s+call.*000"
        ]
    ),

    ErrorRule(
        rule_id="CE013",
        name="Inadequate pain management",
        description="Dismissed severe pain (8-10/10) without appropriate management",
        category="clinical_management",
        keywords=["severe pain", "10/10", "unbearable", "agony"],
        patterns=[
            r"(8|9|10)/10.*no\s+analgesia",
            r"severe\s+pain.*dismissed",
            r"unbearable.*paracetamol\s+only"
        ]
    ),

    ErrorRule(
        rule_id="CE014",
        name="Incorrect vital sign interpretation",
        description="Misinterpreted critically abnormal vitals (BP 80/40, HR 180, Temp 40°C)",
        category="clinical_management",
        keywords=["vital signs", "blood pressure", "heart rate", "temperature"],
        patterns=[
            r"BP\s+80/40.*normal",
            r"HR\s+180.*not\s+urgent",
            r"temp(erature)?\s+40.*reassurance\s+only",
            r"critically\s+abnormal.*ignored"
        ]
    ),

    ErrorRule(
        rule_id="CE015",
        name="Dismissive of serious symptoms",
        description="Told patient to 'go home and rest' for serious red flag symptoms",
        category="clinical_management",
        keywords=["go home", "not serious", "just rest", "overreacting"],
        patterns=[
            r"chest\s+pain.*(go\s+home|just\s+rest)",
            r"red\s+flag.*dismissed",
            r"serious\s+symptom.*overreacting",
            r"take\s+paracetamol.*chest\s+pain"
        ]
    ),

    # ===== PROFESSIONALISM / ETHICS (CE016-CE020) =====

    ErrorRule(
        rule_id="CE016",
        name="Cultural insensitivity",
        description="Offensive or culturally inappropriate comments",
        category="professionalism",
        keywords=["offensive", "inappropriate", "cultural", "discriminatory"],
        patterns=[
            r"culturally\s+insensitive",
            r"offensive\s+comment",
            r"discriminatory",
            r"racist|sexist"
        ]
    ),

    ErrorRule(
        rule_id="CE017",
        name="Failed to obtain informed consent",
        description="Performed intimate examination or procedure without consent",
        category="professionalism",
        keywords=["no consent", "without permission", "forced", "coerced"],
        patterns=[
            r"no\s+consent",
            r"without\s+(permission|asking)",
            r"intimate\s+exam.*not\s+explained",
            r"forced\s+examination"
        ]
    ),

    ErrorRule(
        rule_id="CE018",
        name="Inappropriate intimate examination",
        description="Conducted intimate exam without chaperone or proper explanation",
        category="professionalism",
        keywords=["intimate exam", "chaperone", "inappropriate"],
        patterns=[
            r"intimate\s+exam.*no\s+chaperone",
            r"rectal.*no\s+explanation",
            r"breast.*no\s+consent",
            r"genital.*inappropriate"
        ]
    ),

    ErrorRule(
        rule_id="CE019",
        name="Severe communication breakdown",
        description="Completely failed to communicate (yelled, walked out, ignored patient)",
        category="professionalism",
        keywords=["yelled", "shouted", "walked out", "ignored", "rude"],
        patterns=[
            r"yelled\s+at\s+patient",
            r"walked\s+out",
            r"ignored\s+patient",
            r"extremely\s+rude",
            r"threw.*chart"
        ]
    ),

    ErrorRule(
        rule_id="CE020",
        name="Infection control violations",
        description="Severe infection control breach (no handwashing, contaminated technique)",
        category="professionalism",
        keywords=["infection control", "hand hygiene", "sterile", "contaminated"],
        patterns=[
            r"no\s+hand\s*(washing|hygiene)",
            r"contaminated.*sterile",
            r"broke.*aseptic",
            r"infection\s+control.*violated"
        ]
    ),

    # ===== ADDITIONAL DOMAIN-SPECIFIC RULES (CE021-CE025) =====

    ErrorRule(
        rule_id="CE021",
        name="Missed child safeguarding issue",
        description="Failed to recognize or report child abuse/neglect",
        category="safeguarding",
        keywords=["child abuse", "neglect", "safeguarding", "bruising pattern"],
        patterns=[
            r"child.*bruising.*ignored",
            r"abuse\s+signs.*dismissed",
            r"safeguarding.*not\s+reported"
        ]
    ),

    ErrorRule(
        rule_id="CE022",
        name="Suicidal ideation not assessed",
        description="Patient mentions depression/hopelessness but suicide risk not assessed",
        category="mental_health",
        keywords=["suicidal", "depression", "hopeless", "self-harm"],
        patterns=[
            r"suicidal.*not\s+asked",
            r"depressed.*no\s+risk\s+assessment",
            r"hopeless.*ignored",
            r"self.harm.*dismissed"
        ]
    ),

    ErrorRule(
        rule_id="CE023",
        name="Domestic violence not explored",
        description="Suspicious injuries but domestic violence not sensitively explored",
        category="safeguarding",
        keywords=["domestic violence", "suspicious injuries", "partner", "bruises"],
        patterns=[
            r"suspicious\s+injuries.*not\s+explored",
            r"domestic\s+violence.*not\s+asked",
            r"partner.*injuries.*ignored"
        ]
    ),

    ErrorRule(
        rule_id="CE024",
        name="No safety-netting advice",
        description="Discharged high-risk patient without clear return instructions",
        category="clinical_management",
        keywords=["safety net", "return if", "red flags", "follow-up"],
        patterns=[
            r"high.risk.*no\s+safety.net",
            r"discharged.*no\s+(return|follow.up)\s+advice",
            r"red\s+flags.*not\s+explained"
        ]
    ),

    ErrorRule(
        rule_id="CE025",
        name="Breached confidentiality",
        description="Discussed patient information inappropriately or without consent",
        category="professionalism",
        keywords=["confidentiality", "privacy", "disclosed", "shared information"],
        patterns=[
            r"breached\s+confidentiality",
            r"disclosed.*without\s+consent",
            r"privacy\s+violation",
            r"shared\s+information.*inappropriately"
        ]
    ),
]


def get_all_rules() -> List[ErrorRule]:
    """Return all critical error rules."""
    return CRITICAL_ERROR_RULES


def get_rules_by_category(category: str) -> List[ErrorRule]:
    """Return rules for a specific category."""
    return [rule for rule in CRITICAL_ERROR_RULES if rule.category == category]


def get_rule_by_id(rule_id: str) -> ErrorRule:
    """Get a specific rule by ID."""
    for rule in CRITICAL_ERROR_RULES:
        if rule.rule_id == rule_id:
            return rule
    return None
