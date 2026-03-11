/**
 * Format a number as Indian Rupee currency.
 * Uses the Indian numbering system (lakhs, crores).
 *
 * @param {number} amount  – raw number
 * @param {object} options – { compact: bool, decimals: number }
 * @returns {string}       – formatted string, e.g. "₹1,23,456.00"
 */
export function formatINR(amount, { compact = false, decimals = 2 } = {}) {
    if (amount == null || isNaN(amount)) return '₹0'

    if (compact) {
        if (Math.abs(amount) >= 1_00_00_000) {
            return `₹${(amount / 1_00_00_000).toFixed(1)}Cr`
        }
        if (Math.abs(amount) >= 1_00_000) {
            return `₹${(amount / 1_00_000).toFixed(1)}L`
        }
        if (Math.abs(amount) >= 1_000) {
            return `₹${(amount / 1_000).toFixed(1)}K`
        }
    }

    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
    }).format(amount)
}

/**
 * Parse a formatted INR string back to a number.
 * @param {string} str – formatted string like "₹1,23,456.00"
 * @returns {number}
 */
export function parseINR(str) {
    if (!str) return 0
    return Number(str.replace(/[₹,\s]/g, '')) || 0
}

export default formatINR
