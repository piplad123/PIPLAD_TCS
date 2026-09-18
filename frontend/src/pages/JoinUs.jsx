import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Heart, Users, Handshake, TrendingUp, CheckCircle2, ArrowRight, Loader2, MessageCircle, Award, Zap } from 'lucide-react';
import '../styles/joinus.css';
import { submitVolunteerApplication } from '../api';

import usePageMeta from '../hooks/usePageMeta';

export default function JoinUs({ onOpenDonate }) {
  usePageMeta(
    'Join Us — Volunteer',
    'Volunteer with Piplad Welfare Foundation. Apply today and help create opportunities and lives.'
  );
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phone: '',
    interestArea: 'Education & Skill development',
    aboutYourself: '',
    profilePic: null,
    website: ''
  });
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);

  const waysToBecomeInvolved = [
    {
      icon: <Heart size={36} />,
      title: 'Volunteer Your Time',
      description: 'Lend your time, skills, and compassion on the ground. Whether you can teach, organize events, or help with digital outreach — your efforts matter.',
      color: '#d1fae5',
      textColor: '#059669',
      action: 'volunteer'
    },
    {
      icon: <TrendingUp size={36} />,
      title: 'Become a Donor',
      description: 'Support our ongoing programs through one-time or monthly donations. Your generosity fuels education, healthcare, empowerment, and hope.',
      color: '#fef3c7',
      textColor: '#d97706',
      action: 'donate'
    },
    {
      icon: <Handshake size={36} />,
      title: 'Partner With Us',
      description: 'We welcome collaborations with schools, corporates, NGOs, and local bodies to scale our impact and reach more people in need.',
      color: '#e0f2fe',
      textColor: '#0284c7',
      action: 'contact'
    }
  ];

  const interestAreas = [
    'Education & Skill development',
    'Healthcare',
    'Finance & Legal',
    'Environment & Modern Agriculture',
    'Social Welfare',
    'Culture & Tourism',
    'Sports & Yoga',
    'IT & Social Media'
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setFormData(prev => ({
        ...prev,
        profilePic: file
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await submitVolunteerApplication({
        full_name: formData.fullName,
        email: formData.email,
        phone: formData.phone,
        interest_area: formData.interestArea,
        about_yourself: formData.aboutYourself,
        profile_pic: formData.profilePic,
        website: formData.website,
      });
      setLoading(false);
      setSubmitted(true);

      // Reset form after 3 seconds
      setTimeout(() => {
        setSubmitted(false);
        setFormData({
          fullName: '',
          email: '',
          phone: '',
          interestArea: 'Education & Skill development',
          aboutYourself: '',
          profilePic: null,
          website: ''
        });
      }, 3000);
    } catch {
      setLoading(false);
      setError('Failed to submit. Please try again.');
    }
  };

  return (
    <div>
      {/* ===== HERO SECTION ===== */}
      <section className="joinus-hero">
        <div className="container">
          <div style={{ textAlign: 'center', color: '#ffffff' }}>
            <span className="badge badge-green" style={{ marginBottom: '1rem', display: 'inline-block' }}>
              <Zap size={16} /> Get Involved
            </span>
            <h1 className="heading-xl" style={{ color: '#ffffff', marginBottom: '1.5rem', fontSize: 'clamp(2.2rem, 5vw, 3.8rem)' }}>
              Every Hand Counts. <span style={{ color: '#34d399' }}>Every Voice Matters.</span>
            </h1>
            <p className="subheading" style={{ color: '#94a3b8', maxWidth: '700px', margin: '0 auto', fontSize: '1.15rem' }}>
              At Piplad, we believe that change begins with ordinary people doing extraordinary things. If you're someone who believes in creating a better world — one step, one life, one act of kindness at a time — we invite you to join our journey.
            </p>
            <p style={{ color: '#a7f3d0', marginTop: '2rem', fontWeight: 600 }}>Join us to create real impact, empower communities, and walk the path of meaningful change.</p>
          </div>
        </div>
      </section>

      {/* ===== WAYS TO GET INVOLVED ===== */}
      <section className="section-padding" style={{ background: '#f8fafc' }}>
        <div className="container">
          <div style={{ textAlign: 'center', maxWidth: '700px', margin: '0 auto 3.5rem auto' }}>
            <span className="badge badge-amber" style={{ marginBottom: '0.75rem', display: 'inline-block' }}>
              Multiple Pathways
            </span>
            <h2 className="heading-lg" style={{ marginBottom: '1rem' }}>Ways You Can Get Involved</h2>
            <p className="subheading" style={{ margin: '0 auto' }}>
              Choose the way that works best for you and start making a difference today.
            </p>
          </div>

          <div className="joinus-ways-grid">
            {waysToBecomeInvolved.map((way, idx) => (
              <div key={idx} className="joinus-card">
                <div 
                  className="joinus-card-icon"
                  style={{ background: way.color, color: way.textColor }}
                >
                  {way.icon}
                </div>
                <h3 className="heading-md" style={{ marginBottom: '0.75rem', color: '#0f172a' }}>
                  {way.title}
                </h3>
                <p style={{ fontSize: '0.95rem', color: '#475569', lineHeight: 1.6 }}>
                  {way.description}
                </p>
                <div style={{ marginTop: '1.5rem', color: '#059669', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {way.action === 'donate' ? (
                    <button
                      type="button"
                      onClick={onOpenDonate}
                      className="joinus-learnmore"
                      style={{
                        background: 'none',
                        border: 'none',
                        padding: 0,
                        color: '#059669',
                        fontWeight: 600,
                        fontSize: '1rem',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                      }}
                    >
                      Learn more <ArrowRight size={18} />
                    </button>
                  ) : way.action === 'volunteer' ? (
                    <a
                      href="#volunteer-form"
                      onClick={(e) => {
                        e.preventDefault();
                        document
                          .getElementById('volunteer-form')
                          ?.scrollIntoView({ behavior: 'smooth' });
                      }}
                      style={{
                        textDecoration: 'none',
                        color: '#059669',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                      }}
                    >
                      Learn more <ArrowRight size={18} />
                    </a>
                  ) : (
                    <Link
                      to="/contact"
                      style={{
                        textDecoration: 'none',
                        color: '#059669',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                      }}
                    >
                      Learn more <ArrowRight size={18} />
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== BECOME A MEMBER / VOLUNTEER FORM ===== */}
      <section
        id="volunteer-form"
        className="section-padding"
        style={{ background: '#ffffff' }}
      >
        <div className="container">
          <div style={{ maxWidth: '750px', margin: '0 auto' }}>
            <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
              <span className="badge badge-green" style={{ marginBottom: '0.75rem', display: 'inline-block' }}>
                Join Our Team
              </span>
              <h2 className="heading-lg" style={{ marginBottom: '0.75rem' }}>Become a Volunteer Member</h2>
              <p className="subheading" style={{ margin: '0 auto' }}>
                Fill out our volunteer application form and become part of a movement creating real, tangible change.
              </p>
            </div>

            {submitted ? (
              <div className="joinus-success-message" style={{ 
                background: '#d1fae5', 
                border: '2px solid #059669',
                borderRadius: '12px',
                padding: '2rem',
                textAlign: 'center'
              }}>
                <CheckCircle2 size={48} color="#059669" style={{ margin: '0 auto 1rem auto' }} />
                <h3 style={{ color: '#065f46', fontWeight: 700, marginBottom: '0.5rem' }}>
                  Application Submitted Successfully!
                </h3>
                <p style={{ color: '#047857' }}>
                  Thank you for your interest in joining Piplad. Our team will review your application and contact you soon.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="joinus-form">
                <div style={{ position: 'absolute', left: '-9999px', top: '-9999px', height: 0, overflow: 'hidden' }} aria-hidden="true">
                  <label htmlFor="volunteer-website">Website</label>
                  <input
                    id="volunteer-website"
                    type="text"
                    name="website"
                    tabIndex={-1}
                    autoComplete="off"
                    value={formData.website}
                    onChange={(e) => setFormData(prev => ({ ...prev, website: e.target.value }))}
                  />
                </div>
                {error && (
                  <div style={{
                    background: '#fee2e2',
                    color: '#991b1b',
                    padding: '1rem',
                    borderRadius: '8px',
                    marginBottom: '1.5rem',
                    fontSize: '0.95rem'
                  }}>
                    {error}
                  </div>
                )}

                <div className="form-row">
                  <div className="form-group">
                    <label style={{ fontWeight: 600, color: '#0f172a', marginBottom: '0.5rem', display: 'block' }}>
                      Full Name <span style={{ color: '#ef4444' }}>*</span>
                    </label>
                    <input
                      type="text"
                      name="fullName"
                      value={formData.fullName}
                      onChange={handleInputChange}
                      placeholder="Your Full Name"
                      required
                      className="form-input"
                    />
                  </div>
                  <div className="form-group">
                    <label style={{ fontWeight: 600, color: '#0f172a', marginBottom: '0.5rem', display: 'block' }}>
                      Email Address <span style={{ color: '#ef4444' }}>*</span>
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder="your@email.com"
                      required
                      className="form-input"
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label style={{ fontWeight: 600, color: '#0f172a', marginBottom: '0.5rem', display: 'block' }}>
                      Mobile Number <span style={{ color: '#ef4444' }}>*</span>
                    </label>
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleInputChange}
                      placeholder="+91-XXXXXXXXXX"
                      required
                      className="form-input"
                    />
                  </div>
                  <div className="form-group">
                    <label style={{ fontWeight: 600, color: '#0f172a', marginBottom: '0.5rem', display: 'block' }}>
                      Area of Interest <span style={{ color: '#ef4444' }}>*</span>
                    </label>
                    <select
                      name="interestArea"
                      value={formData.interestArea}
                      onChange={handleInputChange}
                      className="form-input"
                    >
                      {interestAreas.map(area => (
                        <option key={area} value={area}>{area}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label style={{ fontWeight: 600, color: '#0f172a', marginBottom: '0.5rem', display: 'block' }}>
                    Tell Us About Yourself
                  </label>
                  <textarea
                    name="aboutYourself"
                    value={formData.aboutYourself}
                    onChange={handleInputChange}
                    placeholder="Share your background, skills, interests, and what motivates you to join Piplad..."
                    rows="5"
                    className="form-input"
                  />
                  <p style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.25rem' }}>
                    Help us understand your passion and how you'd like to contribute.
                  </p>
                </div>

                <div className="form-group">
                  <label style={{ fontWeight: 600, color: '#0f172a', marginBottom: '0.5rem', display: 'block' }}>
                    Profile Picture <span style={{ color: '#ef4444' }}>*</span>
                  </label>
                  <input
                    type="file"
                    onChange={handleFileChange}
                    accept="image/jpeg,image/png,image/webp,image/gif"
                    required
                    className="form-input"
                    style={{ padding: '0.75rem' }}
                  />
                  <p style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.25rem' }}>
                    Required: Add a profile picture. This will be displayed on your volunteer card.
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="btn btn-primary"
                  style={{
                    width: '100%',
                    padding: '1rem',
                    fontSize: '1.05rem',
                    borderRadius: '8px',
                    fontWeight: 600,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.75rem',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    opacity: loading ? 0.7 : 1
                  }}
                >
                  {loading ? (
                    <>
                      <Loader2 size={20} className="spinning" /> Submitting...
                    </>
                  ) : (
                    <>
                      Submit Application <Heart size={20} />
                    </>
                  )}
                </button>

                <p style={{ fontSize: '0.85rem', color: '#64748b', textAlign: 'center', marginTop: '1rem' }}>
                  By submitting this form, you agree to our volunteer terms and will be contacted by our team.
                </p>
              </form>
            )}
          </div>
        </div>
      </section>

      {/* ===== WHY VOLUNTEER WITH US ===== */}
      <section className="section-padding" style={{ background: '#f8fafc' }}>
        <div className="container">
          <div style={{ textAlign: 'center', maxWidth: '700px', margin: '0 auto 3.5rem auto' }}>
            <span className="badge badge-amber" style={{ marginBottom: '0.75rem', display: 'inline-block' }}>
              Volunteer Benefits
            </span>
            <h2 className="heading-lg">Why Volunteer With Piplad?</h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '2rem' }}>
            <div className="card" style={{ padding: '2rem', borderLeft: '4px solid #059669' }}>
              <Award size={32} color="#059669" style={{ marginBottom: '1rem' }} />
              <h3 className="heading-md" style={{ marginBottom: '0.75rem', color: '#0f172a' }}>
                Certificates & Recognition
              </h3>
              <p style={{ fontSize: '0.95rem', color: '#475569', lineHeight: 1.6 }}>
                Receive volunteer certificates, letter of appreciation, and recognition on our platform for your contributions.
              </p>
            </div>

            <div className="card" style={{ padding: '2rem', borderLeft: '4px solid #d97706' }}>
              <Users size={32} color="#d97706" style={{ marginBottom: '1rem' }} />
              <h3 className="heading-md" style={{ marginBottom: '0.75rem', color: '#0f172a' }}>
                Community & Network
              </h3>
              <p style={{ fontSize: '0.95rem', color: '#475569', lineHeight: 1.6 }}>
                Be part of a passionate community of 500+ volunteers making real impact together.
              </p>
            </div>

            <div className="card" style={{ padding: '2rem', borderLeft: '4px solid #0284c7' }}>
              <MessageCircle size={32} color="#0284c7" style={{ marginBottom: '1rem' }} />
              <h3 className="heading-md" style={{ marginBottom: '0.75rem', color: '#0f172a' }}>
                Skill Development
              </h3>
              <p style={{ fontSize: '0.95rem', color: '#475569', lineHeight: 1.6 }}>
                Gain hands-on experience, learn new skills, and build your professional portfolio.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ===== CTA SECTION ===== */}
      <section className="joinus-cta">
        <div className="container" style={{ textAlign: 'center', color: '#ffffff' }}>
          <h2 className="heading-lg" style={{ color: '#ffffff', marginBottom: '1.5rem' }}>
            Ready to Make a Difference?
          </h2>
          <p style={{ fontSize: '1.1rem', color: '#94a3b8', marginBottom: '2rem', maxWidth: '600px', margin: '0 auto 2rem auto' }}>
            Whether you have 1 hour or 10 hours a week, your time and skills are invaluable to us. Let's create positive change together.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <a href="#" className="btn btn-primary" style={{ borderRadius: '8px', padding: '0.9rem 2rem' }}>
              Volunteer Now <Heart size={18} />
            </a>
            <a href="/contact" className="btn btn-outline" style={{ borderRadius: '8px', padding: '0.9rem 2rem', borderColor: '#ffffff', color: '#ffffff' }}>
              Contact Us <ArrowRight size={18} />
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
