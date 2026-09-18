import { useEffect } from 'react';

const BASE_URL = 'https://pipladfoundation.in';

const DEFAULT_TITLE = 'Piplad Welfare Foundation | Creating Opportunities, Creating Lives';
const DEFAULT_DESCRIPTION =
  'Piplad Welfare Foundation (PWF) is dedicated to child healthcare, quality education for all, zero hunger food drives, and women empowerment. 80G Tax Exemption available.';

function setMeta(attr, key, content) {
  let el = document.head.querySelector(`meta[${attr}="${key}"]`);
  if (!el) {
    el = document.createElement('meta');
    el.setAttribute(attr, key);
    document.head.appendChild(el);
  }
  el.setAttribute('content', content);
}

function removeMeta(attr, key) {
  document.head.querySelectorAll(`meta[${attr}="${key}"]`).forEach((el) => el.remove());
}

export default function usePageMeta(title = DEFAULT_TITLE, description = DEFAULT_DESCRIPTION, image = '/piplad-logo.png') {
  useEffect(() => {
    const fullTitle = title === DEFAULT_TITLE ? title : `${title} | Piplad Welfare Foundation`;
    const canonicalUrl = `${BASE_URL}${window.location.pathname}`;

    document.title = fullTitle;
    setMeta('name', 'description', description);

    setMeta('property', 'og:title', fullTitle);
    setMeta('property', 'og:description', description);
    setMeta('property', 'og:type', 'website');
    setMeta('property', 'og:url', canonicalUrl);
    setMeta('property', 'og:image', /^https?:/.test(image) ? image : `${BASE_URL}${image}`);
    setMeta('property', 'og:site_name', 'Piplad Welfare Foundation');

    setMeta('name', 'twitter:card', 'summary_large_image');
    setMeta('name', 'twitter:title', fullTitle);
    setMeta('name', 'twitter:description', description);

    let canonical = document.head.querySelector('link[rel="canonical"]');
    if (!canonical) {
      canonical = document.createElement('link');
      canonical.setAttribute('rel', 'canonical');
      document.head.appendChild(canonical);
    }
    canonical.setAttribute('href', canonicalUrl);

    return () => {
      removeMeta('property', 'og:title');
      removeMeta('property', 'og:description');
      removeMeta('property', 'og:url');
      removeMeta('property', 'og:image');
      removeMeta('name', 'twitter:title');
      removeMeta('name', 'twitter:description');
    };
  }, [title, description, image]);
}