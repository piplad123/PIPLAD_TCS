// src/components/about/OurApproach.jsx


import { ourApproachData } from "../../data/aboutdata";

const OurApproach = () => {
  const data = ourApproachData;

  return (
    <section className="about-approach">

      <div className="about-container">

        <div className="about-section-heading about-centered">

          <span className="about-eyebrow">
            {data.eyebrow}
          </span>

          <h2>{data.title}</h2>

          <p>{data.description}</p>

        </div>

        <div className="about-approach-grid">

          {data.steps.map((step, index) => (
            <article
              className="about-approach-card"
              key={index}
            >

              <div className="about-approach-top">

                <span className="about-step-number">
                  {step.number}
                </span>

                <span className="about-step-icon">
                  {step.icon}
                </span>

              </div>

              <h3>{step.title}</h3>

              <p>{step.description}</p>

              {index !== data.steps.length - 1 && (
                <span className="about-step-arrow">
                  →
                </span>
              )}

            </article>
          ))}

        </div>

      </div>

    </section>
  );
};

export default OurApproach;