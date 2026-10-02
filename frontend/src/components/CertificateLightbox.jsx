import { useEffect } from 'react';
import { X } from 'lucide-react';
import { cloudinaryUrl, resolveMediaUrl } from '../api';

export default function CertificateLightbox({ certificate, onClose }) {
  useEffect(() => {
    if (!certificate) return undefined;

    const onKeyDown = (event) => {
      if (event.key === 'Escape') onClose();
    };

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [certificate, onClose]);

  if (!certificate) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={`${certificate.title} preview`}
      onClick={onClose}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 40,
        display: 'grid',
        placeItems: 'center',
        padding: 'clamp(1rem, 4vw, 3rem)',
        background: 'rgba(15, 23, 42, 0.94)',
      }}
    >
      <button
        type="button"
        aria-label="Close certificate preview"
        onClick={onClose}
        style={{
          position: 'fixed',
          top: '1rem',
          right: '1rem',
          zIndex: 41,
          display: 'grid',
          placeItems: 'center',
          width: 44,
          height: 44,
          border: '1px solid rgba(255,255,255,.3)',
          borderRadius: '50%',
          background: '#fff',
          color: '#0f172a',
          cursor: 'pointer',
        }}
      >
        <X size={22} />
      </button>

      <figure
        onClick={(event) => event.stopPropagation()}
        style={{
          margin: 0,
          maxWidth: 1100,
          width: '100%',
          maxHeight: '100%',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem',
        }}
      >
        <img
          src={cloudinaryUrl(resolveMediaUrl(certificate.image_url), { width: 1400 })}
          alt={certificate.title}
          style={{
            width: '100%',
            maxHeight: '78vh',
            objectFit: 'contain',
            borderRadius: 8,
            background: '#1e293b',
          }}
        />
        <figcaption style={{ color: '#e2e8f0', textAlign: 'center' }}>
          <strong style={{ display: 'block', color: '#fff' }}>{certificate.title}</strong>
          {certificate.description && (
            <span style={{ color: '#94a3b8' }}>{certificate.description}</span>
          )}
        </figcaption>
      </figure>
    </div>
  );
}
