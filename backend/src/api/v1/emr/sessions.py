"""
EMR Session Management Endpoints

ENDPOINTS:
- POST /sessions/start - Start new EMR practice session with patient selection
- GET /sessions/{session_id} - Retrieve session details with validation results
- PUT /sessions/{session_id} - Update session (auto-save SOAP note)
- POST /sessions/{session_id}/submit - Submit SOAP note for 3-layer validation
- DELETE /sessions/{session_id} - Cancel/delete session
- GET /sessions - List user's sessions (paginated with filters)

SECURITY:
- JWT authentication required
- User can only access their own sessions
- Educators can view all sessions

AUSTRALIAN MEDICAL CONTEXT:
- Uses Australian terminology (paracetamol, salbutamol, adrenaline)
- Emergency number: 000 (NOT 911)
- Follows eTG, PBS, MBS, AHPRA standards
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from uuid import UUID
from datetime import datetime
from typing import List, Optional
import json

from src.db.base import get_db
from src.db.models import (
    User,
    UserRole,
    MockPatient,
    EMRSession,
    EMRSOAPNote,
    EMRPrescription,
    EMRPathologyOrder,
    EMRValidationResult,
)
from src.services.emr.assessment_engine import assess_submission_sync, decide_pass_fail
from src.auth.dependencies import get_current_user
from .schemas import (
    StartSessionRequest,
    UpdateSessionRequest,
    SessionResponse,
    SubmitSessionRequest,
    MockPatientResponse,
    ValidationResult,
    ValidationLayerResult,
)


router = APIRouter()


# ============================================================================
# SPECIALTY WHITELIST
# ============================================================================
# The old hardcoded list rejected 14/24 authored cases (e.g. emergency_medicine,
# obstetrics_gynaecology, general_practice, ophthalmology, psychiatry, surgery,
# urology). This constant is the union of the legacy specialties and every
# specialty actually authored in the practice-case library. At request time we
# additionally accept any specialty currently present in mock_patients, so the
# whitelist can never again drift behind the seeded content — while an unknown
# value (e.g. "not_a_specialty") is still rejected with a 400.
KNOWN_SPECIALTIES = frozenset(
    {
        # Legacy whitelist
        "cardiology",
        "respiratory",
        "gastroenterology",
        "neurology",
        "endocrinology",
        "rheumatology",
        "nephrology",
        "haematology",
        "oncology",
        "infectious_diseases",
        "general",
        # Authored EMR practice-case specialties (Phase 1a reconciliation)
        "emergency_medicine",
        "obstetrics_gynaecology",
        "general_practice",
        "ophthalmology",
        "psychiatry",
        "surgery",
        "urology",
    }
)


# ============================================================================
# ENDPOINT 1: POST /sessions/start - START NEW SESSION
# ============================================================================


@router.post("/sessions/start", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    request: StartSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Start new EMR practice session with automatic patient selection.

    FLOW:
    1. If patient_id provided, use that specific patient
    2. If specialty/difficulty provided, filter patients and select random
    3. If neither provided, select random patient from entire pool
    4. Create session record with status="in_progress"
    5. Return session + patient information

    AUTHORIZATION:
    - User can create unlimited practice sessions
    - Session is linked to current_user.id

    AUSTRALIAN COMPLIANCE:
    - Patient data uses Australian medical context
    - No hardcoded patient IDs (dependency injection)
    """
    # Validate specialty value.
    # Accept the static whitelist plus any specialty actually present in the
    # database, so every authored case is reachable while unknown values 400.
    if request.specialty and request.specialty not in KNOWN_SPECIALTIES:
        db_specialties = {
            row[0]
            for row in db.query(MockPatient.specialty).distinct().all()
            if row[0]
        }
        if request.specialty not in db_specialties:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid specialty - validation error",
            )

    # Validate difficulty value
    if request.difficulty and request.difficulty not in ["easy", "medium", "hard"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid difficulty - validation error",
        )

    # Patient selection logic
    if request.patient_id:
        # Specific patient requested
        mock_patient = db.query(MockPatient).filter(MockPatient.id == request.patient_id).first()
        if not mock_patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {request.patient_id} not found",
            )
    else:
        # Filter by specialty and/or difficulty
        query = db.query(MockPatient)

        if request.specialty:
            query = query.filter(MockPatient.specialty == request.specialty)

        if request.difficulty:
            query = query.filter(MockPatient.difficulty == request.difficulty)

        # Get first matching patient (in production, would randomize)
        mock_patient = query.first()

        if not mock_patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No patients available matching criteria",
            )

    # Create session
    emr_session = EMRSession(
        user_id=current_user.id,
        patient_id=mock_patient.id,
        specialty=mock_patient.specialty,
        difficulty=mock_patient.difficulty,
        status="in_progress",
        auto_save_count=0,
        elapsed_time_seconds=0,
    )

    db.add(emr_session)
    db.commit()
    db.refresh(emr_session)

    # Build response
    return SessionResponse(
        session_id=emr_session.id,
        validation_id=emr_session.id,
        patient=MockPatientResponse(
            id=mock_patient.id,
            name=mock_patient.name,
            age=mock_patient.age,
            gender=mock_patient.gender,
            presenting_complaint=mock_patient.presenting_complaint,
            specialty=mock_patient.specialty,
            vital_signs=mock_patient.vital_signs,
            medical_history=mock_patient.medical_history,
        ),
        specialty=emr_session.specialty,
        difficulty=emr_session.difficulty,
        started_at=emr_session.started_at,
        submitted_at=None,
        elapsed_time_seconds=0,
        status="in_progress",
        auto_save_count=0,
        last_auto_save_at=None,
        validation_score=None,
        validation_results=None,
        soap_note=None,
        typing_metrics=None,
    )


