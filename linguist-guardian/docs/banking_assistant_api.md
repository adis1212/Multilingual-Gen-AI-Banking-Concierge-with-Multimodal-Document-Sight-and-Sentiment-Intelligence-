# Banking Assistant API Documentation

## Overview

The Banking Assistant is an interactive voice-based feature for Union Bank of India branch customers. It helps customers identify the correct counter for their banking needs and provides polite, voice-friendly guidance.

## Features

- **Voice Input**: Customers can speak their requests (Web Speech API)
- **Multi-language Support**: Hindi, Marathi, Tamil, Telugu, Bengali, Gujarati, Kannada, Malayalam, English
- **Intent Detection**: AI-powered detection of banking needs
- **Counter Routing**: Automatic guidance to the correct service counter
- **Text-to-Speech**: Responses converted to speech for clarity
- **Personalization**: Optional customer name in responses

## Endpoints

### 1. Get Banking Help

**POST** `/api/banking-assistant/help`

Process a customer's banking query and provide counter guidance.

**Request:**
```json
{
  "query": "I want to open a new account",
  "language": "en",
  "customer_name": "Priya",
  "session_id": "session-123456"
}
```

**Parameters:**
- `query` (string, required): Customer's banking question
- `language` (string, optional): ISO 639-1 language code (default: "en")
  - Supported: `en`, `hi`, `mr`, `ta`, `te`, `bn`, `gu`, `kn`, `ml`
- `customer_name` (string, optional): Customer's name for personalization
- `session_id` (string, optional): Session identifier for logging

**Response:**
```json
{
  "intent": "new_account",
  "counter": "Counter 1 – Account Services",
  "message": "Welcome to Union Bank of India. Namaste. Please visit Counter 1 – Account Services to open a new account.",
  "language": "en",
  "suitable_for_tts": true
}
```

**Status Codes:**
- `200 OK`: Successfully processed query
- `400 Bad Request`: Invalid or empty query

**Example Usage (cURL):**
```bash
curl -X POST http://localhost:8000/api/banking-assistant/help \
  -H "Content-Type: application/json" \
  -d '{
    "query": "My debit card is not working",
    "language": "en",
    "customer_name": "Ramesh"
  }'
```

**Example Usage (JavaScript/Fetch):**
```javascript
const response = await fetch('http://localhost:8000/api/banking-assistant/help', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'I need to deposit cash',
    language: 'en',
    customer_name: 'Kavitha'
  })
});
const result = await response.json();
console.log(result.message);
// Output: Namaste, Kavitha. For cash deposit, please go to Counter 2 – Cash Deposit / Withdrawal.
```

---

### 2. Get Counter Information

**GET** `/api/banking-assistant/counter-info?counter_number=1`

Get detailed information about a specific counter.

**Query Parameters:**
- `counter_number` (integer, 1-5): Counter ID

**Response:**
```json
{
  "counter": "Counter 1 – Account Services",
  "services": [
    "Account balance inquiry",
    "New account opening",
    "KYC updates",
    "Account details"
  ],
  "token_prefix": "A"
}
```

**Example:**
```bash
curl http://localhost:8000/api/banking-assistant/counter-info?counter_number=2
```

---

### 3. Get Available Intents

**GET** `/api/banking-assistant/intents`

Get list of all supported banking intents.

**Response:**
```json
{
  "intents": [
    { "value": "account_balance", "display": "Account Balance" },
    { "value": "passbook_update", "display": "Passbook Update" },
    { "value": "cash_deposit", "display": "Cash Deposit" },
    { "value": "cash_withdrawal", "display": "Cash Withdrawal" },
    { "value": "loan_inquiry", "display": "Loan Inquiry" },
    { "value": "debit_card_issue", "display": "Debit Card Issue" },
    { "value": "new_account", "display": "New Account" },
    { "value": "kyc_update", "display": "KYC Update" },
    { "value": "internet_banking", "display": "Internet Banking" },
    { "value": "atm_issue", "display": "ATM Issue" },
    { "value": "unknown", "display": "Unknown" }
  ]
}
```

---

## Supported Banking Intents

| Intent | Counter | Services |
|--------|---------|----------|
| `account_balance` | 1 | Account balance inquiry |
| `passbook_update` | 4 | Passbook printing, statements |
| `cash_deposit` | 2 | Cash deposits |
| `cash_withdrawal` | 2 | Cash withdrawals |
| `loan_inquiry` | 3 | Loan details and applications |
| `debit_card_issue` | 5 | Card issues, new cards |
| `new_account` | 1 | Opening new accounts |
| `kyc_update` | 1 | KYC and document updates |
| `internet_banking` | 5 | Online banking help |
| `atm_issue` | 5 | ATM problems |
| `unknown` | 5 | General support (default) |

---

## Supported Languages

