import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Heart, MapPin, Phone, Mail, ShieldCheck, Send } from 'lucide-react';
import SocialLinks from './SocialLinks';
import { fetchFooterFocus, fetchFooterQuickLinks, subscribeNewsletter } from '../api';
import { useSiteSettings } from '../hooks/useSiteSettings';

const DEFAULT_FOCUS = [
  'Childhood Cancer Healthcare',
  'Free Education & School Supplies',
  'Daily Ration & Warm Meals',
  'Women Skill Empowerment',
  'Emergency Medical Financial Aid',
];

const DEFAULT_QUICK_LINKS = [
  { label: 'About Our Foundation', path: '/about' },
  { label: 'Our Impact', path: '/impact' },
  { label: 'Current Welfare Causes', path: '/causes' },
  { label: 'Donate & 80G Benefits', path: '/donate' },
  { label: 'Media & Awards Gallery', path: '/gallery' },
  { label: 'Contact & Reach Us', path: '/contact' },
  { label: 'Refund & Cancellation Policy', path: '/terms' },
];

export default function Footer({ onOpenDonate }) {
  const [focusItems, setFocusItems] = useState(DEFAULT_FOCUS);
  const [quickLinks, setQuickLinks] = useState(DEFAULT_QUICK_LINKS);
  const { settings } = useSiteSettings();

  const [newsletterEmail, setNewsletterEmail] = useState('');
  const [newsletterState, setNewsletterState] = useState('idle');
  const [newsletterWebsite, setNewsletterWebsite] = useState('');

  const handleNewsletterSubmit = async (event) => {
    event.preventDefault();

    const email = newsletterEmail.trim();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      setNewsletterState('error');
      return;
    }

    setNewsletterState('loading');
    try {
      await subscribeNewsletter({ email, website: newsletterWebsite });
      setNewsletterEmail('');
      setNewsletterState('success');
      setTimeout(() => setNewsletterState('idle'), 6000);
    } catch (err) {
      console.error('Newsletter subscribe failed:', err);
      setNewsletterState('error');
    }
  };

  useEffect(() => {
    let isMounted = true;

    const loadFocus = async () => {
      try {
        const data = await fetchFooterFocus();

        if (isMounted && Array.isArray(data) && data.length > 0) {
          setFocusItems(data.map((item) => item.text));
        }
      } catch (error) {
        console.error('Failed to fetch footer focus:', error);
      }
    };

    const loadQuickLinks = async () => {
      try {
        const data = await fetchFooterQuickLinks();

        if (isMounted && Array.isArray(data) && data.length > 0) {
          setQuickLinks(data.map((link) => ({ label: link.label, path: link.path })));
        }
      } catch (error) {
        console.error('Failed to fetch footer quick links:', error);
      }
    };

    loadFocus();
    loadQuickLinks();

    return () => {
      isMounted = false;
    };
  }, []);

  const items = Array.isArray(focusItems) && focusItems.length > 0
    ? focusItems
    : DEFAULT_FOCUS;

  const links = Array.isArray(quickLinks) && quickLinks.length > 0
    ? quickLinks
    : DEFAULT_QUICK_LINKS;

  const mission = settings.mission || 'Creating Opportunities, Creating Lives. Dedicated to child healthcare, quality education, zero hunger, and rural empowerment across India.';
  const copyright = settings.copyright || 'Piplad Welfare Foundation';

  return (
    <footer style={{ background: '#0f172a', color: '#cbd5e1', paddingTop: '4rem', paddingBottom: '2rem' }}>
      <div className="container">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '3rem', marginBottom: '3rem' }}>
          
          {/* Col 1: Brand & Mission */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.25rem' }}>
              <img
                loading="lazy"
                decoding="async"
                src="/piplad-logo.png"
                alt="Piplad Welfare Foundation"
                style={{ width: '80px', height: '80px', borderRadius: '10px', objectFit: 'contain', flexShrink: 0 }}
              />
              <div>
                <div style={{ fontWeight: 800, fontSize: '1.1rem', color: '#ffffff' }}>PIPLAD WELFARE</div>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#34d399', letterSpacing: '0.08em' }}>FOUNDATION</div>
              </div>
            </div>
            <p style={{ fontSize: '0.9rem', color: '#94a3b8', lineHeight: 1.6, marginBottom: '1.5rem' }}>
              {mission}
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(16,185,129,0.1)', color: '#34d399', padding: '0.5rem 0.8rem', borderRadius: '6px', fontSize: '0.85rem', width: 'fit-content' }}>
              <ShieldCheck size={16} /> 80G Tax Deductible (Reg. NGO)
            </div>
            <h4 style={{ color: '#ffffff', fontSize: '1rem', fontWeight: 700, margin: '1.75rem 0 0.9rem 0' }}>Follow Us</h4>
            <SocialLinks />

            {/* Newsletter */}
            <div style={{ marginTop: '1.5rem' }}>
              <label htmlFor="newsletter-email" style={{ color: '#ffffff', fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', display: 'block' }}>
                Subscribe to our newsletter
              </label>
              <form onSubmit={handleNewsletterSubmit} style={{ display: 'flex', gap: '0.5rem', maxWidth: '300px' }}>
                <div style={{ position: 'absolute', left: '-9999px', top: '-9999px', height: 0, overflow: 'hidden' }} aria-hidden="true">
                  <label htmlFor="newsletter-website">Website</label>
                  <input
                    id="newsletter-website"
                    type="text"
                    name="website"
                    tabIndex={-1}
                    autoComplete="off"
                    value={newsletterWebsite}
                    onChange={(e) => setNewsletterWebsite(e.target.value)}
                  />
                </div>
                <input
                  id="newsletter-email"
                  type="email"
                  value={newsletterEmail}
                  onChange={(e) => setNewsletterEmail(e.target.value)}
                  placeholder="Your email address"
                  required
                  style={{
                    flex: 1,
                    minWidth: 0,
                    padding: '0.6rem 0.8rem',
                    borderRadius: '8px',
                    border: '1px solid #334155',
                    background: '#1e293b',
                    color: '#f1f5f9',
                    fontSize: '0.85rem'
                  }}
                />
                <button
                  type="submit"
                  aria-label="Subscribe to newsletter"
                  disabled={newsletterState === 'loading'}
                  style={{
                    background: '#10b981',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '0 0.9rem',
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    opacity: newsletterState === 'loading' ? 0.7 : 1
                  }}
                >
                  <Send size={16} />
                </button>
              </form>
              {newsletterState === 'success' && (
                <p style={{ color: '#34d399', fontSize: '0.8rem', margin: '0.5rem 0 0', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <ShieldCheck size={14} /> Subscribed! Welcome aboard.
                </p>
              )}
              {newsletterState === 'error' && (
                <p style={{ color: '#f87171', fontSize: '0.8rem', margin: '0.5rem 0 0' }}>
                  Please enter a valid email address.
                </p>
              )}
            </div>
          </div>

          {/* Col 2: Quick Links */}
          <div>
            <h4 style={{ color: '#ffffff', fontSize: '1.1rem', fontWeight: 700, marginBottom: '1.25rem' }}>Quick Links</h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.9rem' }}>
              {links.map((link, index) => {
                const external = /^https?:\/\//.test(link.path);

                return (
                  <li key={`${link.label}-${index}`}>
                    {external ? (
                      <a href={link.path} target="_blank" rel="noreferrer" style={{ color: '#cbd5e1', textDecoration: 'none' }}>
                        {link.label}
                      </a>
                    ) : (
                      <Link to={link.path} style={{ color: '#cbd5e1', textDecoration: 'none' }}>
                        {link.label}
                      </Link>
                    )}
                  </li>
                );
              })}
            </ul>
          </div>

          {/* Col 3: Causes */}
          <div>
            <h4 style={{ color: '#ffffff', fontSize: '1.1rem', fontWeight: 700, marginBottom: '1.25rem' }}>Our Core Focus</h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.9rem', color: '#94a3b8' }}>
              {items.map((item, index) => (
                <li key={index}>• {item}</li>
              ))}
            </ul>
          </div>

          {/* Col 4: Contact Info */}
          <div>
            <h4 style={{ color: '#ffffff', fontSize: '1.1rem', fontWeight: 700, marginBottom: '1.25rem' }}>Contact Info</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', fontSize: '0.9rem', color: '#94a3b8' }}>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                <MapPin size={18} color="#10b981" style={{ flexShrink: 0, marginTop: '3px' }} />
                <span>{settings.address}</span>
              </div>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <Phone size={18} color="#10b981" style={{ flexShrink: 0 }} />
                <span>{settings.phone}</span>
              </div>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <Mail size={18} color="#10b981" style={{ flexShrink: 0 }} />
                <span>{settings.email}</span>
              </div>
              <button className="btn btn-primary" onClick={onOpenDonate} style={{ marginTop: '0.5rem', width: 'fit-content' }}>
                <Heart size={16} fill="#ffffff" /> Make a Donation
              </button>
            </div>
          </div>

        </div>

        <div style={{ borderTop: '1px solid #1e293b', paddingTop: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', fontSize: '0.85rem', color: '#64748b' }}>
          <div>
            © {new Date().getFullYear()} {copyright} (PWF). All Rights Reserved.
          </div>
          <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
            <Link to="/terms" style={{ color: '#64748b' }}>Terms & Conditions</Link>
            <Link to="/terms" style={{ color: '#64748b' }}>Refund Policy</Link>
            <Link to="/contact" style={{ color: '#64748b' }}>Support</Link>
            <Link to="/admin" style={{ color: '#64748b' }}>Staff Login</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
