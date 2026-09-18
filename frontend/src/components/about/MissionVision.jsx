// src/components/about/MissionVision.jsx


import { missionVisionData } from "../../data/aboutdata";

const MissionVision = () => {
  const data = missionVisionData;

  return (
    <section
      className="about-mission-vision"
      id="mission-vision"
    >

      <div className="about-container">

        <div className="about-section-heading">
          <span className="about-eyebrow">
            {data.eyebrow}
          </span>
        </div>

        <div className="about-mission-grid">

          <article className="about-mission-card">

            <div className="about-card-icon">
              🎯
            </div>

            <span className="about-card-label">
              {data.mission.label}
            </span>

            <h2>{data.mission.title}</h2>

            <p>{data.mission.description}</p>

            <ul>
              {data.mission.points.map((point, index) => (
                <li key={index}>
                  <span>✓</span>
                  {point}
                </li>
              ))}
            </ul>

          </article>


          <article className="about-vision-card">

            <div className="about-card-icon">
              🌍
            </div>

            <span className="about-card-label">
              {data.vision.label}
            </span>

            <h2>{data.vision.title}</h2>

            <p>{data.vision.description}</p>

            <ul>
              {data.vision.points.map((point, index) => (
                <li key={index}>
                  <span>✓</span>
                  {point}
                </li>
              ))}
            </ul>

          </article>

        </div>

      </div>

    </section>
  );
};

export default MissionVision;