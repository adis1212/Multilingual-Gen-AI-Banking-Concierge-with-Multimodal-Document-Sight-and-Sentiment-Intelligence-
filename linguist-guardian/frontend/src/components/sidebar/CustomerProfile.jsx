import { useCustomerStore } from '@/store/customerStore'

export default function CustomerProfile() {
  const { customer, isLoading } = useCustomerStore()

  if (isLoading) return (
    <div className="p-5 border-b border-border animate-pulse">
      <div className="h-4 bg-surface2 rounded w-3/4 mb-2" />
      <div className="h-3 bg-surface2 rounded w-1/2" />
    </div>
  )

  if (!customer) return null

  const kycColor = customer.kyc_status === 'full' ? 'text-accent2'
    : customer.kyc_status === 'partial' ? 'text-gold' : 'text-critical'

  return (
    <div className="p-4 border-b border-border">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-blue-900 to-accent flex items-center justify-center font-syne font-extrabold text-base">
          {customer.name.split(' ').map(n => n[0]).join('')}
        </div>
        <div>
          <div className="font-syne font-bold text-sm">{customer.name}</div>
          <div className="font-mono text-[11px] text-muted">CIF #{customer.id}</div>
        </div>
      </div>

      {/* Metadata grid */}
      <div className="grid grid-cols-2 gap-2">
        <MetaItem label="CIBIL Score"    value={customer.cibil_score}  color="text-accent2" />
        <MetaItem label="Balance"        value={`₹${customer.account_balance.toLocaleString('en-IN')}`} />
        <MetaItem label="KYC Status"     value={customer.kyc_status.charAt(0).toUpperCase() + customer.kyc_status.slice(1) + (customer.kyc_status !== 'full' ? ' ⚠' : ' ✓')} color={kycColor} />
        <MetaItem label="Loan Status"    value="None ✓"  color="text-accent2" />
        <MetaItem label="Language"       value={customer.language.toUpperCase()} color="text-accent" />
        <MetaItem label="Last Visit"     value="14 days ago" />
      </div>
    </div>
  )
}

function MetaItem({ label, value, color = 'text-text' }) {
  return (
    <div className="p-2.5 bg-surface2 rounded-lg border border-border">
      <div className="text-[10px] text-muted uppercase tracking-wide mb-1">{label}</div>
      <div className={`font-mono text-xs font-medium ${color}`}>{value}</div>
    </div>
  )
}