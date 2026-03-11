/**
 * Detect language from text by analyzing Unicode script ranges.
 * Works for Indian languages without any external API call.
 */

const SCRIPT_RANGES = [
    { code: 'hi', name: 'Hindi', regex: /[\u0900-\u097F]/g },   // Devanagari
    { code: 'mr', name: 'Marathi', regex: /[\u0900-\u097F]/g },   // Devanagari (same script as Hindi)
    { code: 'bn', name: 'Bengali', regex: /[\u0980-\u09FF]/g },
    { code: 'ta', name: 'Tamil', regex: /[\u0B80-\u0BFF]/g },
    { code: 'te', name: 'Telugu', regex: /[\u0C00-\u0C7F]/g },
    { code: 'gu', name: 'Gujarati', regex: /[\u0A80-\u0AFF]/g },
    { code: 'kn', name: 'Kannada', regex: /[\u0C80-\u0CFF]/g },
    { code: 'ml', name: 'Malayalam', regex: /[\u0D00-\u0D7F]/g },
    { code: 'pa', name: 'Punjabi', regex: /[\u0A00-\u0A7F]/g },   // Gurmukhi
]

/**
 * Detect which Indian language a text is written in.
 * @param {string} text – input text
 * @returns {{ code: string, name: string, confidence: number } | null}
 */
export function detectLanguage(text) {
    if (!text || text.trim().length === 0) return null

    const totalChars = text.replace(/\s/g, '').length
    if (totalChars === 0) return null

    let bestMatch = null
    let bestScore = 0

    for (const script of SCRIPT_RANGES) {
        const matches = text.match(script.regex)
        const count = matches ? matches.length : 0
        const score = count / totalChars

        if (score > bestScore) {
            bestScore = score
            bestMatch = { code: script.code, name: script.name, confidence: Math.round(score * 100) }
        }
    }

    // If less than 10% match — probably English
    if (!bestMatch || bestScore < 0.1) {
        return { code: 'en', name: 'English', confidence: Math.round((1 - bestScore) * 100) }
    }

    return bestMatch
}

/**
 * Check if a text contains Devanagari script (Hindi or Marathi).
 */
export function isDevanagari(text) {
    return /[\u0900-\u097F]/.test(text)
}

/**
 * Get the display name for a language code.
 */
export function getLanguageName(code) {
    const map = {
        mr: 'Marathi', hi: 'Hindi', ta: 'Tamil', te: 'Telugu',
        bn: 'Bengali', gu: 'Gujarati', kn: 'Kannada', ml: 'Malayalam',
        pa: 'Punjabi', en: 'English',
    }
    return map[code] || code.toUpperCase()
}

export default detectLanguage