# ============================================================================
# ENDPOINT 2: GET /sessions/{session_id} - GET SESSION DETAILS
# ============================================================================


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve EMR session details with validation results.

    AUTHORIZATION:
    - Students can only access their own sessions
    - Educators can view any session

    RESPONSE:
    - Returns session metadata, patient info, SOAP note, validation results
    - If session is graded, includes validation_results with 3-layer validation
    """
    # Fetch session
    emr_session = db.query(EMRSession).filter(EMRSession.id == session_id).first()

    if not emr_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Authorization check
    if current_user.role != UserRole.EDUCATOR and emr_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session",
        )

    # Fetch patient
    mock_patient = db.query(MockPatient).filter(MockPatient.id == emr_session.patient_id).first()

    # Fetch SOAP note if exists
    soap_note = db.query(EMRSOAPNote).filter(
        EMRSOAPNote.session_id == session_id
    ).order_by(desc(EMRSOAPNote.id)).first()

    soap_note_dict = None
    if soap_note:
        soap_note_dict = {
            "subjective": soap_note.subjective,
            "objective": soap_note.objective,
            "assessment": soap_note.assessment,
            "plan": soap_note.plan,
        }

    # Build validation results when graded, OR when a prior submit hit an AI outage
    # (score_breakdown carries ai_unavailable=True, session left un-graded). The
    # authoritative pass_fail is surfaced as-is (None on outage) — never recomputed.
    validation_results = None
    _bd = emr_session.score_breakdown or {}
    _ai_unavailable = bool(_bd.get("ai_unavailable"))
    if _bd and (emr_session.status == "graded" or _ai_unavailable):
        validation_results = ValidationResult(
            overall_score=emr_session.score_breakdown.get("overall_score", 0),
            pass_fail=emr_session.score_breakdown.get("pass_fail"),
            category_scores=emr_session.score_breakdown.get("category_scores", {}),
            completeness=emr_session.score_breakdown.get("completeness") or None,
            captured=emr_session.score_breakdown.get("captured", []),
            missing_elements=emr_session.score_breakdown.get("missing_elements", []),
            strengths=emr_session.score_breakdown.get("strengths", []),
            improvements=emr_session.score_breakdown.get("improvements", []),
            red_flags=emr_session.score_breakdown.get("red_flags", []),
            australian_compliance=emr_session.score_breakdown.get("australian_compliance", {}),
            ai_unavailable=True if _ai_unavailable else None,
            layer_1_zod=ValidationLayerResult(
                passed=emr_session.score_breakdown.get("layer_1_zod", {}).get("passed", False),
                score=emr_session.score_breakdown.get("layer_1_zod", {}).get("score"),
                feedback=emr_session.score_breakdown.get("layer_1_zod", {}).get("feedback"),
                errors=emr_session.score_breakdown.get("layer_1_zod", {}).get("errors", []),
            ),
            layer_2_python=ValidationLayerResult(
                passed=emr_session.score_breakdown.get("layer_2_python", {}).get("passed", False),
                score=emr_session.score_breakdown.get("layer_2_python", {}).get("score"),
                feedback=emr_session.score_breakdown.get("layer_2_python", {}).get("feedback"),
                errors=emr_session.score_breakdown.get("layer_2_python", {}).get("errors", []),
            ),
            layer_3_ai=(
                ValidationLayerResult(
                    passed=emr_session.score_breakdown.get("layer_3_ai", {}).get("passed", False),
                    score=emr_session.score_breakdown.get("layer_3_ai", {}).get("score"),
                    feedback=emr_session.score_breakdown.get("layer_3_ai", {}).get("feedback"),
                    errors=emr_session.score_breakdown.get("layer_3_ai", {}).get("errors", []),
                )
                if emr_session.score_breakdown.get("layer_3_ai")
                else None
            ),
            performance_summary=emr_session.score_breakdown.get("performance_summary"),
            next_steps=emr_session.score_breakdown.get("next_steps"),
        )

    return SessionResponse(
        session_id=emr_session.id,
        validation_id=emr_session.id,
        patient=MockPatientResponse(
            id=mock_patient.id,
            name=mock_patient.name,
            age=mock_patient.age,
            gender=mock_patient.gender,
            presenting_complaint=mock_patient.presenting_complaint,
            specialty=mock_patient.specialty,
            vital_signs=mock_patient.vital_signs,
            medical_history=mock_patient.medical_history,
        ),
        specialty=emr_session.specialty,
        difficulty=emr_session.difficulty,
        started_at=emr_session.started_at,
        submitted_at=emr_session.submitted_at,
        elapsed_time_seconds=emr_session.elapsed_time_seconds,
        status=emr_session.status,
        auto_save_count=emr_session.auto_save_count,
        last_auto_save_at=emr_session.last_auto_save_at,
        validation_score=emr_session.validation_score,
        total_amc_score=emr_session.validation_score,
        validation_results=validation_results,
        soap_note=soap_note_dict,
        typing_metrics=emr_session.typing_metrics,
    )


# ============================================================================
# ENDPOINT 3: PUT /sessions/{session_id} - UPDATE SESSION (AUTO-SAVE)
# ============================================================================


@router.put("/sessions/{session_id}/auto-save", response_model=SessionResponse)
async def auto_save_session(
    session_id: UUID,
    request: UpdateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Auto-save endpoint alias for update_session.
    """
    return await update_session(session_id, request, current_user, db)


