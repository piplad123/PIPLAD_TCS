// src/components/about/WhoWeAre.jsx


import { whoWeAreData } from "../../data/aboutdata";

const WhoWeAre = () => {
  const data = whoWeAreData;

  return (
    <section className="about-who-we-are">

      <div className="about-container about-two-column">

        <div className="about-who-content">

          <span className="about-eyebrow">
            {data.eyebrow}
          </span>

          <h2>{data.title}</h2>

          <p className="about-lead">
            {data.description}
          </p>

          <p>
            {data.secondaryDescription}
          </p>

          <div className="about-highlight-grid">
            {data.highlights.map((item, index) => (
              <article
                className="about-highlight-card"
                key={index}
              >
                <div className="about-icon-box">
                  {item.icon}
                </div>

                <div>
                  <h3>{item.title}</h3>
                  <p>{item.description}</p>
                </div>
              </article>
            ))}
          </div>

        </div>

        <div className="about-who-visual">

          <div className="about-who-card-main">
            <span className="about-who-big-icon">
              🌱
            </span>

            <span>Community</span>
            <strong>First</strong>

            <p>
              Local leadership + technology + sustainable impact
            </p>
          </div>

          <div className="about-floating-card">
            <strong>Rural India</strong>
            <span>One community at a time</span>
          </div>

        </div>

      </div>

    </section>
  );
};

export default WhoWeAre;