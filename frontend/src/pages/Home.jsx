import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Award,
  BookOpen,
  BriefcaseBusiness,
  CalendarDays,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  HeartPulse,
  Leaf,
  MapPin,
  ShieldCheck,
  Sprout,
  Trophy,
  Users,
  Utensils,
} from 'lucide-react';
import {
  cloudinaryUrl,
  fetchBlogPosts,
  fetchCauses,
  fetchCertificates,
  fetchHomeSlides,
  fetchPublicImpact,
  fetchUpcomingProjects,
  resolveMediaUrl,
} from '../api';
import CauseCard from '../components/CauseCard';
import { impactAreasData, whoWeAreData } from '../data/aboutdata';
import { partnerData } from '../data/partnerData';
import { defaultHeroSlides as heroSlides } from '../data/heroSlides';
import '../styles/home.css';

const programIcons = [
  BookOpen,
  BriefcaseBusiness,
  HeartPulse,
  Leaf,
  Sprout,
  Trophy,
  Users,
  ShieldCheck,
];

function SectionHeading({ eyebrow, title, description, light = false }) {
  return (
    <div className={`home-section-heading ${light ? 'is-light' : ''}`}>
      {eyebrow && <span className="home-eyebrow">{eyebrow}</span>}
      <h2>{title}</h2>
      {description && <p>{description}</p>}
    </div>
  );
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

function truncate(text, length = 150) {
  if (!text) return '';
  const clean = String(text).replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
  return clean.length > length ? `${clean.slice(0, length).trim()}…` : clean;
}

import usePageMeta from '../hooks/usePageMeta';

export default function Home({ onOpenDonate, onSelectCauseToDonate }) {
  usePageMeta();
  const [slide, setSlide] = useState(0);
  const [slides, setSlides] = useState([]);
  const [causes, setCauses] = useState([]);
  const [blogs, setBlogs] = useState([]);
  const [projects, setProjects] = useState([]);
  const [certificates, setCertificates] = useState([]);
  const [impact, setImpact] = useState(null);
  const [loading, setLoading] = useState({ slides: true, causes: true, blogs: true, projects: true, certificates: true, impact: true });

  const activeSlides = slides.length > 0 ? slides : heroSlides;

  useEffect(() => {
    const timer = window.setInterval(() => {
      setSlide((current) => (current + 1) % activeSlides.length);
    }, 6000);
    return () => window.clearInterval(timer);
  }, [activeSlides.length]);

  useEffect(() => {
    let mounted = true;

    const load = async (key, request, setter) => {
      try {
        const data = await request();
        if (mounted) setter(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error(`Failed to load homepage ${key}:`, error);
        if (mounted) setter([]);
      } finally {
        if (mounted) setLoading((state) => ({ ...state, [key]: false }));
      }
    };

    load('slides', fetchHomeSlides, (data) =>
      setSlides(data.map((slide) => ({
        ...slide,
        image: slide.image_url ? resolveMediaUrl(slide.image_url) : '',
      })))
    );
    load('causes', fetchCauses, setCauses);
    load('blogs', fetchBlogPosts, setBlogs);
    load('projects', fetchUpcomingProjects, setProjects);
    load('certificates', fetchCertificates, setCertificates);

    fetchPublicImpact()
      .then((result) => {
        if (mounted) setImpact(result);
      })
      .catch((error) => {
        console.error('Failed to load homepage impact:', error);
        if (mounted) setImpact(null);
      })
      .finally(() => {
        if (mounted) setLoading((state) => ({ ...state, impact: false }));
      });

    return () => {
      mounted = false;
    };
  }, []);

  const activeSlide = activeSlides[Math.min(slide, activeSlides.length - 1)];
  const featuredBlogs = useMemo(() => blogs.slice(0, 4), [blogs]);
  const featuredCertificates = useMemo(() => certificates.slice(0, 6), [certificates]);
  const featuredProjects = useMemo(() => projects.slice(0, 3), [projects]);
  const programs = impactAreasData.areas.slice(0, 8);

  const impactCards = useMemo(() => {
    if (!impact) return [];

    const people = impact.groups?.find((g) => g.key === 'people')?.metrics || [];
    const environmental = impact.groups?.find((g) => g.key === 'environmental')?.metrics || [];

    const cards = [];

    const studentMetric = people.find((m) => m.key === 'students_supported');
    if (studentMetric) {
      cards.push({ icon: <BookOpen size={22} />, value: `${Number(studentMetric.value).toLocaleString('en-IN')}+`, label: studentMetric.name });
    }

    const communityMetric = people.find((m) => m.key === 'community_reached');
    if (communityMetric) {
      cards.push({ icon: <Users size={22} />, value: `${Number(communityMetric.value).toLocaleString('en-IN')}+`, label: communityMetric.name });
    }

    const treeMetric = environmental.find((m) => m.key === 'trees_planted');
    if (treeMetric) {
      cards.push({ icon: <Leaf size={22} />, value: `${Number(treeMetric.value).toLocaleString('en-IN')}+`, label: treeMetric.name });
    }

    return cards;
  }, [impact]);

  return (
    <main className="home-page">
      {/* HERO */}
      <section className="home-hero">
        <div className="home-hero-media" style={{ backgroundImage: `url(${activeSlide.image})` }} />
        <div className="home-hero-overlay" />
        <div className="container home-hero-inner">
          <div className="home-hero-copy">
            <span className="home-hero-badge">
              <ShieldCheck size={16} /> Piplad Welfare Foundation
            </span>
            <span className="home-hero-eyebrow">{activeSlide.eyebrow}</span>
            <h1>
              {activeSlide.title} <span>{activeSlide.highlight}</span>
            </h1>
            <p>{activeSlide.text}</p>
            <div className="home-hero-actions">
              <button className="btn btn-primary home-hero-donate" onClick={() => onOpenDonate()}>
                <HeartPulse size={19} fill="currentColor" /> Donate Now
              </button>
              <Link to="/about" className="home-ghost-button">
                Discover Our Work <ArrowRight size={18} />
              </Link>
            </div>
          </div>
        </div>

        <div className="home-hero-controls container">
          <button type="button" aria-label="Previous slide" onClick={() => setSlide((slide - 1 + activeSlides.length) % activeSlides.length)}>
            <ChevronLeft size={20} />
          </button>
          <div className="home-hero-dots">
            {activeSlides.map((item, index) => (
              <button
                key={item.id ?? item.eyebrow}
                type="button"
                aria-label={`Go to slide ${index + 1}`}
                className={index === slide ? 'active' : ''}
                onClick={() => setSlide(index)}
              />
            ))}
          </div>
          <button type="button" aria-label="Next slide" onClick={() => setSlide((slide + 1) % activeSlides.length)}>
            <ChevronRight size={20} />
          </button>
        </div>
      </section>

      {/* IMPACT STRIP */}
      <section className="home-impact-strip">
        <div className="container home-impact-grid">
          <div><strong>8+</strong><span>Impact Areas</span></div>
          <div><strong>1M</strong><span>Tree Plantation Goal</span></div>
          <div><strong>Section 8</strong><span>Registered Nonprofit</span></div>
          <div><strong>12A & 80G</strong><span>Registered Foundation</span></div>
        </div>
      </section>

      {/* WHO WE ARE */}
      <section className="home-section home-who-we-are">
        <div className="container">
          <span className="home-who-chip">
            <MapPin size={16} /> Rural-first, community-led
          </span>

          <SectionHeading
            eyebrow={whoWeAreData.eyebrow}
            title={whoWeAreData.title}
            description={whoWeAreData.description}
          />
          <p className="home-secondary-copy">{whoWeAreData.secondaryDescription}</p>
          <div className="home-highlight-grid">
            {whoWeAreData.highlights.map((item) => (
              <div className="home-highlight-card" key={item.title}>
                <span>{item.icon}</span>
                <div>
                  <h3>{item.title}</h3>
                  <p>{item.description}</p>
                </div>
              </div>
            ))}
          </div>
          <Link to="/about" className="home-text-link">Learn more about Piplad <ArrowRight size={17} /></Link>
        </div>
      </section>

      {/* PATHSHALA */}
      <section className="home-section home-pathshala">
        <div className="container home-pathshala-grid">
          <div>
            <SectionHeading
              eyebrow="Piplad Pathshala"
              title="Learning should not stop because connectivity is limited."
              description="Piplad Pathshala is a rural-first digital learning platform designed for low-connectivity and bilingual access."
              light
            />
            <div className="home-check-list">
              {[
                'Live interactive classes and recorded lessons',
                'Bilingual learning and exam preparation',
                'Teacher training and data-driven learning paths',
                'Voice-first and offline-friendly distribution',
              ].map((item) => (
                <div key={item}><CheckCircle2 size={19} /> <span>{item}</span></div>
              ))}
            </div>
            <a className="home-light-link" href="https://exam.pipladfoundation.in" target="_blank" rel="noreferrer">
              Explore Piplad Pathshala <ArrowRight size={17} />
            </a>
          </div>
          <div className="home-pathshala-card">
            <BookOpen size={48} />
            <strong>Rural-first digital learning</strong>
            <span>Accessible · Bilingual · Voice-first · Community-focused</span>
          </div>
        </div>
      </section>

      {/* CORE PROGRAMS */}
      <section className="home-section home-programs">
        <div className="container">
          <SectionHeading
            eyebrow="Core Programs"
            title="Eight connected areas of community transformation"
            description="Our programs address interconnected challenges across education, livelihoods, health, environment, agriculture, sports, culture and disaster response."
          />
          <div className="home-program-grid">
            {programs.map((program, index) => {
              const Icon = programIcons[index] || ShieldCheck;
              return (
                <article className="home-program-card" key={program.title}>
                  <div className="home-program-icon"><Icon size={25} /></div>
                  <span className="home-program-number">{program.number}</span>
                  <h3>{program.title}</h3>
                  <p>{program.description}</p>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      {/* IMPACT AT A GLANCE */}
      <section className="home-section home-impact-at-glance">
        <div className="container">
          <SectionHeading
            eyebrow="Impact at a Glance"
            title="Creating measurable change across communities"
            description="Published, verified numbers from our programmes — updated automatically whenever they change."
          />

          {loading.impact ? (
            <div className="home-empty-state">Loading impact data…</div>
          ) : impactCards.length === 0 ? (
            <div className="home-empty-state">Impact figures will be published here as programmes grow.</div>
          ) : (
            <div className="home-at-glance-grid">
              {impactCards.map((card) => (
                <article className="home-at-glance-card" key={card.label}>
                  <div className="home-at-glance-icon">{card.icon}</div>
                  <div className="home-at-glance-value">{card.value}</div>
                  <div className="home-at-glance-label">{card.label}</div>
                </article>
              ))}
            </div>
          )}

          <div className="home-centered-link">
            <Link to="/impact" className="home-outline-button">View Full Impact Report <ArrowRight size={17} /></Link>
          </div>
        </div>
      </section>

      {/* PARTNERSHIPS */}
      <section className="home-section home-partnerships">
        <div className="container">
          <SectionHeading
            eyebrow="Strategic Partnerships"
            title="Technology and industry expertise, grounded in local trust"
            description="Our work scales through partnerships that bring technology, logistics, skills and employment pathways to rural communities."
          />
          <div className="home-partner-grid">
            {partnerData.map((partner) => (
              <Link
                className="home-partner-card"
                key={partner.slug}
                to={`/partners/${partner.slug}`}
              >
                <div className="home-partner-mark">
                  {partner.logo ? (
                    <img loading="lazy" decoding="async" src={partner.logo} alt={`${partner.name} logo`} />
                  ) : (
                    partner.short
                  )}
                </div>
                <div>
                  <h3>{partner.name}</h3>
                  <p>{partner.description}</p>
                </div>
                <ArrowRight className="home-partner-arrow" size={20} />
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* MISSION */}
      <section className="home-section home-mission">
        <div className="container home-mission-inner">
          <SectionHeading
            eyebrow="Our Mission"
            title="Inclusive rural transformation, built to last."
            description="Piplad Pathshala and Piplad Welfare Foundation catalyze inclusive rural transformation by democratizing access to education, healthcare, skills and sustainable livelihoods."
            light
          />
          <div className="home-mission-pillars">
            <span>Education</span><span>Healthcare</span><span>Skills</span><span>Livelihoods</span><span>Environment</span>
          </div>
          <p className="home-mission-tagline">Grassroots-powered. Technology-enabled. Future-focused.</p>
        </div>
      </section>

      {/* UPCOMING PROJECTS */}
      <section className="home-section home-projects">
        <div className="container">
          <div className="home-section-heading-row">
            <SectionHeading
              eyebrow="Upcoming Projects"
              title="What is coming next"
              description="New initiatives published by the Piplad team will appear here automatically."
            />
            <Link to="/gallery" className="home-outline-button">View Media <ArrowRight size={17} /></Link>
          </div>

          {loading.projects ? (
            <div className="home-empty-state">Loading upcoming projects…</div>
          ) : featuredProjects.length === 0 ? (
            <div className="home-empty-state">New upcoming projects will be announced here soon.</div>
          ) : (
            <div className="home-project-grid">
              {featuredProjects.map((project) => (
                <article className="home-project-card" key={project.id}>
                  {project.image_url ? (
                    <img loading="lazy" decoding="async" src={cloudinaryUrl(resolveMediaUrl(project.image_url), { width: 700 })} alt={project.title} />
                  ) : (
                    <div className="home-project-placeholder"><Sprout size={34} /></div>
                  )}
                  <div className="home-project-body">
                    <div className="home-project-meta"><CalendarDays size={15} /> {project.expected_date ? formatDate(project.expected_date) : 'Coming soon'}</div>
                    <h3>{project.title}</h3>
                    <p>{truncate(project.description, 130)}</p>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* BLOG HIGHLIGHTS */}
      <section className="home-section home-blog">
        <div className="container">
          <div className="home-section-heading-row">
            <SectionHeading
              eyebrow="Blogs"
              title="Stories, updates and ideas from Piplad"
              description="The latest posts from the admin-managed blog are highlighted on the homepage."
            />
            <Link to="/blog" className="home-outline-button">View All Blogs <ArrowRight size={17} /></Link>
          </div>

          {loading.blogs ? (
            <div className="home-empty-state">Loading latest stories…</div>
          ) : featuredBlogs.length === 0 ? (
            <div className="home-empty-state">New stories and updates will appear here soon.</div>
          ) : (
            <div className="home-blog-grid">
              {featuredBlogs.map((post) => (
                <article className="home-blog-card" key={post.id}>
                  <div className="home-blog-image-wrap">
                    {post.image_url ? (
                      <img loading="lazy" decoding="async" src={cloudinaryUrl(resolveMediaUrl(post.image_url), { width: 700 })} alt={post.title} />
                    ) : (
                      <div className="home-blog-placeholder"><BookOpen size={34} /></div>
                    )}
                    <span><BookOpen size={14} /> Blog</span>
                  </div>
                  <div className="home-blog-body">
                    {post.published_date && <div className="home-blog-date"><CalendarDays size={14} /> {formatDate(post.published_date)}</div>}
                    <h3>{post.title}</h3>
                    <p>{truncate(post.summary || post.content, 150)}</p>
                    <Link to={`/blog/${post.id}`}>Read story <ArrowRight size={16} /></Link>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* CERTIFICATIONS */}
      <section className="home-section home-certifications">
        <div className="container">
          <SectionHeading
            eyebrow="Our Certifications"
            title="Registered, accountable and ready to partner"
            description="Our certifications and registrations help donors, institutions and corporate partners support our work with confidence."
          />

          {loading.certificates ? (
            <div className="home-empty-state">Loading certifications…</div>
          ) : featuredCertificates.length === 0 ? (
            <div className="home-empty-state">Certification documents will be displayed here soon.</div>
          ) : (
            <div className="home-certificate-grid">
              {featuredCertificates.map((certificate) => (
                <article className="home-certificate-card" key={certificate.id}>
                  {certificate.image_url ? (
                    <img loading="lazy" decoding="async" src={cloudinaryUrl(resolveMediaUrl(certificate.image_url), { width: 700 })} alt={certificate.title} />
                  ) : (
                    <div className="home-certificate-placeholder"><Award size={38} /></div>
                  )}
                  <div>
                    <Award size={17} />
                    <h3>{certificate.title}</h3>
                    {certificate.description && <p>{truncate(certificate.description, 90)}</p>}
                  </div>
                </article>
              ))}
            </div>
          )}
          <div className="home-centered-link"><Link to="/certificates" className="home-outline-button">View All Certifications <ArrowRight size={17} /></Link></div>
        </div>
      </section>

      {/* CAUSES */}
      <section className="home-section home-causes">
        <div className="container">
          <div className="home-section-heading-row">
            <SectionHeading
              eyebrow="Support Our Work"
              title="Every contribution can become an opportunity"
              description="Support active community initiatives and help us continue creating meaningful, measurable impact."
            />
            <Link to="/causes" className="home-outline-button">View Causes <ArrowRight size={17} /></Link>
          </div>
          {loading.causes ? (
            <div className="home-empty-state">Loading active causes…</div>
          ) : causes.length === 0 ? (
            <div className="home-empty-state">New campaigns will appear here soon.</div>
          ) : (
            <div className="home-cause-grid">
              {causes.slice(0, 3).map((cause) => (
                <CauseCard key={cause.id} cause={cause} onDonate={(item) => onSelectCauseToDonate(item)} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* DONATE CTA */}
      <section className="home-donate-cta">
        <div className="container">
          <div>
            <span className="home-eyebrow">Be Part of the Change</span>
            <h2>Give someone the chance to build a better future.</h2>
            <p>Whether you support education, healthcare, livelihoods, environment or relief, your contribution helps turn potential into possibility.</p>
          </div>
          <button className="btn btn-primary" onClick={() => onOpenDonate()}><Utensils size={18} /> Donate Now</button>
        </div>
      </section>
    </main>
  );
}
