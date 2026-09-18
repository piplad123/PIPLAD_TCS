
import { Heart, ShieldCheck, CheckCircle2, Building2, FileText } from 'lucide-react';

import usePageMeta from '../hooks/usePageMeta';

export default function Donate({ onOpenDonate }) {
  usePageMeta(
    'Donate',
    'Donate to Piplad Welfare Foundation. 80G tax-exempt contributions supporting healthcare, education, food security, and women empowerment.'
  );
  return (
    <div>
      {/* Header */}
      <section style={{ background: '#0f172a', color: '#ffffff', padding: '4rem 0 3rem 0', textAlign: 'center' }}>
        <div className="container">
          <span className="badge badge-green" style={{ marginBottom: '0.75rem' }}>
            <ShieldCheck size={16} /> 80G Tax Exemption Eligible
          </span>
          <h1 className="heading-xl" style={{ color: '#ffffff', marginBottom: '0.75rem' }}>Make a Direct Donation</h1>
          <p className="subheading" style={{ color: '#94a3b8', margin: '0 auto' }}>
            All donations to Piplad Welfare Foundation qualify for 50% tax deduction under Section 80G of the Indian Income Tax Act.
          </p>
        </div>
      </section>

      {/* Main Donation Section */}
      <section className="section-padding" style={{ background: '#ffffff' }}>
        <div className="container" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 320px), 1fr))', gap: '3rem' }}>
          
          {/* Card 1: Online Donation */}
          <div className="card donate-card" style={{ borderTop: '4px solid #059669' }}>
            <div style={{ background: '#d1fae5', color: '#059669', width: '50px', height: '50px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
              <Heart size={26} fill="#059669" />
            </div>
            <h2 className="heading-md" style={{ marginBottom: '0.75rem' }}>Instant Online Donation (Razorpay)</h2>
            <p style={{ fontSize: '0.95rem', color: '#475569', lineHeight: 1.6, marginBottom: '1.5rem' }}>
              Pay securely via UPI (Google Pay, PhonePe, Paytm), Credit/Debit Cards, Net Banking, or Wallets with instant digital 80G tax receipt generation.
            </p>
            <button className="btn btn-primary" onClick={onOpenDonate} style={{ width: '100%', padding: '0.9rem', fontSize: '1.05rem' }}>
              <Heart size={18} fill="#ffffff" /> Launch Payment Modal
            </button>
          </div>

          {/* Card 2: Bank Transfer Details */}
          <div className="card donate-card" style={{ borderTop: '4px solid #d97706' }}>
            <div style={{ background: '#fef3c7', color: '#d97706', width: '50px', height: '50px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
              <Building2 size={26} />
            </div>
            <h2 className="heading-md" style={{ marginBottom: '0.75rem' }}>Direct Bank Transfer (NEFT / RTGS / IMPS)</h2>
            <p style={{ fontSize: '0.9rem', color: '#475569', marginBottom: '1.25rem' }}>
              For large contributions or institutional donations, you may transfer directly to our foundation bank account:
            </p>
            <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1rem', fontSize: '0.9rem', color: '#0f172a', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <div><strong>Account Name:</strong> Piplad Welfare Foundation</div>
              <div><strong>Account No:</strong> 98765432109876</div>
              <div><strong>IFSC Code:</strong> SBIN0001234</div>
              <div><strong>Bank Name:</strong> State Bank of India</div>
              <div><strong>Branch:</strong> Main City Branch</div>
            </div>
          </div>

        </div>
      </section>

      {/* Tax Benefit Notice */}
      <section className="section-padding" style={{ background: '#f8fafc' }}>
        <div className="container" style={{ maxWidth: '850px' }}>
          <div className="card donate-card" style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
            <div style={{ background: '#d1fae5', color: '#059669', width: '60px', height: '60px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <FileText size={30} />
            </div>
            <div style={{ flex: 1 }}>
              <h3 className="heading-md" style={{ marginBottom: '0.5rem' }}>Tax Exemption Benefits under Section 80G</h3>
              <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '1rem' }}>
                Piplad Welfare Foundation is registered under Section 80G of the Income Tax Act, 1961. Indian taxpayers can claim 50% exemption on donations made to our foundation. Your tax certificate will contain your PAN number and official 80G registration details.
              </p>
              <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', fontSize: '0.85rem', fontWeight: 600, color: '#059669' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><CheckCircle2 size={16} /> Instant Email Receipt</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><CheckCircle2 size={16} /> Valid PAN Tax Proof</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
