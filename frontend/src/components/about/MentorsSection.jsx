// src/components/about/MentorsSection.jsx

import { useState } from "react";
import { mentorsData } from "../../data/aboutdata";
import { resolveMediaUrl } from "../../api";

const MentorsSection = ({ data = null }) => {
  const fallback = mentorsData;

  const mentors = Array.isArray(data)
    ? data
    : fallback.mentors;

  const [activeMentor, setActiveMentor] = useState(0);

  const safeIndex = Math.min(
    activeMentor,
    Math.max(0, mentors.length - 1)
  );

  const mentor = mentors[safeIndex];

  const mentorImage = data
    ? mentor.image_url
      ? resolveMediaUrl(mentor.image_url)
      : fallback.mentors[safeIndex]?.image || '/piplad-logo.jpg'
    : fallback.mentors[safeIndex]?.image || '/piplad-logo.jpg';

  const fallbackMentor =
    fallback.mentors[safeIndex] || {};

  return (
    <section
      id="mentors"
      className="about-mentors"
      style={{ scrollMarginTop: "100px" }}
    >

      <div className="about-container">

        <div className="about-section-heading about-centered">

          <span className="about-eyebrow">
            {fallback.eyebrow}
          </span>

          <h2>{fallback.title}</h2>

          <p>{fallback.description}</p>

        </div>


        <div className="about-mentor-selector">

          {mentors.map((item, index) => (
            <button
              type="button"
              className={`about-mentor-tab ${
                safeIndex === index
                  ? "active"
                  : ""
              }`}
              onClick={() => setActiveMentor(index)}
              key={item.id ?? index}
            >
              {item.name}
            </button>
          ))}

        </div>


        {mentor && (
          <div className="about-mentor-card">

            <div className="about-mentor-image">

              <img
                loading="lazy"
                decoding="async"
                src={mentorImage}
                alt={mentor.name}
              />

            </div>


            <div className="about-mentor-content">

              <span className="about-card-label">
                Mentor
              </span>

              <h3>{mentor.name}</h3>

              <h4>{mentor.role || fallbackMentor.role}</h4>

              <p>{mentor.description || fallbackMentor.description}</p>

              <blockquote>
                "{mentor.quote || fallbackMentor.quote}"
              </blockquote>

            </div>

          </div>
        )}

      </div>

    </section>
  );
};

export default MentorsSection;