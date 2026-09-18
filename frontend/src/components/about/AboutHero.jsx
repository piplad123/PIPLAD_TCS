// src/components/about/AboutHero.jsx


import { aboutHeroData } from "../../data/aboutdata";

const AboutHero = () => {
  const data = aboutHeroData;

  return (
    <section className="about-hero">
      <div className="about-container about-hero-container">

        <div className="about-hero-content">

          <span className="about-eyebrow">
            {data.eyebrow}
          </span>

          <h1>
            {data.title}
            <span>{data.highlightedTitle}</span>
          </h1>

          <p>
            {data.description}
          </p>

          <div className="about-hero-actions">
            <a href="#mission-vision" className="about-btn about-btn-primary">
              {data.primaryButton}
            </a>

            <a href="#about-cta" className="about-btn about-btn-outline">
              {data.secondaryButton}
            </a>
          </div>

          <div className="about-hero-stats">
            {data.stats.map((stat, index) => (
              <div className="about-hero-stat" key={index}>
                <strong>{stat.value}</strong>
                <span>{stat.label}</span>
              </div>
            ))}
          </div>

        </div>

        <div className="about-hero-visual">
          <div className="about-hero-circle about-hero-circle-one" />
          <div className="about-hero-circle about-hero-circle-two" />

          <div className="about-hero-message">
            <span>🌱</span>
            <strong>Grassroots Powered</strong>
            <small>Technology Enabled</small>
          </div>
        </div>

      </div>
    </section>
  );
};

export default AboutHero;