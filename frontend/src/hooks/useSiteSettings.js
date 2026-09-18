import { useEffect, useState } from 'react';
import { fetchSiteSettings } from '../api';

const DEFAULT_SITE_SETTINGS = {
  phone: '+91-8981266033',
  email: 'info@pipladfoundation.in',
  address: 'Vill-Manikpur, Shahkhund-813108, Bhagalpur, Bihar',
  map_query: 'Manik Pur Buzurg, माणिक पुर बुज़ुर्ग, Bihar',
  mission:
    'Piplad Welfare Foundation works with rural communities to bridge the gaps in education, health, livelihoods, water, environment and technology, building a future where every villager can unlock their true potential.',
  copyright: 'Piplad Welfare Foundation',
};

export function useSiteSettings() {
  const [settings, setSettings] = useState(DEFAULT_SITE_SETTINGS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    fetchSiteSettings()
      .then((data) => {
        if (mounted && data && typeof data === 'object') {
          setSettings({ ...DEFAULT_SITE_SETTINGS, ...data });
        }
      })
      .catch(() => {
        // Keep the default values so the site still works offline.
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  return { settings, loading };
}

export function telHref(phone) {
  return `tel:${String(phone || '').replace(/[^+\d]/g, '')}`;
}