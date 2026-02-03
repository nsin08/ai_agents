"""Provider API endpoints for listing and validating providers."""
from fastapi import APIRouter, HTTPException
from typing import List

# Centralized path setup
import core.path_setup  # noqa: F401

from models import (
    ProviderInfo,
    ProviderRequest,
    ValidateKeyRequest,
    ValidateKeyResponse,
)
from services.provider_service import ProviderService

router = APIRouter(prefix="/providers", tags=["providers"])
provider_service = ProviderService()


@router.get("/", response_model=List[ProviderInfo])
async def list_providers(include_models: bool = False):
    """
    Get list of available LLM providers.
    
    Args:
        include_models: Whether to include supported model lists
        
    Returns:
        List of ProviderInfo objects
    """
    return await provider_service.list_providers(include_models=include_models)


@router.post("/validate", response_model=ValidateKeyResponse)
async def validate_api_key(request: ValidateKeyRequest):
    """
    Validate an API key for a provider.
    
    Args:
        request: Validation request with provider, key, and optional model
        
    Returns:
        ValidateKeyResponse with validation result
    """
    try:
        result = await provider_service.validate_api_key(
            provider=request.provider,
            api_key=request.api_key,
            model=request.model,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
