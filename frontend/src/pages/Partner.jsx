import { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, BriefcaseBusiness, CheckCircle2, HeartHandshake, Users, Camera, Building2, GraduationCap, HeartPulse, HandCoins, TrendingUp } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { partnerData } from '../data/partnerData';
import { fetchGalleryItems, resolveMediaUrl } from '../api';

function groupPartnerAlbums(items) {
  const albums = new Map();

  items.forEach((item) => {
    const key = [item.title, item.description || ''].join('|');

    if (!albums.has(key)) {
      albums.set(key, {
        id: key,
        title: item.title,
        description: item.description,
        photos: [],
      });
    }

    albums.get(key).photos.push(item);
  });

  return Array.from(albums.values());
}

import usePageMeta from '../hooks/usePageMeta';

export default function Partner() {
  usePageMeta(
    'Partners',
    'Meet the corporate partners and supporters of Piplad Welfare Foundation.'
  );
  const { partnerSlug } = useParams();
  const partner = partnerData.find((item) => item.slug === partnerSlug);
  const [partnerPhotos, setPartnerPhotos] = useState([]);

  useEffect(() => {
    if (!partner) return;

    fetchGalleryItems()
      .then((items) => setPartnerPhotos(
        items.filter((item) => item.category === partner.galleryCategory)
      ))
      .catch(() => setPartnerPhotos([]));
  }, [partner]);

  const partnerAlbums = useMemo(
    () => groupPartnerAlbums(partnerPhotos),
    [partnerPhotos]
  );

  if (!partner) {
    return (
      <section className="section-padding">
        <div className="container" style={{ maxWidth: 760 }}>
          <h1>Partnership not found</h1>
          <Link to="/" className="btn">
            <ArrowLeft size={16} /> Back to Home
          </Link>
        </div>
      </section>
    );
  }

  return (
    <div>
      <section style={{ background: '#0f172a', color: '#fff', padding: '5rem 0 4rem' }}>
        <div className="container" style={{ maxWidth: 920 }}>
          <Link to="/" className="home-partner-back-link">
            <ArrowLeft size={16} /> Back to Home
          </Link>
          <div className="home-partner-detail-mark">
            {partner.logo ? (
              <img
                loading="lazy"
                decoding="async"
                src={partner.logo}
                alt={`${partner.name} logo`}
              />
            ) : (
              partner.short
            )}
          </div>
          <span className="home-eyebrow" style={{ color: '#bef264' }}>Strategic Partnership</span>
          <h1 style={{ color: '#fff', maxWidth: 720 }}>{partner.name}</h1>
          <p style={{ color: '#cbd5e1', maxWidth: 680, fontSize: '1.1rem', lineHeight: 1.7 }}>
            {partner.description}
          </p>
        </div>
      </section>

      <section className="section-padding" style={{ background: '#f8fafc' }}>
        <div className="container" style={{ maxWidth: 920 }}>
          <div className="partner-detail-grid">
            <article className="card partner-detail-card">
              <BriefcaseBusiness size={28} color="#65a30d" />
              <h2>Partnership focus</h2>
              <p>{partner.focus}</p>
            </article>
            <article className="card partner-detail-card">
              <CheckCircle2 size={28} color="#65a30d" />
              <h2>How it helps communities</h2>
              <p>{partner.details}</p>
            </article>
          </div>
          <Link to="/gallery#projects" className="home-outline-button" style={{ display: 'inline-flex', marginTop: '2rem' }}>
            Explore our work
          </Link>
        </div>
      </section>

      {partner.slug === 'tata-consultancy-services' && (
        <section className="section-padding" style={{ background: '#fff' }}>
          <div className="container" style={{ maxWidth: 920 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
              <Building2 size={24} color="#059669" />
              <span className="home-eyebrow" style={{ color: '#65a30d', margin: 0 }}>About Our Partner</span>
            </div>
            <h2 style={{ margin: '0 0 1.25rem' }}>Who is Tata Consultancy Services</h2>
            <div className="partner-logo-row">
              <div className="partner-logo-box">
                <img
                  loading="lazy"
                  decoding="async"
                  src="/logos/tcs-logo.png"
                  alt="Tata Consultancy Services logo"
                  className="partner-logo-img"
                  onError={(e) => { e.currentTarget.style.display = 'none'; }}
                />
                <span className="partner-logo-fallback">{partner.short}</span>
              </div>
            </div>
            <p style={{ color: '#475569', lineHeight: 1.8, margin: '0 0 2rem' }}>
              Tata Consultancy Services (TCS) is one of the world's largest information technology services and
              consulting companies, part of the Tata Group — a global enterprise known for its long-standing
              commitment to nation-building and community welfare. Guided by the Tata philosophy of giving back
              to society, TCS brings not only advanced technology but also a people-first approach to everything
              it does.
            </p>

            <div className="partner-info-grid">
              <article className="card partner-detail-card">
                <GraduationCap size={26} color="#65a30d" />
                <h2>How They Help People</h2>
                <p>
                  Through the HOPE Initiative, TCS supports digital education for rural students, telemedicine
                  and healthcare services for underserved families, and data-driven analytics that help us
                  measure and improve our impact. Their employees also volunteer their time and skills, working
                  directly alongside communities to make learning and better health accessible to those who need
                  it most.
                </p>
              </article>
              <article className="card partner-detail-card">
                <HeartPulse size={26} color="#65a30d" />
                <h2>Impact That Reaches People</h2>
                <p>
                  The partnership has brought useful technology, learning resources and connected services to
                  rural villages where these were once out of reach. Teachers and students now access digital
                  tools, families receive health guidance through telemedicine, and our teams make smarter
                  decisions with the help of TCS's analytics expertise.
                </p>
              </article>
              <article className="card partner-detail-card">
                <HandCoins size={26} color="#65a30d" />
                <h2>Our Community Commitment</h2>
                <p>
                  TCS believes technology is a force for good. Their support is not a one-time contribution —
                  it reflects a continuing commitment to walk alongside rural communities, enabling lasting
                  opportunity and empowering people to build better futures for themselves.
                </p>
              </article>
              <article className="card partner-detail-card">
                <TrendingUp size={26} color="#65a30d" />
                <h2>What the Future Holds</h2>
                <p>
                  Looking ahead, TCS will continue to support Piplad Welfare Foundation by expanding digital
                  education, strengthening community healthcare and deepening volunteer engagement. Together,
                  we remain focused on a shared goal: helping people today while building sustainable pathways
                  for a brighter tomorrow.
                </p>
              </article>
            </div>
          </div>
        </section>
      )}

      {partner.slug === 'transport-corporation-of-india' && (
        <section className="section-padding" style={{ background: '#fff' }}>
          <div className="container" style={{ maxWidth: 920 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
              <Building2 size={24} color="#059669" />
              <span className="home-eyebrow" style={{ color: '#65a30d', margin: 0 }}>About Our Partner</span>
            </div>
            <h2 style={{ margin: '0 0 1.25rem' }}>Who is Transport Corporation of India</h2>
            <div className="partner-logo-row">
              <div className="partner-logo-box">
                <img
                  loading="lazy"
                  decoding="async"
                  src="/logos/tci-logo.jpeg"
                  alt="Transport Corporation of India logo"
                  className="partner-logo-img"
                  onError={(e) => { e.currentTarget.style.display = 'none'; }}
                />
                <span className="partner-logo-fallback">{partner.short}</span>
              </div>
            </div>
            <p style={{ color: '#475569', lineHeight: 1.8, margin: '0 0 2rem' }}>
              Transport Corporation of India (TCI) is one of the country's largest integrated logistics and
              supply-chain companies, with a legacy of moving goods and connecting communities across India for
              over seven decades. Beyond its business of freight, supply chain and warehousing, TCI believes in
              building skills and creating dignified livelihood opportunities — especially for rural learners
              who are eager to enter the fast-growing logistics and supply-chain sector.
            </p>

            <div className="partner-info-grid">
              <article className="card partner-detail-card">
                <GraduationCap size={26} color="#65a30d" />
                <h2>How They Help People</h2>
                <p>
                  TCI brings industry-aligned vocational training, hands-on apprenticeships and structured
                  skilling programs to rural learners. Through our partnership, young people gain practical
                  exposure to warehousing, freight documentation, safety standards, transport operations and
                  the digital tools that power modern supply chains — giving them job-ready skills that
                  employers actually look for.
                </p>
              </article>
              <article className="card partner-detail-card">
                <HeartPulse size={26} color="#65a30d" />
                <h2>Impact That Reaches People</h2>
                <p>
                  Trainees move from classrooms directly into placement pathways with logistics companies and
                  nearby industries. Young people from villages who once had few local employment options now
                  enter formal careers with structured growth, safe working conditions and steady income,
                  while entire families benefit from a whole new industry opening up to them.
                </p>
              </article>
              <article className="card partner-detail-card">
                <HandCoins size={26} color="#65a30d" />
                <h2>Our Community Commitment</h2>
                <p>
                  TCI's support reflects a conviction that business growth and community well-being can go hand
                  in hand. Their skills-first approach roots development in local aspiration, pairing training
                  with real employment — so opportunity is created close to home and shared across the
                  community rather than concentrated far away.
                </p>
              </article>
              <article className="card partner-detail-card">
                <TrendingUp size={26} color="#65a30d" />
                <h2>What the Future Holds</h2>
                <p>
                  As logistics and e-commerce expand rapidly across India, the demand for trained, trustworthy
                  professionals keeps growing. Together, we aim to widen the skilling pathways, support more
                  learners each year, and strengthen the route from classroom to career — building stable,
                  dignified futures for the people we both serve.
                </p>
              </article>
            </div>
          </div>
        </section>
      )}

      <section className="section-padding" style={{ background: '#fff' }}>
        <div className="container" style={{ maxWidth: 920 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
            <Camera size={24} color="#059669" />
            <h2 style={{ margin: 0 }}>Partner Event Albums</h2>
          </div>
          {partnerAlbums.length === 0 ? (
            <p style={{ color: '#64748b', lineHeight: 1.7 }}>
              Partner event albums will be added here soon.
            </p>
          ) : (
            <div className="partner-photo-grid">
              {partnerAlbums.map((album) => (
                <article className="partner-photo-card" key={album.id}>
                  <div className="partner-photo-img">
                    <img loading="lazy" decoding="async" src={resolveMediaUrl(album.photos[0].image_url)} alt={album.title} />
                  </div>
                  <figcaption>
                    <h3>{album.title}</h3>
                    {album.description && <p>{album.description}</p>}
                    <p>{album.photos.length} {album.photos.length === 1 ? 'photo' : 'photos'}</p>
                  </figcaption>
                </article>
              ))}
            </div>
          )}
        </div>
      </section>

      {partner.slug === 'tata-consultancy-services' && (
        <>
          <section className="section-padding partner-appreciation" style={{ background: '#0f172a', color: '#fff' }}>
            <div className="container" style={{ maxWidth: 920 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
                <HeartHandshake size={24} color="#a3e635" />
                <span className="home-eyebrow" style={{ color: '#bef264', margin: 0 }}>With Gratitude</span>
              </div>
              <h2 style={{ color: '#fff', margin: '0 0 1.25rem' }}>Built with Care &amp; Dedication</h2>

              <div className="card partner-appreciation-card">
                <p style={{ margin: 0, lineHeight: 1.8, color: '#334155' }}>
                  We extend our sincere appreciation to the dedicated developers behind this partnership page. Their
                  thoughtful work ensures that our story reaches every visitor with clarity and warmth, and their
                  hands-on support at our events has been invaluable to the community we serve.
                </p>
                <div className="partner-developers">
                  <div className="partner-developer">
                    <div className="partner-developer-avatar"><Users size={20} /></div>
                    <div>
                      <a href="https://www.linkedin.com/in/adil-rahaman-molla-166298201/" target="_blank" rel="noreferrer"><strong>Adil</strong></a>
                      <span>Developer</span>
                    </div>
                  </div>
                  <div className="partner-developer">
                    <div className="partner-developer-avatar"><Users size={20} /></div>
                    <div>
                      <a href="https://www.linkedin.com/in/rishu-singh-b8a252238/" target="_blank" rel="noreferrer"><strong>Rishu</strong></a>
                      <span>Developer</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

        </>
      )}
    </div>
  );
}
