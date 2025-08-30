/**
 * Tax Rounding Utility Functions
 * Implements proper tax rounding: 456.49 → 456, 456.50 → 457
 * This ensures all tax calculations follow standard business rounding rules
 */

// Main tax rounding function - rounds to nearest integer
function roundTax(amount) {
    if (typeof amount !== 'number' || isNaN(amount)) {
        return 0;
    }
    // Round to nearest integer: 456.49 → 456, 456.50 → 457
    return Math.round(amount);
}

// Round tax amount with proper business logic
function roundTaxAmount(amount) {
    return roundTax(amount);
}

// Calculate GST with proper rounding
function calculateGST(baseAmount, gstPercentage) {
    if (!baseAmount || !gstPercentage) return 0;
    const gstAmount = (baseAmount * gstPercentage) / 100;
    return roundTaxAmount(gstAmount);
}

// Calculate CGST (half of total GST)
function calculateCGST(baseAmount, gstPercentage) {
    const totalGST = calculateGST(baseAmount, gstPercentage);
    return roundTaxAmount(totalGST / 2);
}

// Calculate SGST (half of total GST)
function calculateSGST(baseAmount, gstPercentage) {
    const totalGST = calculateGST(baseAmount, gstPercentage);
    return roundTaxAmount(totalGST / 2);
}

// Calculate total with GST including proper rounding
function calculateTotalWithGST(baseAmount, gstPercentage) {
    const gstAmount = calculateGST(baseAmount, gstPercentage);
    return baseAmount + gstAmount;
}

// Format currency with proper Indian formatting
function formatCurrency(amount) {
    return `₹ ${Number(amount).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
}

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        roundTax,
        roundTaxAmount,
        calculateGST,
        calculateCGST,
        calculateSGST,
        calculateTotalWithGST,
        formatCurrency
    };
}
