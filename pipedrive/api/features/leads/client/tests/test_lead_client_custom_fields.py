"""Targeted tests for custom_fields payload merging in LeadClient."""
from unittest.mock import AsyncMock

import pytest

from pipedrive.api.features.leads.client.lead_client import LeadClient


@pytest.fixture
def mock_base_client():
    base_client = AsyncMock()
    base_client.request = AsyncMock()
    return base_client


@pytest.fixture
def lead_client(mock_base_client):
    return LeadClient(mock_base_client)


@pytest.mark.asyncio
async def test_create_lead_merges_custom_fields_into_payload(
    lead_client, mock_base_client
):
    """custom_fields keys are spread into the top-level payload (Pipedrive convention)."""
    mock_base_client.request.return_value = {
        "success": True,
        "data": {"id": "lead-uuid", "title": "Test"},
    }

    await lead_client.create_lead(
        title="Test Lead",
        person_id=123,
        custom_fields={
            "abc123def456": 7,
            "ghi789jkl012": "New Jersey",
            "mno345pqr678": 250,
        },
    )

    call_kwargs = mock_base_client.request.call_args.kwargs
    payload = call_kwargs["json_payload"]
    assert payload["title"] == "Test Lead"
    assert payload["person_id"] == 123
    assert payload["abc123def456"] == 7
    assert payload["ghi789jkl012"] == "New Jersey"
    assert payload["mno345pqr678"] == 250


@pytest.mark.asyncio
async def test_update_lead_merges_custom_fields_into_payload(
    lead_client, mock_base_client
):
    """update_lead also spreads custom_fields into the top-level payload."""
    mock_base_client.request.return_value = {
        "success": True,
        "data": {"id": "lead-uuid"},
    }

    await lead_client.update_lead(
        lead_id="123e4567-e89b-12d3-a456-426614174000",
        custom_fields={"outreach_status_key": 3, "total_students_key": 1850},
    )

    call_kwargs = mock_base_client.request.call_args.kwargs
    payload = call_kwargs["json_payload"]
    assert payload["outreach_status_key"] == 3
    assert payload["total_students_key"] == 1850


@pytest.mark.asyncio
async def test_create_lead_no_custom_fields_unchanged(lead_client, mock_base_client):
    """When custom_fields is None, payload should not contain any extra keys."""
    mock_base_client.request.return_value = {
        "success": True,
        "data": {"id": "lead-uuid"},
    }

    await lead_client.create_lead(
        title="Test Lead",
        person_id=123,
    )

    payload = mock_base_client.request.call_args.kwargs["json_payload"]
    assert set(payload.keys()) == {"title", "person_id"}
