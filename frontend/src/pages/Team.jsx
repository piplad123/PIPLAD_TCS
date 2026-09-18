import { useEffect, useMemo, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  ChevronLeft,
  ChevronRight,
  Users,
} from 'lucide-react';

import {
  fetchTeam,
  resolveMediaUrl,
} from '../api';


const TEAM_ORDER = [
  'Education & Skill Development',
  'Healthcare',
  'Finance & Legal',
  'Environment & Modern Agriculture',
  'Social Welfare',
  'Culture & Tourism',
  'Sports & Yoga',
  'IT & Social Media',
  'General',
];


const FALLBACK_LOGO = '/piplad-logo.jpg';


function TeamMemberCard({ member }) {
  const photo = member.photo_url
    ? resolveMediaUrl(member.photo_url)
    : FALLBACK_LOGO;

  return (
    <article className="team-member-card">

      <div className="team-member-photo-wrapper">

        <img
          loading="lazy"
          decoding="async"
          src={photo}
          alt={member.name}
          className="team-member-photo"
          onError={(event) => {
            if (
              event.currentTarget.src
              !== window.location.origin + FALLBACK_LOGO
            ) {
              event.currentTarget.src = FALLBACK_LOGO;
            }
          }}
        />

        <div className="team-member-overlay">
          <Users size={20} />
        </div>

      </div>

      <div className="team-member-info">

        <h3>
          {member.name}
        </h3>

        {member.role && (
          <p className="team-member-role">
            {member.role}
          </p>
        )}

        {member.bio && (
          <p className="team-member-bio">
            {member.bio}
          </p>
        )}

      </div>

    </article>
  );
}


function TeamCarousel({ members }) {
  const trackRef = useRef(null);

  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  function updateButtons() {
    const element = trackRef.current;

    if (!element) {
      return;
    }

    setCanScrollLeft(
      element.scrollLeft > 5
    );

    setCanScrollRight(
      element.scrollLeft
      + element.clientWidth
      < element.scrollWidth - 5
    );
  }


  useEffect(() => {
    updateButtons();

    const element = trackRef.current;

    if (!element) {
      return undefined;
    }

    element.addEventListener(
      'scroll',
      updateButtons,
      { passive: true }
    );

    window.addEventListener(
      'resize',
      updateButtons
    );

    return () => {
      element.removeEventListener(
        'scroll',
        updateButtons
      );

      window.removeEventListener(
        'resize',
        updateButtons
      );
    };
  }, [members]);


  function scroll(direction) {
    const element = trackRef.current;

    if (!element) {
      return;
    }

    const amount =
      Math.max(
        element.clientWidth * 0.78,
        280
      );

    element.scrollBy({
      left:
        direction === 'left'
          ? -amount
          : amount,
      behavior: 'smooth',
    });
  }


  return (
    <div className="team-carousel">

      <button
        type="button"
        className="team-carousel-button team-carousel-button-left"
        onClick={() => scroll('left')}
        disabled={!canScrollLeft}
        aria-label="Previous team members"
      >
        <ChevronLeft size={24} />
      </button>


      <div
        ref={trackRef}
        className="team-carousel-track"
      >
        {members.map((member) => (
          <div
            className="team-carousel-item"
            key={member.id}
          >
            <TeamMemberCard
              member={member}
            />
          </div>
        ))}
      </div>


      <button
        type="button"
        className="team-carousel-button team-carousel-button-right"
        onClick={() => scroll('right')}
        disabled={!canScrollRight}
        aria-label="Next team members"
      >
        <ChevronRight size={24} />
      </button>

    </div>
  );
}


function normalizeTeamName(value) {
  return String(value || '')
    .trim()
    .toLowerCase()
    .replace(/&/g, 'and')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}


import usePageMeta from '../hooks/usePageMeta';

