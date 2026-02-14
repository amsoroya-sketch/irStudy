"""
AI Validation API endpoints with Kimi/Claude routing
Automatically uses Kimi (free) or Claude (paid) based on config
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional

from src.config import get_settings
from src.validators.ai_validator import AIValidator  # Original Claude validator
from src.validators.ai_validator_kimi import AIValidatorKimi  # Kimi validator


router = APIRouter(prefix='/api/v1/ai-validation', tags=['ai-validation'])

settings = get_settings()


def get_ai_validator():
    """
    Get AI validator based on configuration
    Returns Kimi validator (free) or Claude validator (paid)
    """
    if settings.ai_provider == 'kimi':
        return AIValidatorKimi(kimi_api_key=settings.kimi_api_key)
    elif settings.ai_provider == 'claude':
        return AIValidator(api_key=settings.anthropic_api_key)
    else:
        raise ValueError(f"Unknown AI provider: {settings.ai_provider}")


class AIValidationRequest(BaseModel):
    """AI validation request"""
    type: str  # 'soap', 'prescription', 'pathology'
    data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class AIValidationResponse(BaseModel):
    """AI validation response"""
    clinical_accuracy: float
    documentation_quality: Optional[float] = None
    completeness: Optional[float] = None
    overall_score: float
    feedback: str
    strengths: list[str]
    areas_for_improvement: list[str]
    learning_points: list[str]
    ai_provider: str  # 'kimi' or 'claude' - so user knows which was used


@router.post('/validate', response_model=AIValidationResponse)
async def ai_validate(request: AIValidationRequest):
    """
    Validate with AI (Kimi or Claude based on config)

    Args:
        request: AI validation request

    Returns:
        AI validation result with educational feedback
    """
    try:
        # Get appropriate validator
        validator = get_ai_validator()

        if request.type == 'soap':
            result = await validator.validate_soap_note(
                request.data,
                request.context
            )

        elif request.type == 'prescription':
            result = await validator.validate_prescription(
                request.data,
                request.context
            )

        elif request.type == 'pathology':
            result = await validator.validate_pathology_order(
                request.data,
                request.context
            )

        else:
            raise HTTPException(
                status_code=400,
                detail=f'Unknown validation type: {request.type}'
            )

        # Close validator if it's Kimi (has async client)
        if hasattr(validator, 'close'):
            await validator.close()

        return AIValidationResponse(
            clinical_accuracy=result.clinical_accuracy,
            documentation_quality=result.documentation_quality,
            completeness=result.completeness,
            overall_score=result.overall_score,
            feedback=result.feedback,
            strengths=result.strengths,
            areas_for_improvement=result.areas_for_improvement,
            learning_points=result.learning_points,
            ai_provider=settings.ai_provider  # Tell user which AI was used
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'AI validation failed: {str(e)}'
        )


@router.get('/health')
async def ai_health_check():
    """Check if AI validation service is available"""
    try:
        if settings.ai_provider == 'kimi':
            if not settings.kimi_api_key:
                return {
                    'status': 'unavailable',
                    'provider': 'kimi',
                    'message': 'KIMI_API_KEY not configured'
                }

            return {
                'status': 'available',
                'provider': 'kimi',
                'model': 'moonshot-v1-128k',
                'cost': 'FREE'
            }

        elif settings.ai_provider == 'claude':
            if not settings.anthropic_api_key:
                return {
                    'status': 'unavailable',
                    'provider': 'claude',
                    'message': 'ANTHROPIC_API_KEY not configured'
                }

            return {
                'status': 'available',
                'provider': 'claude',
                'model': 'claude-3-5-sonnet-20241022',
                'cost': 'PAID'
            }

        else:
            return {
                'status': 'error',
                'message': f'Unknown AI provider: {settings.ai_provider}'
            }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


@router.get('/provider')
async def get_provider_info():
    """Get current AI provider information"""
    return {
        'provider': settings.ai_provider,
        'enabled': settings.ai_validation_enabled,
        'cost': 'FREE' if settings.ai_provider == 'kimi' else 'PAID'
    }
