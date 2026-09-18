import { useEffect, useState } from 'react';
import { Award } from 'lucide-react';
import { cloudinaryUrl, fetchCertificates, resolveMediaUrl } from '../api';

import usePageMeta from '../hooks/usePageMeta';

export default function Certificates() {
  usePageMeta(
    'Certificates',
    'Official certificates issued by Piplad Welfare Foundation — view and verify.'
  );
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;

    async function load() {
      try {
        const data = await fetchCertificates();
        if (mounted) setCertificates(data);
      } catch {
        if (mounted) setError('Failed to load certificates.');
      } finally {
        if (mounted) setLoading(false);
      }
    }

    load();

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div>
      <section style={{ background: '#0f172a', color: '#fff', padding: '4rem 0', textAlign: 'center' }}>
        <div className="container">
          <span className="badge badge-green" style={{ marginBottom: '0.75rem' }}>Legal & Documents</span>
          <h1 className="heading-xl" style={{ marginBottom: '0.75rem' }}>Our Certificates</h1>
          <p className="subheading" style={{ color: '#94a3b8', margin: '0 auto' }}>
            Our certifications and registrations help donors, institutions and corporate partners support our work with confidence.
          </p>
        </div>
      </section>
      <section className="section-padding" style={{ background: '#f8fafc' }}>
        <div className="container">
          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem 0', color: '#64748b' }}>Loading certifications…</div>
          ) : error ? (
            <div style={{ textAlign: 'center', padding: '3rem 0', color: '#b91c1c' }}>{error}</div>
          ) : certificates.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem 0', color: '#64748b' }}>
              Certification documents will be displayed here soon.
            </div>
          ) : (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: '1.5rem',
              }}
            >
              {certificates.map((certificate) => (
                <article
                  key={certificate.id}
                  className="card"
                  style={{ overflow: 'hidden', display: 'flex', flexDirection: 'column' }}
                >
                  {certificate.image_url ? (
                    <img
                      loading="lazy"
                      decoding="async"
                      src={cloudinaryUrl(resolveMediaUrl(certificate.image_url), { width: 700 })}
                      alt={certificate.title}
                      style={{ width: '100%', height: 200, objectFit: 'cover' }}
                    />
                  ) : (
                    <div
                      style={{
                        height: 200,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        background: 'linear-gradient(135deg, #f0fdf4, #ecfccb)',
                      }}
                    >
                      <Award size={48} color="#059669" />
                    </div>
                  )}
                  <div style={{ padding: '1.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '.5rem', marginBottom: '.5rem' }}>
                      <Award size={18} color="#059669" />
                      <h3 style={{ margin: 0, color: '#0f172a' }}>{certificate.title}</h3>
                    </div>
                    {certificate.description && (
                      <p style={{ color: '#64748b', lineHeight: 1.6, margin: 0 }}>{certificate.description}</p>
                    )}
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
