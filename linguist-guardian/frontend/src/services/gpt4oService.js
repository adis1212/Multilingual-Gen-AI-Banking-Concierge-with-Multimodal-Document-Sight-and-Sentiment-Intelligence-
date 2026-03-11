import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Extract customer intent from a transcript.
 * @param {string} transcript      – raw transcript text
 * @param {string} language        – ISO code
 * @param {object} customerContext – optional context object
 * @param {string} sessionId       – active session id
 */
export async function extractIntent(transcript, language = 'mr', customerContext = {}, sessionId = '') {
    const { data } = await axios.post(`${API_URL}/api/intent/extract`, {
        transcript,
        language,
        customer_context: customerContext,
        session_id: sessionId,
    })
    return data
}

/**
 * Silent RBI compliance check on a staff utterance.
 * @param {string} staffUtterance – what the staff member said
 * @param {string} sessionId     – active session id
 */
export async function checkCompliance(staffUtterance, sessionId = '') {
    const { data } = await axios.post(`${API_URL}/api/intent/compliance`, {
        staff_utterance: staffUtterance,
        session_id: sessionId,
    })
    return data
}
