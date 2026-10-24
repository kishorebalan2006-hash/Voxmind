"""
Unit & Integration Tests for Ask the Meeting Q&A, Vector Embeddings, and Cross-Meeting Search.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.routes import chat, search, meetings
from app.services.search.fake_embedding_provider import FakeEmbeddingProvider
from app.services.search.vector_search_engine import VectorSearchEngine
from app.models.search import EmbeddingDocument
from app.services.chat.ask_meeting_service import AskMeetingService
from app.repositories.search_repository import SearchRepository
from app.repositories.chat_repository import ChatRepository
from app.repositories.transcript_repository import TranscriptRepository
from app.repositories.intelligence_repository import IntelligenceRepository
from tests.conftest import MockMeetingRepository


@pytest.mark.asyncio
async def test_fake_embedding_provider_generates_normalized_vectors():
    provider = FakeEmbeddingProvider(dimension=768)
    vec1 = await provider.generate_embedding("What decisions were ratified?")
    vec2 = await provider.generate_embedding("Who owns the project presentation?")

    assert len(vec1) == 768
    assert len(vec2) == 768
    # Test cosine similarity calculation
    sim = VectorSearchEngine.cosine_similarity(vec1, vec2)
    assert 0.0 <= sim <= 1.0


@pytest.mark.asyncio
async def test_vector_search_engine_hybrid_ranking():
    provider = FakeEmbeddingProvider(dimension=768)
    docs = [
        EmbeddingDocument(
            id="emb_01",
            organizationId="org_alpha",
            meetingId="mtg_001",
            transcriptSegmentId="seg_01",
            text="Alex is responsible for completing the streaming STT load testing by Friday.",
            embedding=await provider.generate_embedding("Alex is responsible for completing the streaming STT load testing by Friday."),
            speakerName="Sarah",
            timestamp="01:15",
        ),
        EmbeddingDocument(
            id="emb_02",
            organizationId="org_alpha",
            meetingId="mtg_002",
            transcriptSegmentId="seg_02",
            text="The team reviewed multi-tenant Firestore security rules and authentication.",
            embedding=await provider.generate_embedding("The team reviewed multi-tenant Firestore security rules and authentication."),
            speakerName="Alex",
            timestamp="02:30",
        ),
    ]

    q_emb = await provider.generate_embedding("Who is responsible for load testing?")
    results = VectorSearchEngine.search(
        query="Who is responsible for load testing?",
        query_embedding=q_emb,
        documents=docs,
        meeting_titles={"mtg_001": "Sprint Review", "mtg_002": "Security Audit"},
    )

    assert len(results) >= 1
    assert results[0].meetingId == "mtg_001"
    assert results[0].segmentId == "seg_01"


def test_ask_meeting_and_search_api_endpoints(test_client: TestClient, mock_user_alpha):
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha
    mock_repo = MockMeetingRepository()
    meetings._meeting_repo = mock_repo
    chat._meeting_repo = mock_repo
    search._meeting_repo = mock_repo

    search_repo = SearchRepository()
    chat_repo = ChatRepository()
    embed_provider = FakeEmbeddingProvider()
    ask_service = AskMeetingService(
        embedding_provider=embed_provider,
        search_repo=search_repo,
        chat_repo=chat_repo,
    )
    chat._ask_service = ask_service
    chat._chat_repo = chat_repo
    search._search_repo = search_repo
    search._embedding_provider = embed_provider

    # 1. Ask the Meeting
    res_ask = test_client.post(
        "/api/v1/meetings/mtg_001/ask",
        headers={"Authorization": "Bearer mock_token"},
        json={"question": "What decisions were made regarding transport?"},
    )
    assert res_ask.status_code == 200
    data = res_ask.json()
    assert data["meetingId"] == "mtg_001"
    assert "answer" in data

    # 2. Get meeting conversations
    res_conv = test_client.get(
        "/api/v1/meetings/mtg_001/conversations",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res_conv.status_code == 200
    convs = res_conv.json()
    assert len(convs) >= 1
    conv_id = convs[0]["id"]

    # 3. Get messages
    res_msgs = test_client.get(
        f"/api/v1/meetings/mtg_001/conversations/{conv_id}",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res_msgs.status_code == 200
    msgs = res_msgs.json()
    assert len(msgs) >= 2

    # 4. Semantic Cross-Meeting Search
    res_search = test_client.post(
        "/api/v1/search/query",
        headers={"Authorization": "Bearer mock_token"},
        json={"query": "load testing streaming WebSocket"},
    )
    assert res_search.status_code == 200
    search_data = res_search.json()
    assert "results" in search_data

    app.dependency_overrides.clear()