export default function Team() {
  usePageMeta(
    'Our Team',
    'Meet the team and mentors behind Piplad Welfare Foundation and its community programs.'
  );
  const { teamName } = useParams();
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');


  useEffect(() => {

    async function loadTeam() {

      try {

        setLoading(true);
        setError('');

        const data = await fetchTeam();

        const allMembers = Array.isArray(data) ? data : [];

        if (!teamName) {
          setMembers(allMembers);
          return;
        }

        const requestedTeam = normalizeTeamName(
          decodeURIComponent(teamName)
        );

        const filteredMembers = allMembers.filter((member) => {
          return normalizeTeamName(member.team || 'General') === requestedTeam;
        });

        setMembers(filteredMembers);

      } catch (err) {

        console.error(
          'Failed to load team:',
          err
        );

        setError(
          'Unable to load team members right now.'
        );

      } finally {

        setLoading(false);

      }
    }

    loadTeam();

  }, [teamName]);


  const groupedTeams = useMemo(() => {

    const groups = new Map();

    members.forEach((member) => {

      const team =
        member.team?.trim()
        || 'General';

      if (!groups.has(team)) {
        groups.set(team, []);
      }

      groups.get(team).push(member);

    });


    const ordered = [];

    TEAM_ORDER.forEach((teamName) => {

      if (groups.has(teamName)) {

        ordered.push({
          name: teamName,
          members: groups.get(teamName),
        });

        groups.delete(teamName);
      }

    });


    // Any custom team created by the admin
    // will still appear.
    groups.forEach((teamMembers, teamName) => {

      ordered.push({
        name: teamName,
        members: teamMembers,
      });

    });


    return ordered;

  }, [members]);


  return (
    <div className="team-page">

      {/* ================================================== */}
      {/* HERO */}
      {/* ================================================== */}

      <section className="team-hero">

        <div className="container">

          <span className="badge badge-green team-hero-badge">
            Our Team
          </span>

          <h1 className="heading-xl team-hero-title">
            Meet the People Behind PWF
          </h1>

          <p className="team-hero-description">
            Dedicated people working together to create
            opportunities, strengthen communities and
            create lasting impact.
          </p>

        </div>

      </section>


      {/* ================================================== */}
      {/* TEAM CONTENT */}
      {/* ================================================== */}

      <section className="team-content">

        <div className="container">

          {loading && (
            <div className="team-state">
              <div className="team-spinner" />
              <p>Loading our team...</p>
            </div>
          )}


          {!loading && error && (
            <div className="team-state team-state-error">
              <p>{error}</p>
            </div>
          )}


          {!loading
            && !error
            && groupedTeams.length === 0 && (
              <div className="team-empty">

                <Users size={42} />

                <h2>
                  Our team is growing
                </h2>

                <p>
                  Team members will appear here
                  once they are added by the administrator.
                </p>

              </div>
            )}


          {!loading
            && !error
            && groupedTeams.map((group) => (

              <section
                key={group.name}
                className="team-section"
              >

                <div className="team-section-header">

                  <div>
                    <span className="team-section-kicker">
                      Our People
                    </span>

                    <h2>
                      {group.name}
                    </h2>
                  </div>

                  <span className="team-member-count">
                    {group.members.length}
                    {' '}
                    {group.members.length === 1
                      ? 'Member'
                      : 'Members'}
                  </span>

                </div>


                <TeamCarousel
                  members={group.members}
                />

              </section>

            ))}

        </div>

      </section>


      {/* ================================================== */}
      {/* PAGE STYLES */}
      {/* ================================================== */}

      <style>{`

        .team-page {
          background: #f8fafc;
          min-height: 100vh;
        }


        /* ================================================ */
        /* HERO */
        /* ================================================ */

        .team-hero {
          position: relative;
          overflow: hidden;
          background:
            radial-gradient(
              circle at 85% 20%,
              rgba(132, 204, 22, 0.25),
              transparent 30%
            ),
            linear-gradient(
              135deg,
              #052e16 0%,
              #064e3b 50%,
              #0f172a 100%
            );
          color: #ffffff;
          padding: 5.5rem 0 5rem;
        }


        .team-hero::before {
          content: '';
          position: absolute;
          width: 420px;
          height: 420px;
          border-radius: 50%;
          border: 1px solid rgba(255,255,255,0.08);
          right: -160px;
          top: -180px;
        }


        .team-hero::after {
          content: '';
          position: absolute;
          width: 260px;
          height: 260px;
          border-radius: 50%;
          border: 1px solid rgba(255,255,255,0.06);
          left: -130px;
          bottom: -160px;
        }


        .team-hero .container {
          position: relative;
          z-index: 2;
          text-align: center;
        }


        .team-hero-badge {
          margin-bottom: 1rem;
          background: rgba(217, 249, 157, 0.16);
          color: #d9f99d;
          border: 1px solid rgba(217, 249, 157, 0.25);
        }


        .team-hero-title {
          color: #ffffff;
          margin-bottom: 1rem;
        }


        .team-hero-description {
          max-width: 680px;
          margin: 0 auto;
          color: #cbd5e1;
          font-size: 1.05rem;
          line-height: 1.8;
        }


        /* ================================================ */
        /* CONTENT */
        /* ================================================ */

        .team-content {
          padding: 5rem 0;
        }


        .team-section {
          margin-bottom: 5rem;
        }


        .team-section:last-child {
          margin-bottom: 0;
        }


        .team-section-header {
          display: flex;
          align-items: flex-end;
          justify-content: space-between;
          gap: 1rem;
          margin-bottom: 2rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid #e2e8f0;
        }


        .team-section-kicker {
          display: block;
          margin-bottom: 0.4rem;
          color: #65a30d;
          text-transform: uppercase;
          letter-spacing: 0.12em;
          font-size: 0.72rem;
          font-weight: 800;
        }


        .team-section-header h2 {
          margin: 0;
          color: #0f172a;
          font-size: clamp(1.6rem, 2.5vw, 2.25rem);
          line-height: 1.2;
        }


        .team-member-count {
          flex-shrink: 0;
          padding: 0.45rem 0.8rem;
          border-radius: 999px;
          background: #ecfccb;
          color: #3f6212;
          font-size: 0.78rem;
          font-weight: 700;
        }


        /* ================================================ */
        /* CAROUSEL */
        /* ================================================ */

        .team-carousel {
          position: relative;
        }


        .team-carousel-track {
          display: flex;
          gap: 1.25rem;
          overflow-x: auto;
          scroll-snap-type: x mandatory;
          scroll-behavior: smooth;
          padding: 0.5rem 0.25rem 1.5rem;
          scrollbar-width: none;
          -webkit-overflow-scrolling: touch;
          cursor: grab;
        }


        .team-carousel-track:active {
          cursor: grabbing;
        }


        .team-carousel-track::-webkit-scrollbar {
          display: none;
        }


        .team-carousel-item {
          flex: 0 0 calc(
            25% - 0.95rem
          );
          min-width: 245px;
          scroll-snap-align: start;
        }


        /* ================================================ */
        /* MEMBER CARD */
        /* ================================================ */

        .team-member-card {
          height: 100%;
          overflow: hidden;
          border-radius: 22px;
          background: #ffffff;
          border: 1px solid #e2e8f0;
          box-shadow:
            0 8px 25px rgba(15, 23, 42, 0.06);
          transition:
            transform 0.35s ease,
            box-shadow 0.35s ease,
            border-color 0.35s ease;
        }


        .team-member-card:hover {
          transform: translateY(-10px);
          border-color: rgba(101, 163, 13, 0.35);
          box-shadow:
            0 22px 45px rgba(15, 23, 42, 0.13);
        }


        .team-member-photo-wrapper {
          position: relative;
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 250px;
          padding: 1.5rem;
          overflow: hidden;
          background:
            radial-gradient(
              circle at center,
              #f7fee7 0%,
              #ecfccb 45%,
              #f8fafc 100%
            );
        }


        .team-member-photo {
          width: 190px;
          height: 190px;
          border-radius: 50%;
          object-fit: cover;
          border: 5px solid #ffffff;
          box-shadow:
            0 8px 25px rgba(15, 23, 42, 0.15);
          transition:
            transform 0.45s ease,
            box-shadow 0.45s ease;
        }


        .team-member-card:hover
        .team-member-photo {
          transform: scale(1.07);
          box-shadow:
            0 15px 35px rgba(15, 23, 42, 0.2);
        }


        .team-member-overlay {
          position: absolute;
          right: 1.25rem;
          bottom: 1.25rem;
          display: flex;
          align-items: center;
          justify-content: center;
          width: 42px;
          height: 42px;
          border-radius: 50%;
          background: #65a30d;
          color: #ffffff;
          opacity: 0;
          transform: translateY(8px);
          transition:
            opacity 0.3s ease,
            transform 0.3s ease;
          box-shadow:
            0 8px 18px rgba(101, 163, 13, 0.35);
        }


        .team-member-card:hover
        .team-member-overlay {
          opacity: 1;
          transform: translateY(0);
        }


        .team-member-info {
          padding: 1.35rem 1.4rem 1.5rem;
          text-align: center;
        }


        .team-member-info h3 {
          margin: 0;
          color: #0f172a;
          font-size: 1.08rem;
          font-weight: 800;
          line-height: 1.35;
          transition: color 0.25s ease;
        }


        .team-member-card:hover
        .team-member-info h3 {
          color: #65a30d;
        }


        .team-member-role {
          margin: 0.45rem 0 0;
          color: #64748b;
          font-size: 0.86rem;
          font-weight: 600;
        }


        .team-member-bio {
          margin: 0.8rem 0 0;
          color: #64748b;
          font-size: 0.82rem;
          line-height: 1.6;
        }


        /* ================================================ */
        /* CAROUSEL BUTTONS */
        /* ================================================ */

        .team-carousel-button {
          position: absolute;
          top: 50%;
          z-index: 5;
          display: flex;
          align-items: center;
          justify-content: center;
          width: 46px;
          height: 46px;
          padding: 0;
          border: 1px solid #e2e8f0;
          border-radius: 50%;
          background: rgba(255,255,255,0.96);
          color: #0f172a;
          box-shadow:
            0 8px 22px rgba(15, 23, 42, 0.12);
          cursor: pointer;
          transform: translateY(-50%);
          transition:
            transform 0.2s ease,
            background 0.2s ease,
            color 0.2s ease,
            opacity 0.2s ease;
        }


        .team-carousel-button:hover:not(:disabled) {
          background: #65a30d;
          color: #ffffff;
          transform:
            translateY(-50%)
            scale(1.08);
        }


        .team-carousel-button:disabled {
          opacity: 0.25;
          cursor: default;
        }


        .team-carousel-button-left {
          left: -22px;
        }


        .team-carousel-button-right {
          right: -22px;
        }


        /* ================================================ */
        /* STATES */
        /* ================================================ */

        .team-state {
          min-height: 300px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 1rem;
          color: #64748b;
        }


        .team-state-error {
          color: #991b1b;
        }


        .team-spinner {
          width: 42px;
          height: 42px;
          border: 4px solid #dcfce7;
          border-top-color: #65a30d;
          border-radius: 50%;
          animation:
            team-spin 0.8s linear infinite;
        }


        @keyframes team-spin {
          to {
            transform: rotate(360deg);
          }
        }


        .team-empty {
          text-align: center;
          max-width: 500px;
          margin: 3rem auto;
          padding: 4rem 2rem;
          border-radius: 24px;
          background: #ffffff;
          border: 1px solid #e2e8f0;
          color: #64748b;
        }


        .team-empty svg {
          color: #65a30d;
          margin-bottom: 1rem;
        }


        .team-empty h2 {
          margin-bottom: 0.5rem;
          color: #0f172a;
        }


        /* ================================================ */
        /* RESPONSIVE */
        /* ================================================ */

        @media (max-width: 1100px) {

          .team-carousel-item {
            flex-basis: calc(
              33.333% - 0.85rem
            );
          }

        }


        @media (max-width: 800px) {

          .team-hero {
            padding: 4.5rem 0 4rem;
          }


          .team-content {
            padding: 3.5rem 0;
          }


          .team-carousel-item {
            flex-basis: 285px;
            min-width: 285px;
          }


          .team-carousel-button-left {
            left: 5px;
          }


          .team-carousel-button-right {
            right: 5px;
          }


          .team-carousel-track {
            padding-left: 3rem;
            padding-right: 3rem;
          }

        }


        @media (max-width: 560px) {

          .team-hero-title {
            font-size: 2.2rem;
          }


          .team-hero-description {
            font-size: 0.92rem;
          }


          .team-section-header {
            align-items: flex-start;
            flex-direction: column;
          }


          .team-section {
            margin-bottom: 3.5rem;
          }


          .team-carousel-item {
            flex-basis: 82vw;
            min-width: 82vw;
          }


          .team-member-photo-wrapper {
            min-height: 230px;
          }


          .team-member-photo {
            width: 175px;
            height: 175px;
          }


          .team-carousel-button {
            width: 40px;
            height: 40px;
          }

        }

      `}</style>

    </div>
  );
}