// src/components/about/ImpactAreas.jsx

import { useState } from "react";
import { impactAreasData } from "../../data/aboutdata";

const ImpactAreas = () => {
  const data = impactAreasData;

  const [activeArea, setActiveArea] = useState(0);

  const active = data.areas[activeArea];

  return (
    <section className="about-impact">

      <div className="about-container">

        <div className="about-section-heading">

          <span className="about-eyebrow">
            {data.eyebrow}
          </span>

          <h2>{data.title}</h2>

          <p>{data.description}</p>

        </div>


        <div className="about-impact-layout">

          <div className="about-impact-list">

            {data.areas.map((area, index) => (
              <button
                type="button"
                className={`about-impact-tab ${
                  activeArea === index
                    ? "active"
                    : ""
                }`}
                onClick={() => setActiveArea(index)}
                key={index}
              >

                <span className="about-impact-number">
                  {area.number}
                </span>

                <span className="about-impact-icon">
                  {area.icon}
                </span>

                <span className="about-impact-title">
                  {area.shortTitle}
                </span>

                <span className="about-impact-arrow">
                  →
                </span>

              </button>
            ))}

          </div>


          <div className="about-impact-detail">

            <span className="about-impact-detail-icon">
              {active.icon}
            </span>

            <span className="about-card-label">
              {active.number}
            </span>

            <h3>{active.title}</h3>

            <p>{active.description}</p>

            <div className="about-impact-features">

              {active.features.map((feature, index) => (
                <span key={index}>
                  ✓ {feature}
                </span>
              ))}

            </div>

          </div>

        </div>

      </div>

    </section>
  );
};

export default ImpactAreas;