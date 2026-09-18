import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Phone,
  Mail,
  Menu,
  X,
  ChevronDown,
} from 'lucide-react';
import { useSiteSettings, telHref } from '../hooks/useSiteSettings';

export default function Header({ onOpenDonate }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [openGroup, setOpenGroup] = useState(null);
  const [openDropdown, setOpenDropdown] = useState(null);
  const location = useLocation();
  const { settings } = useSiteSettings();

  const navItems = [
    {
      label: 'Home',
      path: '/',
    },
    {
      label: 'About Us',
      path: '/about',
      subItems: [
        { label: 'Introduction', path: '/about' },
        { label: 'Founders', path: '/about#founders' },
        { label: 'Mentors', path: '/about#mentors' },
      ],
    },
    {
      label: 'Our Team',
      path: '/team',
      subItems: [
        {
          label: 'Education & Skill development',
          path: '/team/education-and-skill-development',
        },
        {
          label: 'Healthcare',
          path: '/team/healthcare',
        },
        {
          label: 'Finance & Legal',
          path: '/team/finance-and-legal',
        },
        {
          label: 'Environment & Modern Agriculture',
          path: '/team/environment-and-modern-agriculture',
        },
        {
          label: 'Social Welfare',
          path: '/team/social-welfare',
        },
        {
          label: 'Culture & Tourism',
          path: '/team/culture-and-tourism',
        },
        {
          label: 'Sports & Yoga',
          path: '/team/sports-and-yoga',
        },
        {
          label: 'IT & Social Media',
          path: '/team/it-and-social-media',
        },
      ],
    },
    {
      label: 'Media & Awards',
      path: '/gallery',
      subItems: [
        { label: 'Photo Gallery', path: '/gallery#photos' },
        { label: 'Video Gallery', path: '/gallery#videos' },
        { label: 'Upcoming Projects', path: '/gallery#projects' },
      ],
    },
    {
      label: 'Join Us',
      path: '/join',
      subItems: [
        { label: 'Join Us', path: '/join' },
        { label: 'Contact Us', path: '/contact' },
      ],
    },
    {
      label: 'Our Impact',
      path: '/impact',
    },
    {
      label: 'Blog',
      path: '/blog',
    },
  ];

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }

    return location.pathname === path;
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
    setOpenGroup(null);
  };

  // Lock page scroll while the mobile drawer is open and allow Escape to close.
  useEffect(() => {
    document.body.classList.toggle('mobile-menu-open', mobileMenuOpen);

    if (!mobileMenuOpen) {
      return () => document.body.classList.remove('mobile-menu-open');
    }

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        setMobileMenuOpen(false);
        setOpenGroup(null);
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.classList.remove('mobile-menu-open');
    };
  }, [mobileMenuOpen]);

  const closeNavigation = () => {
    setOpenDropdown(null);
    closeMobileMenu();
  };

  return (
    <header className="header-wrapper">
      {/* ============================================================
          TOP CONTACT BAR
      ============================================================ */}
      <div className="header-topbar">
        <div className="container header-topbar-inner">
          <div className="header-topbar-spacer" />

          <div className="header-contact-info">
            <a
              href={telHref(settings.phone)}
              className="header-contact-item"
            >
              <Phone size={14} />
              <span>{settings.phone}</span>
            </a>

            <a
              href={`mailto:${settings.email}`}
              className="header-contact-item"
            >
              <Mail size={14} />
              <span>{settings.email}</span>
            </a>
          </div>
        </div>
      </div>

      {/* ============================================================
          MAIN NAVIGATION
      ============================================================ */}
      <div className="header-main">
        <div className="container header-main-inner">
          {/* BRAND */}
          <Link
            to="/"
            className="site-brand"
            aria-label="Piplad Welfare Foundation Home"
            onClick={closeMobileMenu}
          >
            <img
              src="/piplad-logo.png"
              alt="Piplad Welfare Foundation"
              className="site-brand-logo"
            />
          </Link>

          {/* DESKTOP NAVIGATION */}
          <nav className="desktop-nav" aria-label="Main navigation">
            {navItems.map((item) => (
              <div
                key={item.path}
                className={`nav-item-group ${
                  openDropdown === item.label
                    ? 'nav-item-group-open'
                    : ''
                }`}
              >
                {item.subItems ? (
                  <>
                    <button
                      type="button"
                      className={`nav-link nav-dropdown-trigger ${
                        isActive(item.path)
                          ? 'active-nav-link'
                          : ''
                      }`}
                      onClick={() => setOpenDropdown((current) =>
                        current === item.label ? null : item.label
                      )}
                    >
                      <span>{item.label}</span>
                      <ChevronDown size={15} />
                    </button>

                    <div className="dropdown-menu">
                      {item.subItems.map((subItem) => (
                        <Link
                          key={subItem.path}
                          to={subItem.path}
                          className="dropdown-item"
                          onClick={closeNavigation}
                        >
                          {subItem.label}
                        </Link>
                      ))}
                    </div>
                  </>
                ) : (
                  <Link
                    to={item.path}
                    className={`nav-link ${
                      isActive(item.path)
                        ? 'active-nav-link'
                        : ''
                    }`}
                    onClick={closeNavigation}
                  >
                    {item.label}
                  </Link>
                )}
              </div>
            ))}

            <button
              type="button"
              className="header-donate-button"
              onClick={onOpenDonate}
            >
              Donate
            </button>
          </nav>

          {/* MOBILE MENU BUTTON */}
          <button
            type="button"
            className="mobile-menu-btn"
            aria-label={
              mobileMenuOpen
                ? 'Close navigation menu'
                : 'Open navigation menu'
            }
            aria-expanded={mobileMenuOpen}
            aria-controls="mobile-nav"
            onClick={() =>
              setMobileMenuOpen((current) => !current)
            }
          >
            {mobileMenuOpen ? (
              <X size={27} />
            ) : (
              <Menu size={27} />
            )}
          </button>
        </div>
      </div>

      {/* ============================================================
          MOBILE NAVIGATION
      ============================================================ */}
      {mobileMenuOpen && (
        <>
          <div
            className="mobile-menu-backdrop"
            onClick={closeMobileMenu}
            aria-hidden="true"
          />
          <div className="mobile-menu" id="mobile-nav">
            <div className="container mobile-menu-inner">
              {navItems.map((item) => (
                <div
                  key={item.label}
                  className="mobile-nav-group"
                >
                  {item.subItems ? (
                    <>
                      <button
                        type="button"
                        className={`mobile-nav-heading ${
                          isActive(item.path)
                            ? 'mobile-nav-heading-active'
                            : ''
                        }`}
                        aria-expanded={openGroup === item.label}
                        onClick={() =>
                          setOpenGroup((current) =>
                            current === item.label ? null : item.label
                          )
                        }
                      >
                        <span>{item.label}</span>
                        <ChevronDown size={18} />
                      </button>

                      {openGroup === item.label && (
                        <div className="mobile-submenu">
                          {item.subItems.map((subItem) => (
                            <Link
                              key={subItem.path}
                              to={subItem.path}
                              className="mobile-submenu-link"
                              onClick={closeMobileMenu}
                            >
                              {subItem.label}
                            </Link>
                          ))}
                        </div>
                      )}
                    </>
                  ) : (
                    <Link
                      to={item.path}
                      className={`mobile-nav-link ${
                        isActive(item.path)
                          ? 'mobile-nav-link-active'
                          : ''
                      }`}
                      onClick={closeMobileMenu}
                    >
                      {item.label}
                    </Link>
                  )}
                </div>
              ))}

              <button
                type="button"
                className="mobile-donate-button"
                onClick={() => {
                  closeMobileMenu();
                  onOpenDonate();
                }}
              >
                Donate Now
              </button>
            </div>
          </div>
        </>
      )}
    </header>
  );
}