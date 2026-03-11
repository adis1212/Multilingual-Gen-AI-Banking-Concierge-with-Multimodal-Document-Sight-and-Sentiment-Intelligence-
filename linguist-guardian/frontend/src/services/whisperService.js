import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Transcribe an audio file (full upload).
 * @param {Blob} audioBlob  – audio data (webm/wav/ogg/mpeg)
 * @param {string} language – ISO code: mr, hi, ta, te, bn, en …
 * @param {string} channel  – "A" (customer) or "B" (staff)
 */
export async function transcribeAudio(audioBlob, language = 'mr', channel = 'A') {
    const form = new FormData()
    form.append('audio', audioBlob, 'recording.webm')
    form.append('language', language)
    form.append('channel', channel)

    const { data } = await axios.post(`${API_URL}/api/transcribe/`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
}

/**
 * Transcribe a streaming audio chunk (called every ~3 s).
 */
export async function transcribeChunk(audioBlob, language, channel, sessionId) {
    const form = new FormData()
    form.append('audio', audioBlob, 'chunk.webm')
    form.append('language', language)
    form.append('channel', channel)
    form.append('session_id', sessionId)

    const { data } = await axios.post(`${API_URL}/api/transcribe/stream-chunk`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
}
