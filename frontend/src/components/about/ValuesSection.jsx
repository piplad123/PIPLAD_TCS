// src/components/about/ValuesSection.jsx


import { valuesData } from "../../data/aboutdata";

const ValuesSection = () => {
  const data = valuesData;

  return (
    <section className="about-values">

      <div className="about-container">

        <div className="about-section-heading about-centered">

          <span className="about-eyebrow">
            {data.eyebrow}
          </span>

          <h2>{data.title}</h2>

          <p>{data.description}</p>

        </div>


        <div className="about-values-grid">

          {data.values.map((value, index) => (
            <article
              className="about-value-card"
              key={index}
            >

              <div className="about-value-icon">
                {value.icon}
              </div>

              <div className="about-value-number">
                {String(index + 1).padStart(2, "0")}
              </div>

              <h3>{value.title}</h3>

              <p>{value.description}</p>

            </article>
          ))}

        </div>

      </div>

    </section>
  );
};

export default ValuesSection;