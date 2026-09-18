// src/components/about/FounderStory.jsx


import { founderStoryData } from "../../data/aboutdata";
import { resolveMediaUrl } from "../../api";

const FounderStory = ({ data = null }) => {
  const fallback = founderStoryData;
  const profile = data || fallback;

  const image = data?.image_url ? resolveMediaUrl(data.image_url) : fallback.image;

  const milestones = Array.isArray(profile.milestones)
    ? profile.milestones
    : fallback.milestones;

  return (
    <section
      id="founders"
      className="about-founder"
      style={{ scrollMarginTop: "100px" }}
    >

      <div className="about-container">

        <div className="about-founder-grid">

          <div className="about-founder-image">

            <div className="about-founder-image-frame">

              <img
                loading="lazy"
                decoding="async"
                src={image}
                alt={profile.image_alt || profile.imageAlt || fallback.imageAlt}
              />

            </div>

            <div className="about-founder-badge">

              <strong>{profile.name || fallback.name}</strong>

              <span>{profile.role || fallback.role}</span>

            </div>

          </div>


          <div className="about-founder-content">

            <span className="about-eyebrow">
              {profile.eyebrow || fallback.eyebrow}
            </span>

            <h2>{profile.title || fallback.title}</h2>

            <p className="about-lead">
              {profile.introduction || fallback.introduction}
            </p>

            <p>{profile.story || fallback.story}</p>

            <div className="about-founder-vision">

              <span>Our Vision</span>

              <p>{profile.vision || fallback.vision}</p>

            </div>

            <blockquote>
              "{profile.quote || fallback.quote}"
            </blockquote>

          </div>

        </div>


        <div className="about-founder-milestones">

          {milestones.map((item, index) => (
            <article
              className="about-founder-milestone"
              key={item.id ?? index}
            >

              <span>{item.year}</span>

              <h3>{item.title}</h3>

              <p>{item.description}</p>

            </article>
          ))}

        </div>

      </div>

    </section>
  );
};

export default FounderStory;