import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Synthesize speech using Sarvam AI via backend TTS route.
 * Better accent for Indian regional languages than ElevenLabs.
 *
 * @param {string} text     – text to speak
 * @param {string} language – ISO code (mr, hi, ta, te, bn, gu, kn, en)
 * @returns {Promise<Blob>} audio blob
 */
export async function synthesizeSarvam(text, language = 'hi') {
    const { data } = await axios.post(
        `${API_URL}/api/tts/synthesize`,
        { text, language, emotion: 'neutral', provider: 'sarvam' },
        { responseType: 'blob' },
    )
    return data
}

/**
 * Play Sarvam audio blob through the browser speakers.
 * @param {Blob} audioBlob
 * @returns {HTMLAudioElement}
 */
export function playSarvamAudio(audioBlob) {
    const url = URL.createObjectURL(audioBlob)
    const audio = new Audio(url)
    audio.addEventListener('ended', () => URL.revokeObjectURL(url))
    audio.play()
    return audio
}

/**
 * Convenience: synthesize with Sarvam + play in one call.
 */
export async function speakSarvam(text, language = 'hi') {
    const blob = await synthesizeSarvam(text, language)
    return playSarvamAudio(blob)
}

/**
 * Get list of supported TTS languages.
 */
export async function getSupportedLanguages() {
    const { data } = await axios.get(`${API_URL}/api/tts/languages`)
    return data.languages
}
