// src/components/about/StrategicPriorities.jsx


import { strategicPrioritiesData } from "../../data/aboutdata";

const StrategicPriorities = () => {
  const data = strategicPrioritiesData;

  return (
    <section className="about-strategic">

      <div className="about-container">

        <div className="about-section-heading about-centered">

          <span className="about-eyebrow">
            {data.eyebrow}
          </span>

          <h2>{data.title}</h2>

          <p>{data.description}</p>

        </div>


        <div className="about-priority-grid">

          {data.priorities.map((priority, index) => (
            <article
              className="about-priority-card"
              key={index}
            >

              <div className="about-priority-header">

                <span className="about-priority-number">
                  {priority.number}
                </span>

                <span className="about-priority-icon">
                  {priority.icon}
                </span>

              </div>

              <h3>{priority.title}</h3>

              <p>{priority.description}</p>

            </article>
          ))}

        </div>

      </div>

    </section>
  );
};

export default StrategicPriorities;