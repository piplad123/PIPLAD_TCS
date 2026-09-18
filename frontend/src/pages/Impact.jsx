import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  BookOpen,
  Droplets,
  HandHeart,
  HeartPulse,
  Leaf,
  Recycle,
  Sprout,
  TreePine,
  Trophy,
  Users,
} from 'lucide-react';
import { fetchPublicImpact } from '../api';
import { impactAreasData } from '../data/aboutdata';
import '../styles/impact.css';

const programmeIcons = [
  { Icon: BookOpen, color: '#166534', bg: '#dcfce7' },
  { Icon: Users, color: '#075985', bg: '#e0f2fe' },
  { Icon: HeartPulse, color: '#9f1239', bg: '#ffe4e6' },
  { Icon: Leaf, color: '#166534', bg: '#dcfce7' },
  { Icon: Sprout, color: '#854d0e', bg: '#fef9c3' },
  { Icon: Trophy, color: '#7c2d12', bg: '#ffedd5' },
  { Icon: Recycle, color: '#134e4a', bg: '#ccfbf1' },
  { Icon: HandHeart, color: '#581c87', bg: '#f3e8ff' },
];

const sdgData = [
  { number: '2', title: 'Zero Hunger', color: '#dda63a' },
  { number: '3', title: 'Good Health & Well-being', color: '#4c9f38' },
  { number: '4', title: 'Quality Education', color: '#c5192d' },
  { number: '8', title: 'Decent Work & Growth', color: '#a21942' },
  { number: '13', title: 'Climate Action', color: '#3f7e44' },
  { number: '15', title: 'Life on Land', color: '#56c02b' },
];

function formatMetric(value) {
  const n = Number(value) || 0;
  return n.toLocaleString('en-IN');
}

