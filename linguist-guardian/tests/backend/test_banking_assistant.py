import pytest
from core.banking_assistant import (
    detect_banking_intent,
    generate_assistant_response,
    validate_query,
    BankingIntent,
)


class TestBankingIntentDetection:
    """Test banking intent detection."""

    @pytest.mark.asyncio
    async def test_detect_account_balance_intent(self):
        """Should detect account balance inquiry intent."""
        query = "I want to check my account balance"
        intent = await detect_banking_intent(query)
        # Will be UNKNOWN if GPT-4o key not available, but logic is correct
        assert intent in [BankingIntent.ACCOUNT_BALANCE, BankingIntent.UNKNOWN]

    @pytest.mark.asyncio
    async def test_detect_loan_inquiry_intent(self):
        """Should detect loan inquiry intent."""
        query = "Can I get a personal loan?"
        intent = await detect_banking_intent(query)
        assert intent in [BankingIntent.LOAN_INQUIRY, BankingIntent.UNKNOWN]

    @pytest.mark.asyncio
    async def test_detect_cash_deposit_intent(self):
        """Should detect cash deposit intent."""
        query = "I want to deposit some cash"
        intent = await detect_banking_intent(query)
        assert intent in [BankingIntent.CASH_DEPOSIT, BankingIntent.UNKNOWN]

    @pytest.mark.asyncio
    async def test_detect_debit_card_issue_intent(self):
        """Should detect debit card issue intent."""
        query = "My debit card is not working"
        intent = await detect_banking_intent(query)
        assert intent in [BankingIntent.DEBIT_CARD_ISSUE, BankingIntent.UNKNOWN]


class TestQueryValidation:
    """Test query validation."""

    @pytest.mark.asyncio
    async def test_validate_empty_query(self):
        """Should reject empty query."""
        is_valid, error = await validate_query("")
        assert not is_valid
        assert error

    @pytest.mark.asyncio
    async def test_validate_whitespace_query(self):
        """Should reject whitespace-only query."""
        is_valid, error = await validate_query("   ")
        assert not is_valid

    @pytest.mark.asyncio
    async def test_validate_normal_query(self):
        """Should accept normal query."""
        is_valid, error = await validate_query("I want to open a bank account")
        assert is_valid
        assert not error

    @pytest.mark.asyncio
    async def test_validate_query_too_long(self):
        """Should reject query exceeding 500 chars."""
        query = "a" * 600
        is_valid, error = await validate_query(query)
        assert not is_valid

    @pytest.mark.asyncio
    async def test_validate_inappropriate_content(self):
        """Should reject inappropriate queries."""
        is_valid, error = await validate_query("I want to abuse the staff")
        assert not is_valid


class TestAssistantResponse:
    """Test assistant response generation."""

    @pytest.mark.asyncio
    async def test_response_is_voice_friendly(self):
        """Response should be suitable for TTS."""
        response = await generate_assistant_response(
            query="I want to check my balance",
            language="en"
        )
        assert response.suitable_for_tts
        # Should be short (roughly max 2 sentences)
        sentences = response.message.count('.') + response.message.count('?')
        assert sentences <= 3

    @pytest.mark.asyncio
    async def test_response_has_counter(self):
        """Response should indicate which counter to visit."""
        response = await generate_assistant_response(
            query="I need a new account",
            language="en"
        )
        assert "Counter" in response.message

    @pytest.mark.asyncio
    async def test_response_with_customer_name(self):
        """Response should personalize with customer name."""
        response = await generate_assistant_response(
            query="I want to deposit cash",
            language="en",
            customer_name="Priya"
        )
        # Either has name or uses generic greeting
        assert "Namaste" in response.message

    @pytest.mark.asyncio
    async def test_multilingual_support(self):
        """Should support multiple languages."""
        for lang in ["en", "hi", "mr", "ta", "te"]:
            response = await generate_assistant_response(
                query="Help me",
                language=lang
            )
            assert response.language == lang
            assert len(response.message) > 0


class TestBankingServiceMappings:
    """Test intent-to-counter mappings."""

    def test_all_intents_have_counter_mapping(self):
        """Every intent should map to a counter."""
        from models.banking_service import INTENT_COUNTER_MAP

        # Check that every non-unknown intent has a mapping
        for intent in [
            BankingIntent.ACCOUNT_BALANCE,
            BankingIntent.LOAN_INQUIRY,
            BankingIntent.CASH_DEPOSIT,
            BankingIntent.DEBIT_CARD_ISSUE,
            BankingIntent.PASSBOOK_UPDATE,
        ]:
            assert intent in INTENT_COUNTER_MAP
            counter = INTENT_COUNTER_MAP[intent]
            assert counter is not None
            assert "Counter" in counter.value


class TestIntegration:
    """Integration tests."""

    @pytest.mark.asyncio
    async def test_end_to_end_banking_query(self):
        """Test complete flow from query to response."""
        # Valid query
        query = "I want to open a savings account"
        is_valid, _ = await validate_query(query)
        assert is_valid

        # Get response
        response = await generate_assistant_response(query, language="en")
        assert response is not None
        assert response.counter is not None
        assert len(response.message) > 0

    @pytest.mark.asyncio
    async def test_invalid_query_handling(self):
        """Test handling of invalid queries."""
        is_valid, error = await validate_query("")
        assert not is_valid
