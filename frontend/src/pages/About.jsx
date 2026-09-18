import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { fetchFounder, fetchMentors } from '../api';

import AboutHero from '../components/about/AboutHero';
import WhoWeAre from '../components/about/WhoWeAre';
import MissionVision from '../components/about/MissionVision';
import OurApproach from '../components/about/OurApproach';
import ImpactAreas from '../components/about/ImpactAreas';
import StrategicPriorities from '../components/about/StrategicPriorities';
import ValuesSection from '../components/about/ValuesSection';
import FounderStory from '../components/about/FounderStory';
import MentorsSection from '../components/about/MentorsSection';
import AboutCTA from '../components/about/AboutCTA';

import '../styles/about.css';

import usePageMeta from '../hooks/usePageMeta';

export default function About() {
  usePageMeta(
    'About Us',
    'Learn about Piplad Welfare Foundation — our mission, vision, founder story, and impact across healthcare, education, zero hunger, and women empowerment.'
  );
  const location = useLocation();

  const [aboutData, setAboutData] = useState(null);

  /*
   * Load founder profile and mentors for the About page.
   *
   * The components still use their bundled static content as a fallback,
   * so a failure here never produces a blank page.
   */
  useEffect(() => {
    let isMounted = true;

    const loadAboutData = async () => {
      try {
        const [founderData, mentorsData] = await Promise.all([
          fetchFounder(),
          fetchMentors(),
        ]);

        if (isMounted) {
          setAboutData({ founder: founderData, mentors: mentorsData });
        }
      } catch (error) {
        console.error('Failed to fetch about data:', error);

        if (isMounted) {
          setAboutData(null);
        }
      }
    };

    loadAboutData();

    return () => {
      isMounted = false;
    };
  }, []);

  /*
   * Handle hash navigation
   *
   * Examples:
   *
   * /about#founders
   * /about#mentors
   *
   * React Router changes the URL, but it does not
   * always automatically scroll to the hash target.
   */
  useEffect(() => {
    if (!location.hash) {
      return;
    }

    const hash = location.hash.replace('#', '');

    const scrollToSection = () => {
      const element = document.getElementById(hash);

      if (element) {
        element.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    };

    /*
     * Wait until the About page sections have rendered
     * before trying to find the target element.
     */
    const timeoutId = setTimeout(scrollToSection, 100);

    return () => {
      clearTimeout(timeoutId);
    };
  }, [location.hash]);

  return (
    <main className="about-page">

      {/* =========================================
          1. ABOUT HERO
      ========================================== */}
      <AboutHero />

      {/* =========================================
          2. WHO WE ARE
      ========================================== */}
      <WhoWeAre />

      {/* =========================================
          3. MISSION & VISION
      ========================================== */}
      <MissionVision />

      {/* =========================================
          4. OUR APPROACH
      ========================================== */}
      <OurApproach />

      {/* =========================================
          5. IMPACT AREAS
      ========================================== */}
      <ImpactAreas />

      {/* =========================================
          6. STRATEGIC PRIORITIES
      ========================================== */}
      <StrategicPriorities />

      {/* =========================================
          7. OUR VALUES
      ========================================== */}
      <ValuesSection />

      {/* =========================================
          8. FOUNDER'S STORY
      ========================================== */}
      <FounderStory
        data={aboutData?.founder || null}
      />

      {/* =========================================
          9. MENTORS / TEAM
      ========================================== */}
      <MentorsSection
        data={aboutData?.mentors || null}
      />

      {/* =========================================
          10. FINAL CTA
      ========================================== */}
      <AboutCTA />

    </main>
  );
}