import { useState } from 'react'
import { useOCR } from '@/hooks/useOCR'
import { useCustomerStore } from '@/store/customerStore'

const DOC_TYPES = ['aadhaar', 'pan', 'passbook', 'utility_bill']

export default function DocumentOCR() {
  const { customer } = useCustomerStore()
  const { result, isLoading, error, analyzeFile, clearResult } = useOCR(customer || {})
  const [docType, setDocType] = useState('aadhaar')

  const handleFile = (e) => {
    const file = e.target.files?.[0]
    if (file) analyzeFile(file, docType)
  }

  return (
    <div className="flex-1 overflow-y-auto p-4">
      <div className="text-[11px] font-syne font-bold text-muted uppercase tracking-widest mb-3">
        📄 Document Sight
      </div>

      {/* Doc type selector */}
      <div className="flex gap-1.5 mb-3 flex-wrap">
        {DOC_TYPES.map(t => (
          <button
            key={t}
            onClick={() => setDocType(t)}
            className={`px-2.5 py-1 rounded-md text-[10px] font-semibold border transition-all uppercase tracking-wide ${
              docType === t
                ? 'bg-accent2/20 border-accent2/40 text-accent2'
                : 'border-border text-muted hover:border-accent2/40'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Upload button */}
      <label className="flex items-center justify-center gap-2 w-full py-2.5 mb-3 border border-dashed border-border rounded-xl text-xs text-muted hover:border-accent2 hover:text-accent2 transition-colors cursor-pointer">
        📷 Capture / Upload Document
        <input type="file" accept="image/*" className="hidden" onChange={handleFile} />
      </label>

      {isLoading && (
        <div className="text-xs text-accent font-mono animate-pulse text-center py-3">
          🔍 Analyzing document with GPT-4o Vision...
        </div>
      )}

      {error && (
        <div className="text-xs text-critical bg-critical/10 border border-critical/20 rounded-lg px-3 py-2 mb-3">
          ⚠ {error}
        </div>
      )}

      {/* Demo / Result card */}
      <OCRResultCard result={result} />
    </div>
  )
}

function OCRResultCard({ result }) {
  // Show demo result if no real result yet
  const demo = {
    doc_type: 'aadhaar',
    extracted_fields: { name: 'Priya Sharma', dob: '12/03/1990', address: '2018 record' },
    cross_check_results: [
      { field: 'Name',  status: 'match',    detail: '' },
      { field: 'DOB',   status: 'match',    detail: '' },
      { field: 'Address', status: 'mismatch', detail: 'Address from 2018' },
    ],
    ocr_confidence: 0.97,
    staff_action: "Address does not match digital record. Request utility bill (electricity/gas/water) not older than 3 months.",
    verification_status: 'partial',
  }

  const data = result || demo

  const statusColor = {
    verified: 'text-accent2 border-accent2/30 bg-accent2/10',
    partial:  'text-gold border-gold/30 bg-gold/10',
    rejected: 'text-critical border-critical/30 bg-critical/10',
  }

  return (
    <div className="bg-surface2 border border-border rounded-xl overflow-hidden">
      <div className="flex items-center gap-2 px-3 py-2 border-b border-border">
        <span className="text-sm font-semibold capitalize">{data.doc_type}</span>
        <span className={`ml-auto px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${statusColor[data.verification_status]}`}>
          {data.verification_status}
        </span>
        {data.ocr_confidence && (
          <span className="text-[10px] text-muted font-mono">OCR {Math.round(data.ocr_confidence * 100)}%</span>
        )}
      </div>

      <div className="divide-y divide-border">
        {data.cross_check_results?.map((row, i) => (
          <div key={i} className="flex justify-between items-center px-3 py-2 text-xs">
            <span className="text-muted">{row.field}</span>
            <span className={`font-mono ${row.status === 'match' ? 'text-accent2' : 'text-critical'}`}>
              {row.status === 'match' ? '✓ Match' : `⚠ ${row.detail || 'Mismatch'}`}
            </span>
          </div>
        ))}
      </div>

      {data.staff_action && (
        <div className="px-3 py-2.5 border-t border-border bg-warn/5 flex gap-2">
          <span className="text-warn text-sm flex-shrink-0">🤖</span>
          <span className="text-[11px] text-orange-300 leading-relaxed">{data.staff_action}</span>
        </div>
      )}
    </div>
  )
}