"""Configuration API endpoints."""
import sys
from pathlib import Path
import logging
from fastapi import APIRouter, HTTPException

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import ConfigRequest, ConfigResponse, AgentConfig, PresetConfig
from services.config_service import ConfigService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/config", tags=["config"])

# Singleton config service
config_service = ConfigService()


@router.get("/default", response_model=ConfigResponse)
async def get_default_config() -> ConfigResponse:
    """
    Get default agent configuration.
    
    Returns:
        ConfigResponse with default settings
    """
    try:
        config = config_service.get_default_config()
        logger.info("Retrieved default configuration")
        return ConfigResponse(
            success=True,
            config=config,
            message="Default configuration"
        )
    except Exception as e:
        logger.error(f"Failed to get default config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve default configuration")


@router.get("/presets", response_model=list[PresetConfig])
async def list_presets() -> list[PresetConfig]:
    """
    List all available preset configurations.
    
    Returns:
        List of PresetConfig objects
    """
    try:
        presets = config_service.list_presets()
        logger.info(f"Retrieved {len(presets)} presets")
        return presets
    except Exception as e:
        logger.error(f"Failed to list presets: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve presets")


@router.get("/presets/{preset_name}", response_model=PresetConfig)
async def get_preset(preset_name: str) -> PresetConfig:
    """
    Get a specific preset configuration by name.
    
    Args:
        preset_name: Name of preset (creative, precise, balanced)
        
    Returns:
        PresetConfig for the requested preset
        
    Raises:
        HTTPException: 404 if preset not found
    """
    try:
        preset = config_service.get_preset(preset_name)
        if not preset:
            logger.warning(f"Preset not found: {preset_name}")
            raise HTTPException(status_code=404, detail=f"Preset '{preset_name}' not found")
        
        logger.info(f"Retrieved preset: {preset_name}")
        return preset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get preset {preset_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve preset")


@router.post("/save", response_model=ConfigResponse)
async def save_config(request: ConfigRequest) -> ConfigResponse:
    """
    Save agent configuration for a session.
    
    Args:
        request: ConfigRequest with config and optional preset
        
    Returns:
        ConfigResponse with saved configuration
        
    Raises:
        HTTPException: 400 for validation errors
    """
    try:
        # Use session_id from request or fallback to default
        session_id = request.session_id or "default_session"
        
        # Apply preset if specified
        if request.preset:
            try:
                config = config_service.apply_preset(session_id, request.preset)
                logger.info(f"Applied preset '{request.preset}' to session {session_id}")
                return ConfigResponse(
                    success=True,
                    config=config,
                    message=f"Applied preset: {request.preset}"
                )
            except ValueError as e:
                logger.warning(f"Invalid preset: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))
        
        # Save custom configuration
        config = config_service.save_config(session_id, request.config)
        logger.info(f"Saved custom configuration for session {session_id}")
        return ConfigResponse(
            success=True,
            config=config,
            message="Configuration saved successfully"
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error saving config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save configuration")


@router.post("/reset", response_model=ConfigResponse)
async def reset_config(session_id: Optional[str] = None) -> ConfigResponse:
    """
    Reset configuration to default.
    
    Args:
        session_id: Optional session ID (query param or default to default_session)
    
    Returns:
        ConfigResponse with default configuration
    """
    try:
        session_id = session_id or "default_session"
        config = config_service.reset_config(session_id)
        logger.info(f"Reset configuration for session {session_id}")
        return ConfigResponse(
            success=True,
            config=config,
            message="Configuration reset to default"
        )
    except Exception as e:
        logger.exception(f"Failed to reset config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to reset configuration")


@router.get("/{session_id}", response_model=ConfigResponse)
async def get_config(session_id: str) -> ConfigResponse:
    """
    Get configuration for a specific session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        ConfigResponse with session configuration or default
    """
    try:
        config = config_service.get_config(session_id)
        logger.info(f"Retrieved configuration for session {session_id}")
        return ConfigResponse(
            success=True,
            config=config,
            message="Configuration retrieved"
        )
    except Exception as e:
        logger.exception(f"Failed to get config for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve configuration")
