// src/components/about/AboutCTA.jsx


import { Link } from "react-router-dom";
import { aboutCTAData } from "../../data/aboutdata";

const AboutCTA = () => {
  const data = aboutCTAData;

  return (
    <section
      className="about-cta"
      id="about-cta"
    >

      <div className="about-container">

        <div className="about-cta-inner">

          <div className="about-cta-decoration">
            🌱
          </div>

          <span className="about-eyebrow">
            {data.eyebrow}
          </span>

          <h2>{data.title}</h2>

          <p>{data.description}</p>

          <div className="about-cta-actions">

            <Link
              to="/join"
              className="about-btn about-btn-primary"
            >
              {data.primaryButton}
            </Link>

            <Link
              to="/donate"
              className="about-btn about-btn-light"
            >
              {data.secondaryButton}
            </Link>

          </div>

          <span className="about-cta-closing">
            {data.closingText}
          </span>

        </div>

      </div>

    </section>
  );
};

export default AboutCTA;