function formatDate(value) {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  return date.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

function SectionHeading({ eyebrow, title, description, light = false }) {
  return (
    <div className={`impact-heading ${light ? 'is-light' : ''}`}>
      {eyebrow && <span className="impact-eyebrow">{eyebrow}</span>}
      <h2>{title}</h2>
      {description && <p>{description}</p>}
    </div>
  );
}

import usePageMeta from '../hooks/usePageMeta';

export default function Impact() {
  usePageMeta(
    'Our Impact',
    'See the measurable impact of Piplad Welfare Foundation across people, the environment, and communities.'
  );
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;

    fetchPublicImpact()
      .then((result) => {
        if (mounted) {
          setData(result);
          setError('');
        }
      })
      .catch((err) => {
        if (mounted) setError(err.message || 'Unable to load impact data.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const peopleGroup = useMemo(
    () => data?.groups?.find((g) => g.key === 'people'),
    [data]
  );
  const environmentGroup = useMemo(
    () => data?.groups?.find((g) => g.key === 'environmental'),
    [data]
  );
  const carbonGroup = useMemo(
    () => data?.groups?.find((g) => g.key === 'carbon'),
    [data]
  );

  const carbon = carbonGroup?.metrics?.[0];
  const hasCarbon = data?.has_verified_carbon_credits;

  const programmes = impactAreasData.areas.slice(0, 8);

  const primaryPeople = peopleGroup?.metrics?.slice(0, 2) || [];
  const environmentalMetrics = environmentGroup?.metrics || [];

  return (
    <main className="impact-page">
      {/* HERO */}
      <section className="impact-hero">
        <div className="container impact-hero-inner">
          <span className="impact-hero-badge">Piplad Welfare Foundation</span>
          <h1>Our Impact</h1>
          <p>
            Measuring progress. Demonstrating change. Building stronger communities.
          </p>
          <div className="impact-hero-actions">
            <Link to="/about" className="impact-ghost-button">
              Discover Our Work <ArrowRight size={18} />
            </Link>
            <Link to="/join" className="impact-ghost-button">
              Partner With Us <ArrowRight size={18} />
            </Link>
          </div>
        </div>
      </section>

      {/* IMPACT DASHBOARD */}
      <section className="impact-section impact-dashboard">
        <div className="container">
          <SectionHeading
            eyebrow="Impact Dashboard"
            title="Life-changing numbers, owned by real communities"
            description="Every figure below is published by the Piplad team and reflects verified activity across our programmes. Values update automatically whenever they change."
          />

          {loading ? (
            <div className="impact-empty-state">Loading impact data…</div>
          ) : error ? (
            <div className="impact-empty-state">{error}</div>
          ) : (
            <div className="impact-dashboard-grid">
              {primaryPeople.map((metric) => (
                <article className="impact-stat-card impact-stat-primary" key={metric.key}>
                  <div className="impact-stat-icon">
                    {metric.key === 'students_supported' ? <BookOpen size={26} /> : <Users size={26} />}
                  </div>
                  <div className="impact-stat-value">{formatMetric(metric.value)}+</div>
                  <div className="impact-stat-label">{metric.name}</div>
                </article>
              ))}

              {environmentalMetrics.slice(0, 1).map((metric) => (
                <article className="impact-stat-card impact-stat-primary impact-stat-nature" key={metric.key}>
                  <div className="impact-stat-icon"><TreePine size={26} /></div>
                  <div className="impact-stat-value">{formatMetric(metric.value)}+</div>
                  <div className="impact-stat-label">{metric.name}</div>
                </article>
              ))}
            </div>
          )}

          {data?.last_updated && !error && (
            <div className="impact-last-updated">
              Last updated: {formatDate(data.last_updated)}
            </div>
          )}
        </div>
      </section>

      {/* ENVIRONMENTAL IMPACT */}
      {environmentalMetrics.length > 0 && !loading && !error && (
        <section className="impact-section impact-environment">
          <div className="container">
            <SectionHeading
              eyebrow="Environmental Impact"
              title="Committed to a greener, more resilient future"
              description="Our green initiatives contribute measurable environmental outcomes — from plantation to conservation and estimated carbon impact."
            />

            <div className="impact-environment-grid">
              {environmentalMetrics.map((metric, index) => {
                const MetricIcon = [TreePine, Sprout, Droplets, Leaf][index] || Leaf;
                const n = Number(metric.value);

                if (metric.key === 'estimated_co2e' && n === 0) {
                  return null;
                }

                return (
                  <article className="impact-eco-card" key={metric.key}>
                    <div className="impact-eco-icon"><MetricIcon size={24} /></div>
                    <div className="impact-eco-value">{formatMetric(n)}{n > 0 && metric.unit ? ` ${metric.unit}` : ''}</div>
                    <div className="impact-eco-label">{metric.name}</div>
                  </article>
                );
              })}
            </div>

            {/* VERIFIED CARBON CREDITS */}
            <div className="impact-carbon">
              <SectionHeading
                eyebrow="Verified Carbon Credits"
                title="Credible carbon accounting"
                description="We only report carbon credits that have been formally verified and issued. We do not inflate numbers based on trees planted alone."
              />
              {carbon && hasCarbon ? (
                <div className="impact-carbon-verified">
                  <Leaf size={22} />
                  <span>{formatMetric(carbon.value)} {carbon.unit || 'credits'}</span>
                  <small>Verified carbon credits currently held.</small>
                </div>
              ) : (
                <div className="impact-carbon-verified impact-carbon-none">
                  <Leaf size={22} />
                  <span>No verified carbon credits currently reported.</span>
                  <small>We will publish verified credits here as soon as they are formally issued.</small>
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {/* IMPACT BY PROGRAMME */}
      <section className="impact-section impact-programmes">
        <div className="container">
          <div className="impact-programmes-header">
            <SectionHeading
              eyebrow="Where the Impact Comes From"
              title="Our programmes turn these numbers into real change"
              description="Each metric is connected to a programme, its evidence and the stories behind it — because big numbers mean nothing without proof."
            />
            <Link to="/about" className="impact-outline-button">Explore Our Programmes <ArrowRight size={17} /></Link>
          </div>

          <div className="impact-programme-grid">
            {programmes.map((programme, index) => {
              const { Icon, color, bg } = programmeIcons[index] || programmeIcons[0];
              return (
                <article className="impact-programme-card" key={programme.title}>
                  <div className="impact-programme-icon" style={{ background: bg, color }}>
                    <Icon size={22} />
                  </div>
                  <h3>{programme.shortTitle}</h3>
                  <p>{programme.description}</p>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      {/* SDG ALIGNMENT */}
      <section className="impact-section impact-sdg">
        <div className="container">
          <SectionHeading
            eyebrow="Sustainable Development Goals"
            title="Our work contributes to the global goals"
            description="We associate our programmes only with SDGs where Piplad can substantiate the connection through real activity and outcomes."
            light
          />

          <div className="impact-sdg-grid">
            {sdgData.map((sdg) => (
              <article className="impact-sdg-card" key={sdg.number}>
                <div className="impact-sdg-badge" style={{ background: sdg.color }}>
                  {sdg.number}
                </div>
                <div>
                  <strong>SDG {sdg.number}</strong>
                  <span>{sdg.title}</span>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* PARTNER CTA */}
      <section className="impact-cta">
        <div className="container">
          <div>
            <span className="impact-eyebrow">Be Part of the Change</span>
            <h2>Help us turn measured progress into lasting transformation.</h2>
            <p>Partner with us, volunteer, or support a programme — and watch our impact grow with evidence, not exaggeration.</p>
          </div>
          <div className="impact-cta-actions">
            <Link to="/join" className="btn btn-primary">Get Involved</Link>
            <Link to="/contact" className="impact-cta-ghost">Partner With Us <ArrowRight size={17} /></Link>
          </div>
        </div>
      </section>
    </main>
  );
}