@router.put("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: UUID,
    request: UpdateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update session with auto-save functionality.

    FLOW:
    1. Validate session exists and belongs to user
    2. Check session is in_progress (cannot update submitted sessions)
    3. Save SOAP note (upsert - create or update)
    4. Increment auto_save_count
    5. Update last_auto_save_at timestamp
    6. Return updated session

    PERFORMANCE TARGET: <2s (p95)
    """
    # Fetch session
    emr_session = db.query(EMRSession).filter(
        EMRSession.id == session_id
    ).first()

    if not emr_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Authorization check
    if current_user.role != UserRole.EDUCATOR and emr_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session",
        )

    # Check session status
    if emr_session.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update submitted session",
        )

    # Save SOAP note if provided
    if request.soap_note:
        # Check if SOAP note already exists
        soap_note = db.query(EMRSOAPNote).filter(
            EMRSOAPNote.session_id == session_id,
            EMRSOAPNote.is_final_submission == False
        ).first()

        if soap_note:
            # Update existing
            soap_note.subjective = request.soap_note.get("subjective", soap_note.subjective)
            soap_note.objective = request.soap_note.get("objective", soap_note.objective)
            soap_note.assessment = request.soap_note.get("assessment", soap_note.assessment)
            soap_note.plan = request.soap_note.get("plan", soap_note.plan)
        else:
            # Create new
            soap_note = EMRSOAPNote(
                session_id=session_id,
                subjective=request.soap_note.get("subjective", ""),
                objective=request.soap_note.get("objective", ""),
                assessment=request.soap_note.get("assessment", ""),
                plan=request.soap_note.get("plan", ""),
                is_final_submission=False,
            )
            db.add(soap_note)

    # Update session metadata
    emr_session.auto_save_count += 1
    emr_session.last_auto_save_at = datetime.utcnow()
    emr_session.elapsed_time_seconds = request.elapsed_time_seconds

    db.commit()
    db.refresh(emr_session)

    # Fetch patient for response
    mock_patient = db.query(MockPatient).filter(MockPatient.id == emr_session.patient_id).first()

    return SessionResponse(
        session_id=emr_session.id,
        validation_id=emr_session.id,
        patient=MockPatientResponse(
            id=mock_patient.id,
            name=mock_patient.name,
            age=mock_patient.age,
            gender=mock_patient.gender,
            presenting_complaint=mock_patient.presenting_complaint,
            specialty=mock_patient.specialty,
            vital_signs=mock_patient.vital_signs,
            medical_history=mock_patient.medical_history,
        ),
        specialty=emr_session.specialty,
        difficulty=emr_session.difficulty,
        started_at=emr_session.started_at,
        submitted_at=emr_session.submitted_at,
        elapsed_time_seconds=emr_session.elapsed_time_seconds,
        status=emr_session.status,
        auto_save_count=emr_session.auto_save_count,
        last_auto_save_at=emr_session.last_auto_save_at,
        validation_score=emr_session.validation_score,
        total_amc_score=emr_session.validation_score,
        validation_results=None,
        soap_note=request.soap_note,
        typing_metrics=None,
        message="Session auto-saved successfully",
    )


# ============================================================================
# ENDPOINT 4: POST /sessions/{session_id}/submit - SUBMIT FOR VALIDATION
# ============================================================================


from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/sessions/{session_id}/submit", response_model=SessionResponse)
@limiter.limit("5/minute")
async def submit_session(
    request: Request,
    session_id: UUID,
    data: SubmitSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submit SOAP note for 3-layer validation.

    VALIDATION LAYERS:
    1. Layer 1 (Zod/Pydantic): Field presence, length, data types
    2. Layer 2 (Python): Australian terminology, PBS prescription rules
    3. Layer 3 (Claude AI): Clinical reasoning, safety, guidelines compliance

    FLOW:
    1. Validate session exists and belongs to user
    2. Check session not already submitted
    3. Save final SOAP note, prescriptions, pathology orders
    4. Run 3-layer validation
    5. Calculate overall score (0-15 AMC rubric)
    6. Update session status to "graded"
    7. Return validation results

    PERFORMANCE TARGET: <6s (includes Claude AI call)
    """
    # Fetch session
    emr_session = db.query(EMRSession).filter(
        EMRSession.id == session_id,
        EMRSession.user_id == current_user.id
    ).first()

    if not emr_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Check session status - if already graded, return existing results
    if emr_session.status == "graded":
        mock_patient = db.query(MockPatient).filter(MockPatient.id == emr_session.patient_id).first()
        soap_note = db.query(EMRSOAPNote).filter(
            EMRSOAPNote.session_id == session_id,
            EMRSOAPNote.is_final_submission == True
        ).order_by(desc(EMRSOAPNote.id)).first()

        soap_note_dict = None
        if soap_note:
            soap_note_dict = {
                "subjective": soap_note.subjective,
                "objective": soap_note.objective,
                "assessment": soap_note.assessment,
                "plan": soap_note.plan,
            }

        return SessionResponse(
            session_id=emr_session.id,
            validation_id=emr_session.id,
            patient=MockPatientResponse(
                id=mock_patient.id if mock_patient else None,
                name=mock_patient.name if mock_patient else "Unknown",
                age=mock_patient.age if mock_patient else 0,
                gender=mock_patient.gender if mock_patient else "unknown",
                presenting_complaint=mock_patient.presenting_complaint if mock_patient else "",
                specialty=mock_patient.specialty if mock_patient else "",
                vital_signs=mock_patient.vital_signs if mock_patient else {},
                medical_history=mock_patient.medical_history if mock_patient else [],
            ),
            specialty=emr_session.specialty,
            difficulty=emr_session.difficulty,
            started_at=emr_session.started_at,
            submitted_at=emr_session.submitted_at,
            elapsed_time_seconds=emr_session.elapsed_time_seconds,
            status=emr_session.status,
            auto_save_count=emr_session.auto_save_count,
            last_auto_save_at=emr_session.last_auto_save_at,
            validation_score=emr_session.validation_score,
            total_amc_score=emr_session.validation_score,
            validation_results=None,
            soap_note=soap_note_dict,
            typing_metrics=emr_session.typing_metrics,
        )

    # Check session status
    if emr_session.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already submitted",
        )

    # Remove any prior final-submission artefacts. These only exist if an earlier
    # submit hit an AI outage (Claude unavailable): that path deliberately leaves
    # the session in_progress so the student can re-submit, and we must not let a
    # re-submit accumulate duplicate final SOAP notes / orders.
    db.query(EMRSOAPNote).filter(
        EMRSOAPNote.session_id == session_id,
        EMRSOAPNote.is_final_submission == True,
    ).delete(synchronize_session=False)
    db.query(EMRPrescription).filter(
        EMRPrescription.session_id == session_id
    ).delete(synchronize_session=False)
    db.query(EMRPathologyOrder).filter(
        EMRPathologyOrder.session_id == session_id
    ).delete(synchronize_session=False)

    # Save final SOAP note
    final_soap_note = EMRSOAPNote(
        session_id=session_id,
        subjective=data.final_soap_note.get("subjective", ""),
        objective=data.final_soap_note.get("objective", ""),
        assessment=data.final_soap_note.get("assessment", ""),
        plan=data.final_soap_note.get("plan", ""),
        is_final_submission=True,
    )
    db.add(final_soap_note)

    # Save prescriptions
    for prescription in data.prescriptions:
        prescription_record = EMRPrescription(
            session_id=session_id,
            medication_name=prescription.medication,
            dose=prescription.dose,
            frequency=prescription.frequency,
            route=prescription.route,
            # `repeats` is NOT NULL in the DB (CHECK 0..5). The current
            # PrescriptionSubmit schema does not carry repeats/indication, so we
            # default repeats to 0 (no repeats). Wire these through here if/when
            # PrescriptionSubmit gains the fields.
            repeats=getattr(prescription, "repeats", 0) or 0,
            indication=getattr(prescription, "indication", None),
        )
        db.add(prescription_record)

    # Save pathology orders
    for pathology in data.pathology_orders:
        pathology_record = EMRPathologyOrder(
            session_id=session_id,
            test_name=pathology.test_name,
            urgency=pathology.urgency,
            indication=pathology.clinical_notes,
        )
        db.add(pathology_record)

    # ========================================================================
    # 3-LAYER VALIDATION
    # ========================================================================

    # Layer 1: Zod/Pydantic Validation (field presence, length, types)
    layer_1_errors = []
    layer_1_passed = True

    # Check SOAP note field lengths (Australian medical documentation standards)
    if len(data.final_soap_note.get("subjective", "")) < 50:
        layer_1_errors.append("Subjective section too short (<50 characters)")
        layer_1_passed = False
    if len(data.final_soap_note.get("objective", "")) < 30:
        layer_1_errors.append("Objective section too short (<30 characters)")
        layer_1_passed = False
    if len(data.final_soap_note.get("assessment", "")) < 20:
        layer_1_errors.append("Assessment section too short (<20 characters)")
        layer_1_passed = False
    if len(data.final_soap_note.get("plan", "")) < 30:
        layer_1_errors.append("Plan section too short (<30 characters)")
        layer_1_passed = False

    layer_1_result = {
        "passed": layer_1_passed,
        "score": 5.0 if layer_1_passed else 2.0,
        "feedback": "All required fields present and meet minimum length requirements" if layer_1_passed else "Some fields are incomplete",
        "errors": layer_1_errors,
    }

    # Layer 2: Python Business Logic Validation (Australian terminology, PBS rules)
    layer_2_errors = []
    layer_2_passed = True

    # Check for American terminology (red flags)
    soap_text = json.dumps(data.final_soap_note, ensure_ascii=False).lower()
    american_terms = {
        "acetaminophen": "paracetamol",
        "epinephrine": "adrenaline",
        "albuterol": "salbutamol",
        "911": "000",
    }
    for american, australian in american_terms.items():
        if american in soap_text:
            layer_2_errors.append(f"Use Australian term '{australian}' instead of '{american}'")
            layer_2_passed = False

    # Check PBS prescription rules (max 5 repeats)
    for prescription in data.prescriptions:
        # In production, would check against PBS database
        pass  # Placeholder for PBS validation

    layer_2_result = {
        "passed": layer_2_passed,
        "score": 5.0 if layer_2_passed else 3.0,
        "feedback": "Australian medical standards compliance verified" if layer_2_passed else "Some Australian terminology issues detected",
        "errors": layer_2_errors,
    }

    # Layer 3: Claude AI clinical assessment against THIS case's answer-key.
    # Replaces the former hardcoded 12.5/15 mock (PRD-EMR-PRACTICE-001): the note
    # is now graded on captured-vs-expected findings + critical-error detection.
    mock_patient = db.query(MockPatient).filter(MockPatient.id == emr_session.patient_id).first()
    validation_criteria = (mock_patient.validation_criteria if mock_patient else None) or {}

    assessment = assess_submission_sync(
        data.final_soap_note,
        validation_criteria,
        {"layer_1": layer_1_result, "layer_2": layer_2_result},
    )

    overall_score = float(assessment.get("overall_score", 0.0))
    # Claude AI outage (missing Vault key or API error): the engine echoes the
    # validator's ``ai_unavailable`` flag. In that case we must NOT fabricate a
    # graded FAIL from the 0.0 fallback score — see the ai_unavailable branch below.
    ai_unavailable = bool(assessment.get("ai_unavailable"))

    # assess_submission already applies the authoritative PASS/FAIL rule; recompute
    # defensively if absent. When the AI layer is unavailable there is no
    # authoritative decision, so pass_fail is left as None (not a fabricated FAIL).
    if ai_unavailable:
        pass_fail = None
    else:
        pass_fail = assessment.get("pass_fail")
        if pass_fail is None:
            pass_fail = decide_pass_fail(assessment, validation_criteria)

    critical_errors = assessment.get("critical_errors_committed", []) or []
    layer_3_result = {
        "passed": False if ai_unavailable else bool(pass_fail),
        "score": overall_score,
        "feedback": (
            "AI assessment temporarily unavailable — submission not graded, please re-submit."
            if ai_unavailable
            else (
                "; ".join(assessment.get("accuracy_notes", []) or [])
                or "Case-specific clinical assessment completed"
            )
        ),
        "errors": critical_errors,
        # Retained so the persisted layer_3_ai JSON explains WHY the learner
        # passed/failed (the response's ValidationLayerResult ignores these extra
        # keys, but the DB row and score_breakdown keep the full context).
        "critical_errors_committed": critical_errors,
        "missing_elements": assessment.get("missing_elements", []) or [],
    }

    performance_summary = {
        "time_taken_minutes": round(
            (datetime.utcnow() - emr_session.started_at).total_seconds() / 60, 2
        ),
        "typing_metrics": data.typing_metrics,
    }
    next_steps = {
        "recommended_practice": f"Continue practicing {emr_session.specialty} cases",
        "focus_areas": assessment.get("improvements", []) or [],
    }
    australian_compliance = {
        "terminology": (
            "✓ Correct Australian terminology used"
            if layer_2_result["passed"]
            else "⚠ Australian terminology issues detected"
        ),
    }

    # Persisted verbatim to score_breakdown; keeps both the assessment contract
    # (for analytics / the GET read path) and the display fields the response needs.
    score_breakdown = {
        "overall_score": overall_score,
        # Authoritative decision from decide_pass_fail; None when the AI layer was
        # unavailable (no authoritative grade). This is the single source of truth
        # the client must display — it must never be recomputed with a different rule.
        "pass_fail": None if ai_unavailable else bool(pass_fail),
        "ai_unavailable": ai_unavailable,
        "completeness": assessment.get("completeness", {}),
        "captured": assessment.get("captured", []),
        "missing_elements": assessment.get("missing_elements", []),
        "critical_errors_committed": critical_errors,
        "accuracy_notes": assessment.get("accuracy_notes", []),
        "category_scores": assessment.get("category_scores", {}),
        "strengths": assessment.get("strengths", []),
        "improvements": assessment.get("improvements", []),
        "red_flags": critical_errors,
        "australian_compliance": australian_compliance,
        "layer_1_zod": layer_1_result,
        "layer_2_python": layer_2_result,
        "layer_3_ai": layer_3_result,
        "performance_summary": performance_summary,
        "next_steps": next_steps,
    }

    elapsed_seconds = int((datetime.utcnow() - emr_session.started_at).total_seconds())
    response_message = None

    if ai_unavailable:
        # AI outage: preserve the student's work but do NOT grade. Leave the session
        # in_progress with no authoritative score and NO EMRValidationResult row, so
        # the student can re-submit and re-run the assessment once Claude is back.
        emr_session.status = "in_progress"
        emr_session.submitted_at = None
        emr_session.elapsed_time_seconds = elapsed_seconds
        emr_session.validation_score = None
        emr_session.score_breakdown = score_breakdown  # carries ai_unavailable=True
        emr_session.typing_metrics = data.typing_metrics
        response_message = (
            "AI assessment is temporarily unavailable. Your work has been saved but "
            "not graded — please re-submit shortly to run the assessment."
        )
        db.commit()
        db.refresh(emr_session)
    else:
        # Update session with the REAL score
        emr_session.status = "graded"
        emr_session.submitted_at = datetime.utcnow()
        emr_session.elapsed_time_seconds = elapsed_seconds
        emr_session.validation_score = overall_score
        emr_session.score_breakdown = score_breakdown
        emr_session.typing_metrics = data.typing_metrics

        # Persist a validation-result row (one per session). Columns match
        # Alembic migration 008 (the live-DB source of truth). layer_3_ai retains
        # the assessment's critical_errors_committed & missing_elements so the
        # learner can see WHY they passed/failed.
        db.add(
            EMRValidationResult(
                session_id=session_id,
                validation_type="emr_practice",
                layer_1_zod=layer_1_result,
                layer_2_python=layer_2_result,
                layer_3_ai=layer_3_result,
                overall_score=overall_score,
                passed=bool(pass_fail),
                strengths=score_breakdown["strengths"],
                improvements=score_breakdown["improvements"],
                red_flags=score_breakdown["red_flags"],
            )
        )

        db.commit()
        db.refresh(emr_session)

    # Build validation results
    validation_results = ValidationResult(
        overall_score=overall_score,
        pass_fail=None if ai_unavailable else bool(pass_fail),
        category_scores=score_breakdown["category_scores"],
        completeness=score_breakdown["completeness"] or None,
        captured=score_breakdown["captured"],
        missing_elements=score_breakdown["missing_elements"],
        strengths=score_breakdown["strengths"],
        improvements=score_breakdown["improvements"],
        red_flags=score_breakdown["red_flags"],
        australian_compliance=australian_compliance,
        ai_unavailable=True if ai_unavailable else None,
        layer_1_zod=ValidationLayerResult(**layer_1_result),
        layer_2_python=ValidationLayerResult(**layer_2_result),
        layer_3_ai=ValidationLayerResult(**layer_3_result),
        performance_summary=performance_summary,
        next_steps=next_steps,
    )

    return SessionResponse(
        session_id=emr_session.id,
        validation_id=emr_session.id,
        patient=MockPatientResponse(
            id=mock_patient.id,
            name=mock_patient.name,
            age=mock_patient.age,
            gender=mock_patient.gender,
            presenting_complaint=mock_patient.presenting_complaint,
            specialty=mock_patient.specialty,
            vital_signs=mock_patient.vital_signs,
            medical_history=mock_patient.medical_history,
        ),
        specialty=emr_session.specialty,
        difficulty=emr_session.difficulty,
        started_at=emr_session.started_at,
        submitted_at=emr_session.submitted_at,
        elapsed_time_seconds=emr_session.elapsed_time_seconds,
        status=emr_session.status,
        auto_save_count=emr_session.auto_save_count,
        last_auto_save_at=emr_session.last_auto_save_at,
        validation_score=emr_session.validation_score,
        total_amc_score=emr_session.validation_score,
        validation_results=validation_results,
        soap_note=data.final_soap_note,
        typing_metrics=emr_session.typing_metrics,
        performance_summary=performance_summary,
        next_steps=next_steps,
        message=response_message,
    )


