import pytest
import sys
from pathlib import Path

from src.agent_labs.tools import ExecutionStatus

# Add lab src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_client_agent import build_registry_from_mcp


@pytest.mark.asyncio
async def test_lab_09_registry_executes_allowlisted_tools():
    registry = build_registry_from_mcp(allowlist={"add"})
    result = await registry.execute("add", a=1, b=2, __request_id="req-9")
    assert result.status == ExecutionStatus.SUCCESS
    assert result.output == 3.0
    assert result.metadata["request_id"] == "req-9"


@pytest.mark.asyncio
async def test_lab_09_allowlist_blocks_tools():
    registry = build_registry_from_mcp(allowlist=set())
    result = await registry.execute("add", a=1, b=2)
    assert result.status == ExecutionStatus.NOT_FOUND
