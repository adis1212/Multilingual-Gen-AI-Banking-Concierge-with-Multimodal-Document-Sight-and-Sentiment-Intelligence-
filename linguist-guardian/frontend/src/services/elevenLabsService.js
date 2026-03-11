import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Synthesize speech using ElevenLabs via backend TTS route.
 * Returns an audio Blob that can be played in the browser.
 *
 * @param {string} text     – text to speak
 * @param {string} language – ISO code (mr, hi, ta, te, bn, en …)
 * @param {string} emotion  – customer emotion for adaptive tone
 * @returns {Promise<Blob>} MP3 audio blob
 */
export async function synthesizeSpeech(text, language = 'hi', emotion = 'neutral') {
    const { data } = await axios.post(
        `${API_URL}/api/tts/synthesize`,
        { text, language, emotion, provider: 'elevenlabs' },
        { responseType: 'blob' },
    )
    return data
}

/**
 * Play audio blob through the browser speakers.
 * @param {Blob} audioBlob – MP3 audio blob
 * @returns {HTMLAudioElement}
 */
export function playAudioBlob(audioBlob) {
    const url = URL.createObjectURL(audioBlob)
    const audio = new Audio(url)
    audio.addEventListener('ended', () => URL.revokeObjectURL(url))
    audio.play()
    return audio
}

/**
 * Convenience: synthesize + play in one call.
 */
export async function speakText(text, language = 'hi', emotion = 'neutral') {
    const blob = await synthesizeSpeech(text, language, emotion)
    return playAudioBlob(blob)
}