```
en - English
hi - Hindi
mr - Marathi
ta - Tamil
te - Telugu
bn - Bengali
gu - Gujarati
kn - Kannada
ml - Malayalam
```

---

## Frontend Integration

### React Component Usage

```jsx
import BankingAssistantPage from '@/pages/banking_assistant';

// In your routing
<Route path="/banking-assistant" element={<BankingAssistantPage />} />
```

### Key Features

1. **Voice Input**: Click "Start Listening" button to capture voice
2. **Language Selection**: Choose preferred language for input/output
3. **Personalization**: Enter customer name for personalized responses
4. **Text-to-Speech**: Click "Hear Response" to listen to the guidance
5. **Counter Display**: Visual indication of which counter to visit

---

## Voice Processing

### Input (Speech-to-Text)
- Uses Web Speech API for browser-based transcription
- Automatic language detection based on selected language
- Real-time interim results display

### Output (Text-to-Speech)
- Uses browser's SpeechSynthesis API
- Slower speech rate (0.9) for clarity
- Automatically uses selected language

---

## Error Handling

### Validation Errors

**Empty Query:**
```
HTTP 400 Bad Request
{ "detail": "Invalid query: Query is empty" }
```

**Query Too Long (>500 chars):**
```
HTTP 400 Bad Request
{ "detail": "Invalid query: Query too long" }
```

**Inappropriate Content:**
```
HTTP 400 Bad Request
{ "detail": "Invalid query: Query contains inappropriate language" }
```

---

## Response Format

All responses are designed to be:
1. **Short**: Maximum 2 sentences for voice playback clarity
2. **Simple**: Uses basic banking language, no jargon
3. **Actionable**: Clear guidance to specific counter
4. **Polite**: Respectful, professional tone
5. **Friendly**: Warm greeting, personalized when possible

---

## Example Interactions

### Example 1: Account Opening
**Query:** "I want to open a bank account"
**Response:** "Welcome to Union Bank of India. Please visit Counter 1 – Account Services to open a new account."

### Example 2: Loan Inquiry with Name
**Query:** "Can I get a personal loan?"
**Customer Name:** "Ramesh"
**Response:** "Namaste, Ramesh. Our loan specialist is at Counter 3 – Loan Desk. They'll assist you."

### Example 3: Debit Card Issue
**Query:** "My debit card is not working"
**Response:** "Please visit Counter 5 – Customer Support for your debit card issue."

### Example 4: Unknown Intent
**Query:** "Can you tell me the bank's history?"
**Response:** "Please visit Counter 5 – Customer Support. Our team will help you with your banking needs."

---

## Testing

### Unit Tests
```bash
cd linguist-guardian/backend
python -m pytest tests/backend/test_banking_assistant.py -v
```

### Manual Testing

Using curl:
```bash
curl -X POST http://localhost:8000/api/banking-assistant/help \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I want to update my passbook",
    "language": "en"
  }'
```

Using the web interface:
1. Navigate to `http://localhost:3000/banking-assistant`
2. Enter your question or click "Start Listening"
3. Click "Get Help"
4. View the counter guidance
5. Click "Hear Response" to listen

---

## Architecture

### Backend Flow
1. Customer query → Validation
2. Intent detection → GPT-4o analysis
3. Counter mapping → Database lookup
4. Response generation → TTS-friendly formatting

### Frontend Flow
1. Voice input → Web Speech API
2. Query submission → REST API call
3. Response parsing → Display counter info
4. TTS output → Browser SpeechSynthesis

---

## Environment Variables

```env
# Required for intent detection
OPENAI_API_KEY=sk-proj-...

# For TTS output (optional, uses browser native by default)
ELEVENLABS_API_KEY=sk_...

# Database for storing interactions (optional)
DATABASE_URL=sqlite:///./linguist.db
```

---

## Security Considerations

1. **Input Validation**: All queries validated for length and content
2. **Language Validation**: Only supported language codes accepted
3. **Rate Limiting**: Can be added via API gateway
4. **CORS**: Configured for frontend domain only

---

## Performance

- **Response Time**: < 2 seconds (including GPT-4o API call)
- **Max Query Length**: 500 characters
- **Concurrent Sessions**: Unlimited (async FastAPI)
- **Voice Processing**: Browser-based (no server overhead)

---

## Future Enhancements

1. **Emotion Detection**: Analyze customer tone for de-escalation
2. **Document OCR**: Verify documents for specific intents
3. **Queue Management**: Real-time counter wait times
4. **Multi-turn Conversations**: Follow-up questions support
5. **Analytics**: Track intent patterns and customer satisfaction

---

## Support

For issues or questions:
1. Check test cases in `tests/backend/test_banking_assistant.py`
2. Review example responses above
3. Check API response status codes and messages
4. Verify `.env` file has required API keys
