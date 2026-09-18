import { useState, useEffect, Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import DonateModal from './components/DonateModal';
import Home from './pages/Home';
import { fetchCauses, trackVisit } from './api';

const About = lazy(() => import('./pages/About'));
const Causes = lazy(() => import('./pages/Causes'));
const Donate = lazy(() => import('./pages/Donate'));
const Gallery = lazy(() => import('./pages/Gallery'));
const Contact = lazy(() => import('./pages/Contact'));
const Terms = lazy(() => import('./pages/Terms'));
const Blog = lazy(() => import('./pages/Blog'));
const BlogPost = lazy(() => import('./pages/BlogPost'));
const Team = lazy(() => import('./pages/Team'));
const Certificates = lazy(() => import('./pages/Certificates'));
const JoinUs = lazy(() => import('./pages/JoinUs'));
const Impact = lazy(() => import('./pages/Impact'));
const Admin = lazy(() => import('./pages/Admin'));
const Partner = lazy(() => import('./pages/Partner'));
const VerifyCertificate = lazy(() => import('./pages/VerifyCertificate'));
const VerifyVolunteer = lazy(() => import('./pages/VerifyVolunteer'));

function ScrollToTop() {
  const { pathname, hash } = useLocation();

  useEffect(() => {
    // Scroll to the top whenever the route/path changes. Skip when
    // navigation only targets an in-page anchor (e.g. /about#founders),
    // which are handled by the pages themselves.
    if (hash) return;
    window.scrollTo(0, 0);
  }, [pathname, hash]);

  return null;
}

function PageLoader() {
  return (
    <div style={{ padding: '6rem 1rem', textAlign: 'center', color: '#475569' }}>
      Loading…
    </div>
  );
}

export default function App() {
  const [donateModalOpen, setDonateModalOpen] = useState(false);
  const [selectedCause, setSelectedCause] = useState(null);
  const [causes, setCauses] = useState([]);

  useEffect(() => {
    fetchCauses()
      .then((data) => setCauses(data))
      .catch((err) => console.error(err));

    trackVisit();
  }, []);

  useEffect(() => {
    document.body.classList.toggle('modal-open', donateModalOpen);
    return () => document.body.classList.remove('modal-open');
  }, [donateModalOpen]);

  const handleOpenDonate = (cause = null) => {
    setSelectedCause(cause);
    setDonateModalOpen(true);
  };

  const handleCloseDonate = () => {
    setDonateModalOpen(false);
    setSelectedCause(null);
  };

  return (
    <Router>
      <ScrollToTop />
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100dvh' }}>
        <Header onOpenDonate={() => handleOpenDonate()} />

        <main style={{ flexGrow: 1 }}>
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/" element={<Home onOpenDonate={() => handleOpenDonate()} onSelectCauseToDonate={(c) => handleOpenDonate(c)} />} />
              <Route path="/about" element={<About />} />
              <Route path="/causes" element={<Causes onSelectCauseToDonate={(c) => handleOpenDonate(c)} />} />
              <Route path="/donate" element={<Donate onOpenDonate={() => handleOpenDonate()} />} />
              <Route path="/gallery" element={<Gallery />} />
              <Route path="/contact" element={<Contact />} />
              <Route path="/terms" element={<Terms />} />
              <Route path="/blog" element={<Blog />} />
              <Route path="/blog/:id" element={<BlogPost />} />
              <Route path="/team" element={<Team />} />
              <Route path="/team/:teamName" element={<Team />} />
              <Route path="/certificates" element={<Certificates />} />
              <Route path="/join" element={<JoinUs onOpenDonate={() => handleOpenDonate()} />} />
              <Route path="/impact" element={<Impact />} />
              <Route path="/admin" element={<Admin />} />
              <Route path="/partners/:partnerSlug" element={<Partner />} />
              <Route path="/verify/certificate/:identifier" element={<VerifyCertificate />} />
              <Route path="/verify/:identifier" element={<VerifyCertificate />} />
              <Route path="/verify/volunteer/:identifier" element={<VerifyVolunteer />} />
            </Routes>
          </Suspense>
        </main>

        <Footer onOpenDonate={() => handleOpenDonate()} />

        <DonateModal
          isOpen={donateModalOpen}
          onClose={handleCloseDonate}
          selectedCause={selectedCause}
          causes={causes}
        />
      </div>
    </Router>
  );
}