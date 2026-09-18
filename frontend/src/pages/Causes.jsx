import { useEffect, useState } from 'react';
import { fetchCauses } from '../api';
import CauseCard from '../components/CauseCard';
import { ShieldCheck } from 'lucide-react';

import usePageMeta from '../hooks/usePageMeta';

export default function Causes({ onSelectCauseToDonate }) {
  usePageMeta(
    'Our Causes',
    'Support Piplad Welfare Foundation causes — healthcare, education, zero hunger, and women empowerment. Every donation is 80G tax exempt.'
  );
  const [causes, setCauses] = useState([]);
  const [filter, setFilter] = useState('All');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCauses()
      .then((data) => {
        setCauses(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const categories = ['All', 'Healthcare', 'Education', 'Relief', 'Empowerment'];

  const filteredCauses = filter === 'All'
    ? causes
    : causes.filter((c) => (c.category || '').toLowerCase() === filter.toLowerCase());

  return (
    <div>
      {/* Header Banner */}
      <section style={{ background: '#0f172a', color: '#ffffff', padding: '4rem 0 3rem 0', textAlign: 'center' }}>
        <div className="container">
          <span className="badge badge-green" style={{ marginBottom: '0.75rem' }}>
            <ShieldCheck size={16} /> Verified Campaigns
          </span>
          <h1 className="heading-xl" style={{ color: '#ffffff', marginBottom: '0.75rem' }}>Our Active Welfare Causes</h1>
          <p className="subheading" style={{ color: '#94a3b8', margin: '0 auto' }}>
            Browse through our transparent welfare projects. Choose a cause close to your heart and make an immediate impact.
          </p>
        </div>
      </section>

      {/* Main Section */}
      <section className="section-padding" style={{ background: '#f8fafc' }}>
        <div className="container">
          {/* Category Filter Tabs */}
          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', marginBottom: '2.5rem', flexWrap: 'wrap' }}>
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setFilter(cat)}
                style={{
                  padding: '0.6rem 1.4rem',
                  borderRadius: '999px',
                  border: filter === cat ? '2px solid #059669' : '1px solid #cbd5e1',
                  background: filter === cat ? '#059669' : '#ffffff',
                  color: filter === cat ? '#ffffff' : '#334155',
                  fontWeight: 600,
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  transition: 'all 0.2s'
                }}
              >
                {cat}
              </button>
            ))}
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '4rem 0', color: '#64748b' }}>Loading campaigns...</div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(290px, 1fr))', gap: '2rem' }}>
              {filteredCauses.map((cause) => (
                <CauseCard key={cause.id} cause={cause} onDonate={(c) => onSelectCauseToDonate(c)} />
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