# ============================================================================
# ENDPOINT 5: DELETE /sessions/{session_id} - DELETE SESSION
# ============================================================================


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cancel/delete in-progress session.

    FLOW:
    1. Validate session exists and belongs to user
    2. Delete session from database (hard delete)
    3. Return 204 No Content

    AUTHORIZATION:
    - User can only delete their own sessions

    NOTE: This is a hard delete. In production, consider soft delete with is_deleted flag.
    """
    # Fetch session
    emr_session = db.query(EMRSession).filter(
        EMRSession.id == session_id
    ).first()

    if not emr_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Authorization check
    if current_user.role != UserRole.EDUCATOR and emr_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session",
        )

    # Delete related SOAP notes (cascade)
    db.query(EMRSOAPNote).filter(EMRSOAPNote.session_id == session_id).delete()

    # Delete related prescriptions (cascade)
    db.query(EMRPrescription).filter(EMRPrescription.session_id == session_id).delete()

    # Delete related pathology orders (cascade)
    db.query(EMRPathologyOrder).filter(EMRPathologyOrder.session_id == session_id).delete()

    # Delete session
    db.delete(emr_session)
    db.commit()

    return None  # 204 No Content


# ============================================================================
# ENDPOINT 6: GET /sessions - LIST USER'S SESSIONS (PAGINATED)
# ============================================================================


@router.get("/sessions")
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    status: Optional[str] = Query(None, description="Filter by status (in_progress, graded)"),
    user_id: Optional[UUID] = Query(None, description="Filter by user ID (UUID only)"),
):
    """
    List user's EMR sessions with pagination and filters.

    AUTHORIZATION:
    - User can only access their own sessions

    FILTERS:
    - specialty: Filter by medical specialty
    - status: Filter by session status (in_progress, graded)

    PAGINATION:
    - page: 1-indexed page number
    - per_page: Items per page (max 100)

    PERFORMANCE TARGET: <300ms (p95)
    """
    # Build base query
    query = db.query(EMRSession).filter(EMRSession.user_id == current_user.id)

    # Apply filters
    if specialty:
        query = query.filter(EMRSession.specialty == specialty)

    if status:
        query = query.filter(EMRSession.status == status)

    # user_id is validated as UUID by FastAPI/Pydantic (prevents SQL injection)
    # We ignore it in the query since users can only see their own sessions

    # Get total count
    total = query.count()

    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page  # Ceiling division

    # Apply pagination
    offset = (page - 1) * per_page
    query = query.order_by(desc(EMRSession.started_at)).limit(per_page).offset(offset)

    # Execute query
    sessions = query.all()

    # Build session list
    session_list = []
    for emr_session in sessions:
        # Fetch patient for each session
        mock_patient = db.query(MockPatient).filter(MockPatient.id == emr_session.patient_id).first()

        session_list.append({
            "session_id": str(emr_session.id),
            "specialty": emr_session.specialty,
            "difficulty": emr_session.difficulty,
            "status": emr_session.status,
            "started_at": emr_session.started_at.isoformat(),
            "submitted_at": emr_session.submitted_at.isoformat() if emr_session.submitted_at else None,
            "validation_score": emr_session.validation_score,
            "patient_name": mock_patient.name if mock_patient else "Unknown",
        })

    return {
        "sessions": session_list,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        }
    }
