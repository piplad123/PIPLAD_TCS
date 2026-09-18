
import { Heart } from 'lucide-react';
import { cloudinaryUrl } from '../api';

export default function CauseCard({ cause, onDonate }) {
  const percentage = Math.min(
    100,
    Math.round(((cause.raised_amount || 0) / (cause.target_amount || 1)) * 100)
  );

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Image Container */}
      <div style={{ position: 'relative', height: '200px', overflow: 'hidden' }}>
        <img
          loading="lazy"
          decoding="async"
          src={cloudinaryUrl(cause.image_url, { width: 700 }) || 'https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?auto=format&fit=crop&q=80&w=800'}
          alt={cause.title}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
        />
        <span
          className="badge badge-green"
          style={{ position: 'absolute', top: '12px', left: '12px', boxShadow: '0 2px 6px rgba(0,0,0,0.15)' }}
        >
          {cause.category || 'Welfare'}
        </span>
      </div>

      {/* Card Content */}
      <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.6rem', lineHeight: 1.35 }}>
          {cause.title}
        </h3>
        <p style={{ fontSize: '0.9rem', color: '#475569', marginBottom: '1.25rem', flexGrow: 1, lineHeight: 1.5 }}>
          {cause.short_description}
        </p>

        {/* Progress Bar & Amounts */}
        <div style={{ marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.4rem' }}>
            <span style={{ color: '#059669' }}>
              ₹{(cause.raised_amount || 0).toLocaleString('en-IN')} Raised
            </span>
            <span style={{ color: '#64748b' }}>
              Goal: ₹{(cause.target_amount || 0).toLocaleString('en-IN')}
            </span>
          </div>
          <div className="progress-bar-bg">
            <div className="progress-bar-fill" style={{ width: `${percentage}%` }} />
          </div>
          <div style={{ textAlign: 'right', fontSize: '0.75rem', fontWeight: 700, color: '#059669', marginTop: '0.25rem' }}>
            {percentage}% Funded
          </div>
        </div>

        {/* Action Button */}
        <button
          className="btn btn-primary"
          onClick={() => onDonate(cause)}
          style={{ width: '100%', gap: '0.5rem' }}
        >
          <Heart size={18} fill="#ffffff" /> Donate to Cause
        </button>
      </div>
    </div>
  );
}
