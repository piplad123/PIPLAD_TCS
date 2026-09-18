import React, { useEffect, useState } from 'react';

import CertificateManagement from '../components/admin/CertificateManagement';
import CertificateHistory from '../components/admin/CertificateHistory';

import {
  BadgeCheck,
  CalendarDays,
  HandHeart,
  History,
  Image as ImageIcon,
  LogIn,
  LogOut,
  MessageSquare,
  RefreshCw,
  ShieldCheck,
  Trash2,
  Upload,
  Video,
  DollarSign,
  Users,
  Heart,
  Check,
  X,
  Award,
  Edit3,
  Mail,
  MailX,
  BarChart3,
  ChevronRight,
  Eye,
  EyeOff,
  LayoutDashboard,
  Link2,
  Send,
  Target,
  UserCheck,
  Settings,
  Home,
  ArrowUp,
  ArrowDown,
  Save,
  Plus,
} from 'lucide-react';

import {
  clearAdminCredentials,
  createAdminCause,
  createAdminCertificate,
  createAdminFooterFocus,
  createAdminFooterQuickLink,
  createAdminHomeSlide,
  createAdminMentor,
  createAdminProject,
  createAdminTeamMember,
  deleteAdminCause,
  deleteAdminCertificate,
  deleteAdminFooterFocus,
  deleteAdminFooterQuickLink,
  deleteAdminGalleryImage,
  deleteAdminHomeSlide,
  deleteAdminMentor,
  deleteAdminProject,
  deleteAdminTeamMember,
  deleteAdminVideo,
  deleteContactInquiry,
  fetchAdminCauses,
  fetchAdminCertificates,
  fetchAdminFounder,
  fetchAdminFooterFocus,
  fetchAdminFooterQuickLinks,
  fetchAdminGallery,
  fetchAdminHomeSlides,
  fetchAdminMentors,
  fetchAdminProjects,
  fetchAdminStats,
  fetchAdminVisits,
  fetchAdminTeam,
  fetchAdminTeamCard,
  fetchAdminVideos,
  fetchAdminVolunteers,
  fetchAdminGalleryCategories,
  fetchAdminVideoCategories,
  fetchContactInquiries,
  fetchDonationsList,
  getAdminCredentials,
  reorderAdminFooterFocus,
  reorderAdminFooterQuickLinks,
  reorderAdminHomeSlides,
  resolveMediaUrl,
  sendAdminTeamCard,
  setAdminCredentials,
  updateAdminCause,
  updateAdminCertificate,
  updateAdminFounder,
  updateAdminFooterFocus,
  updateAdminFooterQuickLink,
  updateAdminHomeSlide,
  updateAdminMentor,
  updateAdminProject,
  updateAdminTeamMember,
  updateAdminVolunteerStatus,
  uploadAdminGalleryImage,
  uploadAdminVideo,
  deleteAdminVolunteer,
  resendAdminVolunteerCard,
  resendAdminVolunteerRejection,
  fetchAdminDonations,
  fetchAdminDonationEmailPreview,
  resendAdminDonationReceipt,
  fetchAdminImpact,
  updateAdminImpact,
  fetchSiteSettings,
  updateSiteSettings,
} from '../api';

import { defaultHeroSlides } from '../data/heroSlides';


// ============================================================
// EMPTY FORMS
// ============================================================

const emptyPhotoForm = {
  title: '',
  description: '',
  category: 'Photo Gallery',
  files: [],
};

const emptyVideoForm = {
  title: '',
  description: '',
  category: 'Video Gallery',
  files: [],
};

const emptyProjectForm = {
  title: '',
  description: '',
  expectedDate: '',
  file: null,
};

const emptyCertificateForm = {
  title: '',
  description: '',
  file: null,
};

const emptyCauseForm = {
  title: '',
  category: '',
  shortDescription: '',
  fullDescription: '',
  targetAmount: '',
  file: null,
};


// ============================================================
// SHARED COMPONENTS
// ============================================================

function ErrorMessage({ message }) {
  if (!message) {
    return null;
  }

  return (
    <div
      style={{
        padding: '0.85rem 1rem',
        marginBottom: '1rem',
        borderRadius: 8,
        background: '#fee2e2',
        color: '#991b1b',
      }}
    >
      {message}
    </div>
  );
}


function ManagerSection({
  title,
  icon,
  children,
}) {
  return (
    <section
      className="card"
      style={{
        padding: '1.5rem',
        marginBottom: '2rem',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '.6rem',
          marginBottom: '1.25rem',
        }}
      >
        {icon}
        <h2 style={{ margin: 0 }}>
          {title}
        </h2>
      </div>

      {children}
    </section>
  );
}


// ============================================================
// CATEGORY PICKER
// ============================================================

function CategoryPicker({
  value,
  onChange,
  options,
}) {
  const [isNew, setIsNew] = useState(false);
  const [newValue, setNewValue] = useState('');

  const selectStyle = {
    ...inputStyle,
    appearance: 'auto',
  };

  return (
    <div
      style={{
        display: 'grid',
        gap: '.5rem',
      }}
    >
      {!isNew ? (
        <select
          value={options.includes(value) ? value : ''}
          onChange={(e) => {
            if (e.target.value === '__new__') {
              setIsNew(true);
              setNewValue('');
              onChange('');
              return;
            }

            onChange(e.target.value);
          }}
          style={selectStyle}
        >
          <option value="" disabled>
            Select a category
          </option>

          {options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}

          <option value="__new__">
            + Add New / Other...
          </option>
        </select>
      ) : (
        <div style={{ display: 'grid', gap: '.5rem' }}>
          <input
            placeholder="Type a new category name"
            value={newValue}
            onChange={(e) => {
              setNewValue(e.target.value);
              onChange(e.target.value);
            }}
            style={inputStyle}
            autoFocus
          />
          <button
            type="button"
            className="btn"
            onClick={() => {
              setIsNew(false);
              setNewValue('');
              onChange(options[0] || '');
            }}
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}


// ============================================================
// ADMIN LOGIN
// ============================================================

function AdminLogin({ onLogin }) {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();

    setError('');
    setLoading(true);

    try {
      setAdminCredentials(
        username,
        password
      );

      await fetchAdminStats();

      onLogin();
    } catch (err) {
      clearAdminCredentials();

      setError(
        err.code === 'ADMIN_AUTH_REQUIRED'
          ? 'Invalid admin username or password.'
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section
      className="section-padding"
      style={{
        background: '#f8fafc',
        minHeight: '70vh',
      }}
    >
      <div
        className="container"
        style={{ maxWidth: 460 }}
      >
        <div
          className="card"
          style={{ padding: '2rem' }}
        >
          <div
            style={{
              textAlign: 'center',
              marginBottom: '1.5rem',
            }}
          >
            <ShieldCheck
              size={42}
              color="#059669"
            />

            <h1
              style={{
                margin:
                  '0.75rem 0 0.4rem',
              }}
            >
              Admin Login
            </h1>

            <p
              style={{
                color: '#64748b',
                margin: 0,
              }}
            >
              Sign in to manage Piplad.
            </p>
          </div>

          <ErrorMessage
            message={error}
          />

          <form onSubmit={submit}>
            <label
              style={{
                display: 'block',
                fontWeight: 600,
                marginBottom: 6,
              }}
            >
              Username
            </label>

            <input
              value={username}
              onChange={(e) =>
                setUsername(e.target.value)
              }
              required
              style={inputStyle}
            />

            <label
              style={{
                display: 'block',
                fontWeight: 600,
                margin:
                  '1rem 0 6px',
              }}
            >
              Password
            </label>

            <input
              type="password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              required
              style={inputStyle}
            />

            <button
              className="btn"
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                marginTop: '1.25rem',
                background: '#059669',
                color: '#fff',
                border: 0,
              }}
            >
              <LogIn size={17} />

              {loading
                ? 'Signing in...'
                : 'Sign in'}
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}


// ============================================================
// PHOTO GALLERY
// ============================================================

function GalleryManager({ refreshAll }) {
  const [items, setItems] =
    useState([]);

  const [selectedIds, setSelectedIds] =
    useState([]);

  const pageSize = 9;

  const [page, setPage] =
    useState(1);

  const currentPage = Math.min(
    page,
    Math.max(
      1,
      Math.ceil(
        items.length / pageSize
      )
    )
  );

  const totalPages = Math.max(
    1,
    Math.ceil(
      items.length / pageSize
    )
  );

  const pageItems = items.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  const [form, setForm] =
    useState(emptyPhotoForm);

  const [categories, setCategories] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState('');

  async function load() {
    setLoading(true);

    try {
      const [photoData, categoryData] =
        await Promise.all([
          fetchAdminGallery(),
          fetchAdminGalleryCategories(),
        ]);

      setItems(photoData);
      setSelectedIds([]);
      setCategories(categoryData);
      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(e) {
    e.preventDefault();

    setError('');

    if (form.files.length === 0) {
      setError(
        'Please select at least one image.'
      );
      return;
    }

    setSaving(true);

    try {
      await uploadAdminGalleryImage(
        form
      );

      setForm(emptyPhotoForm);

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  async function remove(id) {
    if (
      !window.confirm(
        'Delete this photograph?'
      )
    ) {
      return;
    }

    try {
      await deleteAdminGalleryImage(id);

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    }
  }

  function toggleSelected(id) {
    setSelectedIds((current) =>
      current.includes(id)
        ? current.filter((selectedId) => selectedId !== id)
        : [...current, id]
    );
  }

  function toggleAll() {
    setSelectedIds((current) =>
      current.length === items.length
        ? []
        : items.map((item) => item.id)
    );
  }

  async function removeSelected() {
    if (selectedIds.length === 0) return;

    if (
      !window.confirm(
        `Delete ${selectedIds.length} selected ${selectedIds.length === 1 ? 'photo' : 'photos'}?`
      )
    ) {
      return;
    }

    try {
      await Promise.all(
        selectedIds.map((id) => deleteAdminGalleryImage(id))
      );

      await load();
      refreshAll();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <ManagerSection
      title="Photo Gallery"
      icon={
        <ImageIcon size={22} />
      }
    >
      <ErrorMessage
        message={error}
      />

      {items.length > 0 && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '.75rem',
            flexWrap: 'wrap',
            marginBottom: '1rem',
          }}
        >
          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '.5rem',
              color: '#334155',
              fontWeight: 600,
            }}
          >
            <input
              type="checkbox"
              checked={selectedIds.length === items.length}
              onChange={toggleAll}
            />
            Select all photos
          </label>

          {selectedIds.length > 0 && (
            <button
              type="button"
              className="btn"
              onClick={removeSelected}
              style={dangerButton}
            >
              <Trash2 size={15} />
              Delete selected ({selectedIds.length})
            </button>
          )}
        </div>
      )}

      <form
        onSubmit={submit}
        style={formGridStyle}
      >
        <input
          placeholder="Event / album title"
          value={form.title}
          onChange={(e) =>
            setForm({
              ...form,
              title: e.target.value,
            })
          }
          required
          style={inputStyle}
        />

        <CategoryPicker
          value={form.category}
          options={categories}
          onChange={(category) =>
            setForm({
              ...form,
              category,
            })
          }
        />

        <input
          type="file"
          multiple
          accept="image/jpeg,image/png,image/webp,image/gif"
          onChange={(e) =>
            setForm({
              ...form,
              files:
                Array.from(
                  e.target.files || []
                ),
            })
          }
          required
          style={inputStyle}
        />

        {form.files.length > 0 && (
          <p
            style={{
              color: '#475569',
              fontSize: '.9rem',
              margin: 0,
            }}
          >
            {form.files.length}
            {' '}
            {form.files.length === 1
              ? 'file'
              : 'files'}
            {' '}
            selected
          </p>
        )}

        <textarea
          placeholder="Description / caption (optional)"
          value={form.description}
          onChange={(e) =>
            setForm({
              ...form,
              description:
                e.target.value,
            })
          }
          style={textareaStyle}
        />

        <button
          className="btn"
          disabled={saving}
          style={primaryButton}
        >
          <Upload size={17} />

          {saving
            ? 'Uploading...'
            : 'Upload Photos'}
        </button>
      </form>

      <div style={managerGrid}>
        {loading ? (
          <p>Loading...</p>
        ) : items.length === 0 ? (
          <p
            style={{
              color: '#64748b',
            }}
          >
            No photos uploaded yet.
          </p>
        ) : (
          pageItems.map((item) => (
            <article
              key={item.id}
              className="card"
              style={{
                overflow: 'hidden',
              }}
            >
              <label
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '.5rem',
                  padding: '.75rem 1rem 0',
                  color: '#334155',
                  fontWeight: 600,
                  fontSize: '.9rem',
                }}
              >
                <input
                  type="checkbox"
                  checked={selectedIds.includes(item.id)}
                  onChange={() => toggleSelected(item.id)}
                />
                Select photo
              </label>

              <img
                src={resolveMediaUrl(
                  item.image_url
                )}
                alt={item.title}
                style={{
                  width: '100%',
                  height: 180,
                  objectFit: 'cover',
                }}
              />

              <div
                style={{
                  padding: '1rem',
                }}
              >
                {item.category && (
                  <span
                    style={{
                      display:
                        'inline-block',
                      background:
                        '#ecfdf5',
                      color: '#047857',
                      fontSize: '.75rem',
                      fontWeight: 700,
                      padding:
                        '.25rem .6rem',
                      borderRadius: 999,
                      marginBottom:
                        '.6rem',
                    }}
                  >
                    {item.category}
                  </span>
                )}

                <h3
                  style={{
                    margin: '0 0 .4rem',
                  }}
                >
                  {item.title}
                </h3>

                {item.description && (
                  <p
                    style={{
                      color: '#64748b',
                    }}
                  >
                    {item.description}
                  </p>
                )}

                <button
                  onClick={() =>
                    remove(item.id)
                  }
                  className="btn"
                  style={dangerButton}
                >
                  <Trash2 size={15} />
                  Delete
                </button>
              </div>
            </article>
          ))
        )}
      </div>

      <Pagination
        page={currentPage}
        totalPages={totalPages}
        onPage={setPage}
      />
    </ManagerSection>
  );
}


// ============================================================
// VIDEO MANAGER
// ============================================================

function VideoManager({ refreshAll }) {
  const [items, setItems] =
    useState([]);

  const [form, setForm] =
    useState(emptyVideoForm);

  const [categories, setCategories] =
    useState([]);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState('');

  const [loading, setLoading] =
    useState(true);

  const pageSize = 9;

  const [page, setPage] =
    useState(1);

  const currentPage = Math.min(
    page,
    Math.max(
      1,
      Math.ceil(
        items.length / pageSize
      )
    )
  );

  const totalPages = Math.max(
    1,
    Math.ceil(
      items.length / pageSize
    )
  );

  const pageItems = items.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  async function load() {
    setLoading(true);

    try {
      const [videoData, categoryData] =
        await Promise.all([
          fetchAdminVideos(),
          fetchAdminVideoCategories(),
        ]);

      setItems(videoData);
      setCategories(categoryData);
      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(e) {
    e.preventDefault();

    setError('');

    if (form.files.length === 0) {
      setError(
        'Please select at least one video.'
      );
      return;
    }

    setSaving(true);

    try {
      await uploadAdminVideo(
        form
      );

      setForm(emptyVideoForm);

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  async function remove(id) {
    if (
      !window.confirm(
        'Delete this video?'
      )
    ) {
      return;
    }

    try {
      await deleteAdminVideo(id);

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <ManagerSection
      title="Video Gallery"
      icon={<Video size={22} />}
    >
      <ErrorMessage
        message={error}
      />

      <form
        onSubmit={submit}
        style={formGridStyle}
      >
        <input
          placeholder="Video title"
          value={form.title}
          onChange={(e) =>
            setForm({
              ...form,
              title: e.target.value,
            })
          }
          required
          style={inputStyle}
        />

        <CategoryPicker
          value={form.category}
          options={categories}
          onChange={(category) =>
            setForm({
              ...form,
              category,
            })
          }
        />

        <input
          type="file"
          multiple
          accept="video/mp4,video/webm,video/quicktime,video/x-m4v"
          onChange={(e) =>
            setForm({
              ...form,
              files:
                Array.from(
                  e.target.files || []
                ),
            })
          }
          required
          style={inputStyle}
        />

        {form.files.length > 0 && (
          <p
            style={{
              color: '#475569',
              fontSize: '.9rem',
              margin: 0,
            }}
          >
            {form.files.length}
            {' '}
            {form.files.length === 1
              ? 'file'
              : 'files'}
            {' '}
            selected
          </p>
        )}

        <textarea
          placeholder="Description (optional)"
          value={form.description}
          onChange={(e) =>
            setForm({
              ...form,
              description:
                e.target.value,
            })
          }
          style={textareaStyle}
        />

        <button
          className="btn"
          disabled={saving}
          style={primaryButton}
        >
          <Upload size={17} />

          {saving
            ? 'Uploading...'
            : 'Upload Videos'}
        </button>
      </form>

      <p
        style={{
          color: '#64748b',
          fontSize: '.9rem',
        }}
      >
        Maximum video size: 100 MB.
        MP4 is recommended for browser
        compatibility.
      </p>

      <div style={managerGrid}>
        {loading ? (
          <p>Loading...</p>
        ) : items.length === 0 ? (
          <p
            style={{
              color: '#64748b',
            }}
          >
            No videos uploaded yet.
          </p>
        ) : (
          pageItems.map((item) => (
            <article
              key={item.id}
              className="card"
              style={{
                overflow: 'hidden',
              }}
            >
              <video
                controls
                preload="metadata"
                src={resolveMediaUrl(
                  item.video_url
                )}
                style={{
                  width: '100%',
                  height: 180,
                  objectFit: 'cover',
                }}
              />

              <div
                style={{
                  padding: '1rem',
                }}
              >
                {item.category && (
                  <span
                    style={{
                      display:
                        'inline-block',
                      background:
                        '#ecfdf5',
                      color: '#047857',
                      fontSize: '.75rem',
                      fontWeight: 700,
                      padding:
                        '.25rem .6rem',
                      borderRadius: 999,
                      marginBottom:
                        '.6rem',
                    }}
                  >
                    {item.category}
                  </span>
                )}

                <h3
                  style={{
                    margin: '0 0 .4rem',
                  }}
                >
                  {item.title}
                </h3>

                {item.description && (
                  <p
                    style={{
                      color: '#64748b',
                    }}
                  >
                    {item.description}
                  </p>
                )}

                <button
                  onClick={() =>
                    remove(item.id)
                  }
                  className="btn"
                  style={dangerButton}
                >
                  <Trash2 size={15} />
                  Delete
                </button>
              </div>
            </article>
          ))
        )}
      </div>

      <Pagination
        page={currentPage}
        totalPages={totalPages}
        onPage={setPage}
      />
    </ManagerSection>
  );
}


// ============================================================
// VOLUNTEER MANAGER
// ============================================================

function VolunteerManager() {
  const [items, setItems] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState('');

  const [notice, setNotice] =
    useState('');

  const [busyId, setBusyId] =
    useState(null);

  const [filter, setFilter] =
    useState('all');

  const filteredItems =
    filter === 'all'
      ? items
      : items.filter(
          (item) =>
            item.status === filter
        );

  const pageSize = 5;

  const [page, setPage] =
    useState(1);

  useEffect(() => {
    setPage(1);
  }, [filter]);

  const currentPage = Math.min(
    page,
    Math.max(
      1,
      Math.ceil(
        filteredItems.length / pageSize
      )
    )
  );

  const totalPages = Math.max(
    1,
    Math.ceil(
      filteredItems.length / pageSize
    )
  );

  const pageItems = filteredItems.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  async function load() {
    setLoading(true);

    try {
      setItems(
        await fetchAdminVolunteers()
      );

      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function setStatus(
    id,
    status
  ) {
    setBusyId(id);
    setError('');
    setNotice('');

    try {
      const updated =
        await updateAdminVolunteerStatus(
          id,
          status
        );

      setItems((current) =>
        current.map((item) =>
          item.id === id
            ? updated
            : item
        )
      );

      if (
        status === 'accepted' &&
        updated &&
        updated.volunteer_id &&
        updated.card_emailed === false &&
        !updated.card_sent_at
      ) {
        setNotice(
          'Volunteer accepted. The welcome card is being emailed automatically and may take a minute - use "Send card" to resend it later if needed.'
        );
      } else if (status === 'rejected') {
        setNotice(
          'Volunteer rejected. The rejection email is being sent automatically and may take a minute.'
        );
      } else {
        setNotice('');
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setBusyId(null);
    }
  }

  async function resendCard(id) {
    setBusyId(id);
    setError('');
    setNotice('');

    try {
      const updated =
        await resendAdminVolunteerCard(id);

      setItems((current) =>
        current.map((item) =>
          item.id === id
            ? updated
            : item
        )
      );

      if (updated && updated.card_sent_at) {
        setNotice('Welcome card emailed.');
      } else {
        setNotice(
          'Welcome card is being emailed and may take a minute.'
        );
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setBusyId(null);
    }
  }

  async function resendRejection(id) {
    setBusyId(id);
    setError('');
    setNotice('');

    try {
      const updated =
        await resendAdminVolunteerRejection(id);

      setItems((current) =>
        current.map((item) =>
          item.id === id
            ? updated
            : item
        )
      );

      if (updated && updated.rejection_email_sent_at) {
        setNotice('Rejection email sent.');
      } else {
        setNotice(
          'Rejection email is being sent and may take a minute.'
        );
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setBusyId(null);
    }
  }

  async function remove(id) {
    if (
      !window.confirm(
        'Remove this volunteer application?'
      )
    ) {
      return;
    }

    setBusyId(id);
    setError('');
    setNotice('');

    try {
      await deleteAdminVolunteer(
        id
      );

      await load();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusyId(null);
    }
  }

  return (
    <ManagerSection
      title="Volunteer Applications"
      icon={<Users size={22} />}
    >
      <ErrorMessage
        message={error}
      />

      {notice && (
        <div
          style={{
            padding: '0.85rem 1rem',
            marginBottom: '1rem',
            borderRadius: 8,
            background: '#dcfce7',
            color: '#166534',
          }}
        >
          {notice}
        </div>
      )}

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent:
            'space-between',
          gap: '.75rem',
          flexWrap: 'wrap',
          marginBottom: '1rem',
        }}
      >
        <div
          style={{
            display: 'flex',
            gap: '.5rem',
            flexWrap: 'wrap',
          }}
        >
          {[
            ['all', 'All'],
            ['pending', 'Pending'],
            ['accepted', 'Accepted'],
            ['rejected', 'Rejected'],
          ].map(
            ([key, label]) => (
              <button
                key={key}
                className="btn"
                onClick={() =>
                  setFilter(key)
                }
                style={{
                  ...outlineButton,
                  background:
                    filter === key
                      ? '#059669'
                      : 'transparent',
                  color:
                    filter === key
                      ? '#ffffff'
                      : '#059669',
                  borderColor:
                    filter === key
                      ? '#059669'
                      : '#059669',
                }}
              >
                {label}
              </button>
            )
          )}
        </div>

        <span
          style={{
            color: '#64748b',
            fontSize: '.9rem',
          }}
        >
          {filteredItems.length} of{' '}
          {items.length} application
          {items.length === 1
            ? ''
            : 's'}
        </span>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : filteredItems.length === 0 ? (
        <p
          style={{
            color: '#64748b',
          }}
        >
          No volunteer applications yet.
        </p>
      ) : (
        <div
          style={{
            display: 'grid',
            gap: '1rem',
          }}
        >
          {pageItems.map((item) => (
            <article
              key={item.id}
              className="card"
              style={{
                padding: '1rem',
                borderLeft:
                  `4px solid ${
                    item.status ===
                    'accepted'
                      ? '#059669'
                      : item.status ===
                        'rejected'
                      ? '#dc2626'
                      : '#d97706'
                  }`,
              }}
            >
              <div
                style={{
                  display: 'flex',
                  justifyContent:
                    'space-between',
                  gap: '1rem',
                  flexWrap: 'wrap',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    gap: '.85rem',
                    flex: 1,
                    minWidth: 0,
                  }}
                >
                  {item.profile_pic_url ? (
                    <img
                      src={resolveMediaUrl(
                        item.profile_pic_url
                      )}
                      alt={item.full_name}
                      style={{
                        width: 56,
                        height: 56,
                        borderRadius: 12,
                        objectFit: 'cover',
                        flexShrink: 0,
                      }}
                    />
                  ) : (
                    <div
                      style={{
                        width: 56,
                        height: 56,
                        borderRadius: 12,
                        background: '#e2e8f0',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#64748b',
                        flexShrink: 0,
                      }}
                    >
                      <Users size={22} />
                    </div>
                  )}

                  <div
                    style={{
                      minWidth: 0,
                    }}
                  >
                    <h3
                      style={{
                        margin: 0,
                      }}
                    >
                      {item.full_name}
                    </h3>

                    <p
                      style={{
                        color: '#475569',
                        margin:
                          '.35rem 0',
                      }}
                    >
                      {item.email}
                      {' · '}
                      {item.phone}
                      <br />
                      <span
                        style={{
                          color: '#64748b',
                          fontSize:
                            '.85rem',
                        }}
                      >
                        Applied{' '}
                        {new Date(
                          item.created_at
                        ).toLocaleString()}
                      </span>
                    </p>

                    <span
                      style={{
                        display:
                          'inline-block',
                        background:
                          '#ecfdf5',
                        color: '#047857',
                        fontSize:
                          '.75rem',
                        fontWeight: 700,
                        padding:
                          '.25rem .6rem',
                        borderRadius: 999,
                        marginTop:
                          '.35rem',
                      }}
                    >
                      {item.interest_area}
                    </span>

                    {item.about_yourself && (
                    <p
                      style={{
                        color: '#475569',
                        lineHeight: 1.5,
                      }}
                    >
                      {
                        item.about_yourself
                      }
                    </p>
                  )}

                  {item.volunteer_id && (
                    <p
                      style={{
                        color: '#059669',
                        marginTop: '.35rem',
                        fontWeight: 700,
                      }}
                    >
                      Volunteer ID:{' '}
                      {item.volunteer_id}
                    </p>
                  )}
                  </div>
                </div>

                <span
                  className="badge"
                  style={{
                    background:
                      item.status ===
                      'accepted'
                        ? '#d1fae5'
                        : item.status ===
                          'rejected'
                        ? '#fee2e2'
                        : '#fef3c7',
                    color:
                      item.status ===
                      'accepted'
                        ? '#065f46'
                        : item.status ===
                          'rejected'
                        ? '#991b1b'
                        : '#92400e',
                  }}
                >
                  {item.status}
                </span>

                {item.status ===
                  'accepted' && (
                  <span
                    className="badge"
                    style={{
                      display:
                        'inline-flex',
                      alignItems: 'center',
                      gap: '.3rem',
                      background: item.card_sent_at
                        ? '#d1fae5'
                        : '#fef3c7',
                      color: item.card_sent_at
                        ? '#065f46'
                        : '#92400e',
                    }}
                    title={
                      item.card_sent_at
                        ? `Welcome card sent on ${new Date(
                            item.card_sent_at
                          ).toLocaleString()}`
                        : 'Welcome card not emailed yet'
                    }
                  >
                    {item.card_sent_at ? (
                      <Mail size={13} />
                    ) : (
                      <MailX size={13} />
                    )}
                    {item.card_sent_at
                      ? 'Card emailed'
                      : 'Card not sent'}
                  </span>
                )}

                {item.status ===
                  'rejected' && (
                  <span
                    className="badge"
                    style={{
                      display:
                        'inline-flex',
                      alignItems: 'center',
                      gap: '.3rem',
                      background: item.rejection_email_sent_at
                        ? '#d1fae5'
                        : '#fef3c7',
                      color: item.rejection_email_sent_at
                        ? '#065f46'
                        : '#92400e',
                    }}
                    title={
                      item.rejection_email_sent_at
                        ? `Rejection email sent on ${new Date(
                            item.rejection_email_sent_at
                          ).toLocaleString()}`
                        : 'Rejection email not sent yet'
                    }
                  >
                    {item.rejection_email_sent_at ? (
                      <Mail size={13} />
                    ) : (
                      <MailX size={13} />
                    )}
                    {item.rejection_email_sent_at
                      ? 'Rejection emailed'
                      : 'Rejection not sent'}
                  </span>
                )}
              </div>

              <div
                style={{
                  display: 'flex',
                  gap: '.5rem',
                  flexWrap: 'wrap',
                  marginTop: '1rem',
                }}
              >
                <button
                  className="btn"
                  onClick={() =>
                    setStatus(
                      item.id,
                      'accepted'
                    )
                  }
                  disabled={busyId === item.id}
                  style={primaryButton}
                >
                  <Check size={15} />
                  {busyId === item.id
                    ? 'Processing...'
                    : 'Accept'}
                </button>

                <button
                  className="btn"
                  onClick={() =>
                    setStatus(
                      item.id,
                      'rejected'
                    )
                  }
                  disabled={busyId === item.id}
                  style={dangerButton}
                >
                  <X size={15} />
                  {busyId === item.id
                    ? 'Processing...'
                    : 'Reject'}
                </button>

                {item.status ===
                  'accepted' && (
                  <button
                    className="btn"
                    onClick={() =>
                      resendCard(item.id)
                    }
                    disabled={busyId === item.id}
                    style={{
                      ...outlineButton,
                    }}
                  >
                    <Mail size={15} />
                    {busyId === item.id
                      ? 'Processing...'
                      : item.card_sent_at
                      ? 'Resend card'
                      : 'Send card'}
                  </button>
                )}

                {item.status ===
                  'rejected' && (
                  <button
                    className="btn"
                    onClick={() =>
                      resendRejection(item.id)
                    }
                    disabled={busyId === item.id}
                    style={{
                      ...outlineButton,
                    }}
                  >
                    <Mail size={15} />
                    {busyId === item.id
                      ? 'Processing...'
                      : item.rejection_email_sent_at
                      ? 'Resend rejection email'
                      : 'Send rejection email'}
                  </button>
                )}

                <button
                  className="btn"
                  onClick={() =>
                    remove(item.id)
                  }
                  disabled={busyId === item.id}
                  style={dangerButton}
                >
                  <Trash2 size={15} />
                  {busyId === item.id
                    ? 'Processing...'
                    : 'Remove'}
                </button>
              </div>
            </article>
          ))}
          <Pagination
            page={currentPage}
            totalPages={totalPages}
            onPage={setPage}
          />
        </div>
      )}
    </ManagerSection>
  );
}


// ============================================================
// DONATION MANAGER
// ============================================================

function DonationManager() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(5);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  async function load(nextPage = page) {
    setLoading(true);
    try {
      const data = await fetchAdminDonations(nextPage, pageSize);
      setItems(data.items || []);
      setTotal(data.total || 0);
      setPage(data.page || 1);
      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load(1);
  }, [pageSize]);

  async function resendReceipt(id) {
    try {
      const updated = await resendAdminDonationReceipt(id);
      setItems((current) =>
        current.map((item) =>
          item.id === id ? updated : item
        )
      );
      setError('');
    } catch (e) {
      setError(e.message);
    }
  }

  const [emailPreview, setEmailPreview] = useState(null);

  async function openReceiptPreview(id) {
    try {
      const data = await fetchAdminDonationEmailPreview(id);
      setEmailPreview(data);
      setError('');
    } catch (e) {
      setError(e.message);
    }
  }

  const panelStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '1rem',
    flexWrap: 'wrap',
    marginBottom: '1rem',
  };

  const badgeStyle = (status) => {
    const completed = status === 'completed';
    return {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '.3rem',
      borderRadius: '9999px',
      padding: '.25rem .75rem',
      fontSize: '0.78rem',
      fontWeight: 700,
      background: completed ? '#d1fae5' : '#fef3c7',
      color: completed ? '#065f46' : '#92400e',
    };
  };

  const paginationStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '.75rem',
    flexWrap: 'wrap',
    marginTop: '1.25rem',
  };

  const metaStyle = {
    color: '#64748b',
    fontSize: '.9rem',
    marginBottom: '1rem',
  };

  function goTo(next) {
    if (next < 1 || next > totalPages) {
      return;
    }
    load(next);
  }

  return (
    <ManagerSection
      title="Donations"
      icon={<DollarSign size={22} />}
    >
      <ErrorMessage message={error} />

      {!loading && total > 0 && (
        <p style={metaStyle}>
          Showing {((page - 1) * pageSize) + 1}–
          {Math.min(page * pageSize, total)} of {total} donations
        </p>
      )}

      {loading ? (
        <p>Loading...</p>
      ) : items.length === 0 ? (
        <p style={{ color: '#64748b' }}>
          No donation records yet.
        </p>
      ) : (
        <div style={{ display: 'grid', gap: '1rem' }}>
          {items.map((item) => (
            <article
              key={item.id}
              className="card"
              style={{ padding: '1rem' }}
            >
              <div style={panelStyle}>
                <div>
                  <h3 style={{ margin: 0 }}>
                    {item.donor_name}
                  </h3>
                  <p style={{ color: '#475569', margin: '.35rem 0' }}>
                    {item.donor_email}
                    {item.donor_phone ? ` · ${item.donor_phone}` : ''}
                  </p>
                  <p style={{ color: '#64748b', margin: 0 }}>
                    {item.razorpay_order_id || '—'} ·{' '}
                    {new Date(item.created_at).toLocaleString()}
                  </p>
                </div>

                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '.75rem',
                    flexWrap: 'wrap',
                  }}
                >
                  <span style={{ fontSize: '1.15rem', fontWeight: 800, color: '#059669' }}>
                    ₹{Number(item.amount).toLocaleString('en-IN')}
                  </span>

                  <span style={badgeStyle(item.status)}>
                    {item.status}
                  </span>

                  {item.status === 'completed' && (
                    <span
                      style={badgeStyle('completed')}
                      title={
                        item.receipt_sent_at
                          ? `Receipt emailed on ${new Date(item.receipt_sent_at).toLocaleString()}`
                          : 'Receipt not emailed yet'
                      }
                    >
                      {item.receipt_sent_at ? (
                        <Mail size={13} />
                      ) : (
                        <MailX size={13} />
                      )}
                      {item.receipt_sent_at
                        ? 'Emailed'
                        : 'Not sent'}
                    </span>
                  )}
                </div>
              </div>

              {item.status === 'completed' && (
                <div style={{ display: 'flex', gap: '.5rem', flexWrap: 'wrap', marginTop: '.75rem' }}>
                  <button
                    className="btn"
                    onClick={() => resendReceipt(item.id)}
                    style={{ ...outlineButton }}
                  >
                    <Send size={15} />
                    {item.receipt_sent_at
                      ? 'Resend receipt'
                      : 'Send receipt'}
                  </button>

                  <button
                    className="btn"
                    onClick={() => openReceiptPreview(item.id)}
                    style={{ ...outlineButton }}
                  >
                    <Eye size={15} />
                    View emailed receipt
                  </button>
                </div>
              )}
            </article>
          ))}
        </div>
      )}

      {!loading && total > 0 && (
        <div style={paginationStyle}>
          <button
            className="btn"
            onClick={() => goTo(page - 1)}
            disabled={page <= 1}
            style={outlineButton}
          >
            Previous
          </button>

          <span style={{ color: '#475569', fontSize: '.9rem' }}>
            Page {page} of {totalPages}
          </span>

          <button
            className="btn"
            onClick={() => goTo(page + 1)}
            disabled={page >= totalPages}
            style={outlineButton}
          >
            Next
          </button>
        </div>
      )}

      {emailPreview && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 1000,
            background: 'rgba(15,23,42,0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1rem',
          }}
          onClick={() => setEmailPreview(null)}
        >
          <div
            className="card"
            style={{
              width: '100%',
              maxWidth: 760,
              maxHeight: '90vh',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
              padding: 0,
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: '1rem',
                padding: '.75rem 1rem',
                borderBottom: '1px solid #e2e8f0',
              }}
            >
              <strong style={{ color: '#0f172a' }}>
                Receipt emailed to the donor
              </strong>
              <button
                className="btn"
                onClick={() => setEmailPreview(null)}
                style={outlineButton}
              >
                <X size={15} />
                Close
              </button>
            </div>
            <iframe
              title="Receipt email preview"
              srcDoc={emailPreview.html}
              sandbox=""
              style={{
                width: '100%',
                flex: 1,
                minHeight: '65vh',
                border: 'none',
                background: '#f1f5f9',
              }}
            />
          </div>
        </div>
      )}
    </ManagerSection>
  );
}


// ============================================================
// PROJECT MANAGER
// ============================================================

function ProjectManager({
  refreshAll,
}) {
  const [items, setItems] =
    useState([]);

  const [form, setForm] =
    useState(emptyProjectForm);

  const [editingId, setEditingId] =
    useState(null);

  const [removeImage, setRemoveImage] =
    useState(false);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState('');

  const [loading, setLoading] =
    useState(true);

  const pageSize = 6;

  const [page, setPage] =
    useState(1);

  const currentPage = Math.min(
    page,
    Math.max(
      1,
      Math.ceil(
        items.length / pageSize
      )
    )
  );

  const totalPages = Math.max(
    1,
    Math.ceil(
      items.length / pageSize
    )
  );

  const pageItems = items.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  async function load() {
    setLoading(true);

    try {
      setItems(
        await fetchAdminProjects()
      );
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function reset() {
    setForm(emptyProjectForm);
    setEditingId(null);
    setRemoveImage(false);
  }

  function edit(item) {
    setEditingId(item.id);

    setRemoveImage(false);

    setForm({
      title: item.title,
      description:
        item.description || '',
      expectedDate:
        item.expected_date || '',
      file: null,
    });

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  }

  async function submit(e) {
    e.preventDefault();

    setError('');
    setSaving(true);

    try {
      if (editingId) {
        await updateAdminProject(
          editingId,
          {
            ...form,
            removeImage,
          }
        );
      } else {
        await createAdminProject(
          form
        );
      }

      reset();

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  async function remove(id) {
    if (
      !window.confirm(
        'Delete this upcoming project?'
      )
    ) {
      return;
    }

    try {
      await deleteAdminProject(id);

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <ManagerSection
      title="Upcoming Projects"
      icon={
        <CalendarDays size={22} />
      }
    >
      <ErrorMessage
        message={error}
      />

      <form
        onSubmit={submit}
        style={formGridStyle}
      >
        <input
          placeholder="Project title"
          value={form.title}
          onChange={(e) =>
            setForm({
              ...form,
              title: e.target.value,
            })
          }
          required
          style={inputStyle}
        />

        <input
          type="date"
          value={form.expectedDate}
          onChange={(e) =>
            setForm({
              ...form,
              expectedDate:
                e.target.value,
            })
          }
          style={inputStyle}
        />

        <textarea
          placeholder="Project description"
          value={form.description}
          onChange={(e) =>
            setForm({
              ...form,
              description:
                e.target.value,
            })
          }
          style={textareaStyle}
        />

        <input
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          onChange={(e) =>
            setForm({
              ...form,
              file:
                e.target.files?.[0] ||
                null,
            })
          }
          style={inputStyle}
        />

        {editingId && (
          <label
            style={{
              display: 'flex',
              gap: '.5rem',
              alignItems: 'center',
            }}
          >
            <input
              type="checkbox"
              checked={removeImage}
              onChange={(e) =>
                setRemoveImage(
                  e.target.checked
                )
              }
            />

            Remove current image
          </label>
        )}

        <div
          style={{
            display: 'flex',
            gap: '.75rem',
            flexWrap: 'wrap',
          }}
        >
          <button
            className="btn"
            disabled={saving}
            style={primaryButton}
          >
            {saving
              ? 'Saving...'
              : editingId
              ? 'Update Project'
              : 'Add Upcoming Project'}
          </button>

          {editingId && (
            <button
              type="button"
              className="btn"
              onClick={reset}
            >
              Cancel
            </button>
          )}
        </div>
      </form>

      <div style={managerGrid}>
        {loading ? (
          <p>Loading...</p>
        ) : items.length === 0 ? (
          <p
            style={{
              color: '#64748b',
            }}
          >
            No upcoming projects yet.
          </p>
        ) : (
          pageItems.map((item) => (
            <article
              key={item.id}
              className="card"
              style={{
                overflow: 'hidden',
              }}
            >
              {item.image_url && (
                <img
                  src={resolveMediaUrl(
                    item.image_url
                  )}
                  alt={item.title}
                  style={{
                    width: '100%',
                    height: 180,
                    objectFit: 'cover',
                  }}
                />
              )}

              <div
                style={{
                  padding: '1rem',
                }}
              >
                <span className="badge badge-green">
                  Upcoming
                </span>

                <h3
                  style={{
                    margin:
                      '.5rem 0',
                  }}
                >
                  {item.title}
                </h3>

                {item.description && (
                  <p
                    style={{
                      color: '#64748b',
                    }}
                  >
                    {item.description}
                  </p>
                )}

                <p
                  style={{
                    color: '#475569',
                  }}
                >
                  {item.expected_date
                    ? new Date(
                        `${item.expected_date}T00:00:00`
                      ).toLocaleDateString(
                        'en-IN'
                      )
                    : 'Date not set'}
                </p>

                <div
                  style={{
                    display: 'flex',
                    gap: '.5rem',
                  }}
                >
                  <button
                    className="btn"
                    onClick={() =>
                      edit(item)
                    }
                  >
                    Edit
                  </button>

                  <button
                    onClick={() =>
                      remove(item.id)
                    }
                    className="btn"
                    style={dangerButton}
                  >
                    <Trash2 size={15} />
                    Delete
                  </button>
                </div>
              </div>
            </article>
          ))
        )}
      </div>

      <Pagination
        page={currentPage}
        totalPages={totalPages}
        onPage={setPage}
      />
    </ManagerSection>
  );
}


// ============================================================
// VISITOR STATS
// ============================================================

function MiniStat({ label, value, sub, icon }) {
  return (
    <div
      className="card"
      style={{
        padding: '1.1rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '.25rem',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '.5rem',
          color: '#64748b',
          fontSize: '.82rem',
          fontWeight: 600,
        }}
      >
        {icon}
        {label}
      </div>

      <strong
        style={{
          fontSize: '1.5rem',
          color: '#0f172a',
          lineHeight: 1.2,
        }}
      >
        {value}
      </strong>

      {sub && (
        <span
          style={{
            color: '#059669',
            fontSize: '.78rem',
            fontWeight: 700,
            whiteSpace: 'nowrap',
          }}
        >
          {sub}
        </span>
      )}
    </div>
  );
}


function VerticalBars({
  data,
  height = 190,
  labelStep = 1,
}) {
  if (!data || data.length === 0) {
    return (
      <p
        style={{
          color: '#64748b',
        }}
      >
        No data yet.
      </p>
    );
  }

  const max = Math.max(
    1,
    ...data.map((d) => d.value)
  );

  const showValue = data.length <= 14;

  return (
    <div>
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-end',
          gap: 4,
          height,
        }}
      >
        {data.map((d, i) => {
          const pct = Math.round(
            (d.value / max) * 100
          );

          return (
            <div
              key={i}
              style={{
                flex: 1,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'flex-end',
                alignItems: 'center',
              }}
              title={`${
                d.tooltip || d.label
              }: ${d.value}`}
            >
              {showValue &&
                d.value > 0 && (
                  <span
                    style={{
                      fontSize: '.62rem',
                      color: '#059669',
                      fontWeight: 800,
                      marginBottom: 3,
                      lineHeight: 1,
                    }}
                  >
                    {d.value}
                  </span>
                )}

              <div
                style={{
                  width: '100%',
                  maxWidth: 38,
                  height: `${pct}%`,
                  minHeight:
                    d.value > 0 ? 3 : 0,
                  borderRadius:
                    '4px 4px 0 0',
                  background:
                    d.value > 0
                      ? 'linear-gradient(180deg, #34d399 0%, #059669 100%)'
                      : 'transparent',
                  boxShadow:
                    d.value > 0
                      ? '0 1px 3px rgba(5,150,105,.25)'
                      : 'none',
                }}
              />
            </div>
          );
        })}
      </div>

      <div
        style={{
          display: 'flex',
          gap: 4,
          marginTop: 5,
        }}
      >
        {data.map((d, i) => {
          const show =
            i % labelStep === 0 ||
            i === data.length - 1;

          return (
            <div
              key={i}
              style={{
                flex: 1,
                textAlign: 'center',
                fontSize: '.62rem',
                color: '#64748b',
                fontWeight: 700,
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {show ? d.label : ''}
            </div>
          );
        })}
      </div>
    </div>
  );
}


function VisitorStats() {
  const [daily, setDaily] =
    useState([]);

  const [monthly, setMonthly] =
    useState([]);

  const [total, setTotal] =
    useState(0);

  const [range, setRange] =
    useState(14);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState('');

  async function load() {
    setLoading(true);

    try {
      const data =
        await fetchAdminVisits(
          range
        );

      setDaily(data.daily || []);
      setMonthly(data.monthly || []);

      setTotal(
        data.total_visitors || 0
      );

      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [range]);

  const label = (value) => {
    const [y, m, d] = value
      .split('-')
      .map(Number);

    return new Date(
      y,
      m - 1,
      d
    ).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const today =
    daily.length > 0
      ? daily[daily.length - 1].count
      : 0;

  const lastWeek = daily
    .slice(-7)
    .reduce((sum, d) => sum + d.count, 0);

  const busiest = daily.reduce(
    (acc, d) =>
      d.count > acc.count
        ? d
        : acc,
    { count: 0, date: null }
  );

  const dailyBars = daily.map(
    (d) => {
      const [y, m, dd] = d.date
        .split('-')
        .map(Number);

      return {
        label: String(dd),
        tooltip: `${dd}/${m}/${y}`,
        value: d.count,
      };
    }
  );

  const monthlyBars = monthly.map(
    (m) => {
      const [y, mm] = m.month
        .split('-')
        .map(Number);

      const dt = new Date(y, mm - 1, 1);

      return {
        label: dt.toLocaleDateString(
          'en-IN',
          { month: 'short' }
        ),
        tooltip: dt.toLocaleDateString(
          'en-IN',
          {
            month: 'long',
            year: 'numeric',
          }
        ),
        value: m.count,
      };
    }
  );

  const dayLabelStep =
    range >= 30
      ? 5
      : range === 14
      ? 2
      : 1;

  const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '.9rem',
  };

  const thStyle = {
    textAlign: 'left',
    padding: '.5rem .75rem',
    borderBottom: '2px solid #e2e8f0',
    color: '#475569',
    fontSize: '.78rem',
    textTransform: 'uppercase',
    letterSpacing: '.03em',
  };

  const tdStyle = {
    padding: '.5rem .75rem',
    borderBottom: '1px solid #f1f5f9',
    color: '#0f172a',
  };

  const scrollStyle = {
    maxHeight: 280,
    overflowY: 'auto',
  };

  return (
    <ManagerSection
      title="Visitor Analytics"
      icon={<Eye size={22} />}
    >
      <ErrorMessage
        message={error}
      />

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent:
            'space-between',
          gap: '.75rem',
          flexWrap: 'wrap',
          marginBottom: '1.25rem',
        }}
      >
        <p
          style={{
            margin: 0,
            color: '#475569',
          }}
        >
          Track how many people visit the
          website, day by day.
        </p>

        <div
          style={{
            display: 'flex',
            gap: '.5rem',
            flexWrap: 'wrap',
          }}
        >
          {[7, 14, 30].map(
            (days) => (
              <button
                key={days}
                className="btn"
                onClick={() =>
                  setRange(days)
                }
                style={{
                  ...outlineButton,
                  background:
                    range === days
                      ? '#059669'
                      : 'transparent',
                  color:
                    range === days
                      ? '#ffffff'
                      : '#059669',
                  borderColor:
                    '#059669',
                }}
              >
                Last {days} days
              </button>
            )
          )}
        </div>
      </div>

      {/* =====================================================
          SUMMARY CARDS
          ===================================================== */}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns:
            'repeat(auto-fit, minmax(170px, 1fr))',
          gap: '1rem',
          marginBottom: '1.5rem',
        }}
      >
        <MiniStat
          label="Visitors Today"
          value={today}
          icon={<Eye size={16} />}
        />

        <MiniStat
          label="This Week"
          value={lastWeek}
          icon={<CalendarDays size={16} />}
        />

        <MiniStat
          label="Total Visitors"
          value={total.toLocaleString(
            'en-IN'
          )}
          icon={<Users size={16} />}
        />

        <MiniStat
          label="Busiest Day"
          value={busiest.count}
          sub={
            busiest.date
              ? label(busiest.date)
              : 'No visits yet'
          }
          icon={<BarChart3 size={16} />}
        />
      </div>

      {/* =====================================================
          CHARTS
          ===================================================== */}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns:
            'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '1.5rem',
        }}
      >
        <div
          className="card"
          style={{
            padding: '1.25rem',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent:
                'space-between',
              gap: '.5rem',
              marginBottom: '.9rem',
            }}
          >
            <h3
              style={{
                margin: 0,
                fontSize: '1.05rem',
              }}
            >
              Daily Visitors
            </h3>

            <span className="badge badge-green">
              Last {range} days
            </span>
          </div>

          {loading ? (
            <p>Loading...</p>
          ) : (
            <VerticalBars
              data={dailyBars}
              height={190}
              labelStep={dayLabelStep}
            />
          )}
        </div>

        <div
          className="card"
          style={{
            padding: '1.25rem',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent:
                'space-between',
              gap: '.5rem',
              marginBottom: '.9rem',
            }}
          >
            <h3
              style={{
                margin: 0,
                fontSize: '1.05rem',
              }}
            >
              Monthly Visitors
            </h3>

            <span className="badge badge-green">
              Trend
            </span>
          </div>

          {loading ? (
            <p>Loading...</p>
          ) : (
            <VerticalBars
              data={monthlyBars}
              height={190}
              labelStep={1}
            />
          )}
        </div>
      </div>

      {/* =====================================================
          DETAIL TABLES
          ===================================================== */}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns:
            'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '1.5rem',
          marginTop: '1.5rem',
        }}
      >
        <div
          className="card"
          style={{
            padding: '1.25rem',
          }}
        >
          <h3
            style={{
              margin: '0 0 .75rem',
              fontSize: '1.05rem',
            }}
          >
            Day-wise Detail
          </h3>

          {loading ? (
            <p>Loading...</p>
          ) : (
            <div style={scrollStyle}>
              <table style={tableStyle}>
                <thead>
                  <tr>
                    <th style={thStyle}>
                      Date
                    </th>
                    <th
                      style={{
                        ...thStyle,
                        textAlign: 'right',
                      }}
                    >
                      Visitors
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {daily
                    .slice()
                    .reverse()
                    .map((item) => (
                      <tr key={item.date}>
                        <td style={tdStyle}>
                          {label(
                            item.date
                          )}
                        </td>
                        <td
                          style={{
                            ...tdStyle,
                            textAlign: 'right',
                            fontWeight: 700,
                          }}
                        >
                          {item.count}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div
          className="card"
          style={{
            padding: '1.25rem',
          }}
        >
          <h3
            style={{
              margin: '0 0 .75rem',
              fontSize: '1.05rem',
            }}
          >
            Month-wise Detail
          </h3>

          {loading ? (
            <p>Loading...</p>
          ) : (
            <div style={scrollStyle}>
              <table style={tableStyle}>
                <thead>
                  <tr>
                    <th style={thStyle}>
                      Month
                    </th>
                    <th
                      style={{
                        ...thStyle,
                        textAlign: 'right',
                      }}
                    >
                      Visitors
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {monthly
                    .slice()
                    .reverse()
                    .map((item) => (
                      <tr key={item.month}>
                        <td style={tdStyle}>
                          {label(
                            `${item.month}-01`
                          )}
                        </td>
                        <td
                          style={{
                            ...tdStyle,
                            textAlign: 'right',
                            fontWeight: 700,
                          }}
                        >
                          {item.count}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </ManagerSection>
  );
}


// ============================================================
// CAUSE MANAGER
// ============================================================

function CauseManager({ refreshAll }) {
  const [items, setItems] =
    useState([]);

  const [form, setForm] =
    useState(emptyCauseForm);

  const [editingId, setEditingId] =
    useState(null);

  const [removeImage, setRemoveImage] =
    useState(false);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState('');

  const [loading, setLoading] =
    useState(true);

  const pageSize = 6;

  const [page, setPage] =
    useState(1);

  const currentPage = Math.min(
    page,
    Math.max(
      1,
      Math.ceil(
        items.length / pageSize
      )
    )
  );

  const totalPages = Math.max(
    1,
    Math.ceil(
      items.length / pageSize
    )
  );

  const pageItems = items.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  async function load() {
    setLoading(true);

    try {
      setItems(
        await fetchAdminCauses()
      );
      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function reset() {
    setForm(emptyCauseForm);
    setEditingId(null);
    setRemoveImage(false);
  }

  function edit(item) {
    setEditingId(item.id);
    setRemoveImage(false);

    setForm({
      title: item.title,
      category: item.category || '',
      shortDescription:
        item.short_description || '',
      fullDescription:
        item.full_description || '',
      targetAmount:
        item.target_amount != null
          ? String(item.target_amount)
          : '',
      file: null,
    });

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  }

  async function submit(e) {
    e.preventDefault();

    setError('');
    setSaving(true);

    try {
      if (editingId) {
        await updateAdminCause(
          editingId,
          {
            ...form,
            removeImage,
          }
        );
      } else {
        await createAdminCause(
          form
        );
      }

      reset();

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  async function remove(id) {
    if (
      !window.confirm(
        'Delete this cause?'
      )
    ) {
      return;
    }

    try {
      await deleteAdminCause(id);

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <ManagerSection
      title="Welfare Causes"
      icon={<HandHeart size={22} />}
    >
      <ErrorMessage
        message={error}
      />

      <form
        onSubmit={submit}
        style={formGridStyle}
      >
        <input
          placeholder="Cause title"
          value={form.title}
          onChange={(e) =>
            setForm({
              ...form,
              title: e.target.value,
            })
          }
          required
          style={inputStyle}
        />

        <input
          placeholder="Category (e.g. Healthcare)"
          value={form.category}
          onChange={(e) =>
            setForm({
              ...form,
              category: e.target.value,
            })
          }
          style={inputStyle}
        />

        <input
          type="number"
          min="0"
          step="0.01"
          placeholder="Target amount (₹)"
          value={form.targetAmount}
          onChange={(e) =>
            setForm({
              ...form,
              targetAmount:
                e.target.value,
            })
          }
          style={inputStyle}
        />

        <textarea
          placeholder="Short description (shown on cards)"
          value={form.shortDescription}
          onChange={(e) =>
            setForm({
              ...form,
              shortDescription:
                e.target.value,
            })
          }
          required
          style={textareaStyle}
        />

        <textarea
          placeholder="Full description (optional)"
          value={form.fullDescription}
          onChange={(e) =>
            setForm({
              ...form,
              fullDescription:
                e.target.value,
            })
          }
          style={textareaStyle}
        />

        <input
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          onChange={(e) =>
            setForm({
              ...form,
              file:
                e.target.files?.[0] ||
                null,
            })
          }
          style={inputStyle}
        />

        {editingId && (
          <label
            style={{
              display: 'flex',
              gap: '.5rem',
              alignItems:
                'center',
            }}
          >
            <input
              type="checkbox"
              checked={removeImage}
              onChange={(e) =>
                setRemoveImage(
                  e.target.checked
                )
              }
            />

            Remove current image
          </label>
        )}

        <div
          style={{
            display: 'flex',
            gap: '.75rem',
            flexWrap: 'wrap',
          }}
        >
          <button
            className="btn"
            disabled={saving}
            style={primaryButton}
          >
            {saving
              ? 'Saving...'
              : editingId
              ? 'Update Cause'
              : 'Add Cause'}
          </button>

          {editingId && (
            <button
              type="button"
              className="btn"
              onClick={reset}
            >
              Cancel
            </button>
          )}
        </div>
      </form>

      <div style={managerGrid}>
        {loading ? (
          <p>Loading...</p>
        ) : items.length === 0 ? (
          <p
            style={{
              color: '#64748b',
            }}
          >
            No causes yet.
          </p>
        ) : (
          pageItems.map((item) => (
            <article
              key={item.id}
              className="card"
              style={{
                overflow: 'hidden',
              }}
            >
              {item.image_url && (
                <img
                  src={resolveMediaUrl(
                    item.image_url
                  )}
                  alt={item.title}
                  style={{
                    width: '100%',
                    height: 180,
                    objectFit: 'cover',
                  }}
                />
              )}

              <div
                style={{
                  padding: '1rem',
                }}
              >
                {item.category && (
                  <span className="badge badge-green">
                    {item.category}
                  </span>
                )}

                <h3
                  style={{
                    margin: '.5rem 0',
                  }}
                >
                  {item.title}
                </h3>

                <p
                  style={{
                    color: '#64748b',
                  }}
                >
                  {item.short_description}
                </p>

                <p
                  style={{
                    color: '#475569',
                  }}
                >
                  ₹{(item.target_amount || 0).toLocaleString('en-IN')} goal
                  {' · '}
                  ₹{(item.raised_amount || 0).toLocaleString('en-IN')} raised
                </p>

                <div
                  style={{
                    display: 'flex',
                    gap: '.5rem',
                  }}
                >
                  <button
                    className="btn"
                    onClick={() =>
                      edit(item)
                    }
                  >
                    Edit
                  </button>

                  <button
                    onClick={() =>
                      remove(item.id)
                    }
                    className="btn"
                    style={dangerButton}
                  >
                    <Trash2 size={15} />
                    Delete
                  </button>
                </div>
              </div>
            </article>
          ))
        )}
      </div>

      <Pagination
        page={currentPage}
        totalPages={totalPages}
        onPage={setPage}
      />
    </ManagerSection>
  );
}


// ============================================================
// TEAM MANAGER
// ============================================================

function TeamManager({
  refreshAll,
}) {
  const [items, setItems] =
    useState([]);

  const pageSize = 12;

  const [page, setPage] =
    useState(1);

  const currentPage = Math.min(
    page,
    Math.max(
      1,
      Math.ceil(
        items.length / pageSize
      )
    )
  );

  const totalPages = Math.max(
    1,
    Math.ceil(
      items.length / pageSize
    )
  );

  const visibleItems = items.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  const [form, setForm] =
    useState({
      name: '',
      role: '',
      team:
        'Education & Skill Development',
      bio: '',
      memberId: '',
      joinedDate: '',
      email: '',
      file: null,
    });

  const [editingId, setEditingId] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState('');

  const teamOptions = [
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

  async function load() {
    setLoading(true);

    try {
      setItems(
        await fetchAdminTeam()
      );

      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function resetForm() {
    setForm({
      name: '',
      role: '',
      team:
        'Education & Skill Development',
      bio: '',
      memberId: '',
      joinedDate: '',
      email: '',
      file: null,
    });

    setEditingId(null);
  }

  async function submit(e) {
    e.preventDefault();

    setError('');

    if (!form.name.trim()) {
      setError(
        'Please enter the team member name.'
      );
      return;
    }

    if (!form.role.trim()) {
      setError(
        'Please enter the team member role.'
      );
      return;
    }

    if (!form.memberId.trim()) {
      setError(
        'Please enter the team member ID.'
      );
      return;
    }

    if (!form.email.trim()) {
      setError(
        'Please enter the team member email.'
      );
      return;
    }

    if (!form.team.trim()) {
      setError(
        'Please select a team.'
      );
      return;
    }

    if (!editingId && !form.file) {
      setError(
        'A profile photo is required for new team members.'
      );
      return;
    }

    setSaving(true);

    try {
      if (editingId) {
        await updateAdminTeamMember(
          editingId,
          {
            ...form,
            removeImage: false,
          }
        );
      } else {
        await createAdminTeamMember(
          form
        );
      }

      resetForm();

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  function startEdit(item) {
    setEditingId(item.id);

    setForm({
      name: item.name || '',
      role: item.role || '',
      team: item.team || 'General',
      bio: item.bio || '',
      memberId: item.member_id || '',
      joinedDate: item.joined_date || '',
      email: item.email || '',
      file: null,
    });

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  }

  async function downloadCard(id, name) {
    try {
      const blob = await fetchAdminTeamCard(id);

      const url = URL.createObjectURL(blob);

      const anchor = document.createElement('a');

      anchor.href = url;

      anchor.download = `${name || 'team-member'}-id-card.jpg`;

      document.body.appendChild(anchor);

      anchor.click();

      document.body.removeChild(anchor);

      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e.message);
    }
  }

  async function emailCard(id) {
    try {
      await sendAdminTeamCard(id);

      alert('Team member ID card emailed successfully.');
    } catch (e) {
      setError(e.message);
    }
  }

  async function remove(id) {
    if (
      !window.confirm(
        'Are you sure you want to remove this team member?'
      )
    ) {
      return;
    }

    try {
      await deleteAdminTeamMember(
        id
      );

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    }
  }

  const groupedItems =
    visibleItems.reduce(
      (groups, item) => {
        const team =
          item.team || 'General';

        if (!groups[team]) {
          groups[team] = [];
        }

        groups[team].push(item);

        return groups;
      },
      {}
    );

  return (
    <ManagerSection
      title="Team Management"
      icon={<Users size={22} />}
    >
      <ErrorMessage
        message={error}
      />

      <div
        style={{
          padding: '1rem',
          marginBottom: '1.5rem',
          borderRadius: 12,
          background: '#f0fdf4',
          border:
            '1px solid #bbf7d0',
          color: '#166534',
          lineHeight: 1.6,
        }}
      >
        Add, edit and remove people who
        should appear on the public
        Our Team page. Name, Member ID,
        role, email and a profile photo
        are all required for each
        member.
      </div>

      <form
        onSubmit={submit}
        style={formGridStyle}
      >
        <input
          placeholder="Team member name"
          value={form.name}
          onChange={(e) =>
            setForm({
              ...form,
              name: e.target.value,
            })
          }
          required
          style={inputStyle}
        />

        <input
          placeholder="Role / designation"
          value={form.role}
          onChange={(e) =>
            setForm({
              ...form,
              role: e.target.value,
            })
          }
          required
          style={inputStyle}
        />

        <select
          value={form.team}
          onChange={(e) =>
            setForm({
              ...form,
              team: e.target.value,
            })
          }
          required
          style={inputStyle}
        >
          {teamOptions.map(
            (team) => (
              <option
                key={team}
                value={team}
              >
                {team}
              </option>
            )
          )}
        </select>

        <textarea
          placeholder="Short bio (optional)"
          value={form.bio}
          onChange={(e) =>
            setForm({
              ...form,
              bio: e.target.value,
            })
          }
          style={textareaStyle}
        />

        <input
          placeholder="Member ID (e.g. PWF-TM-0001, required)"
          value={form.memberId}
          onChange={(e) =>
            setForm({
              ...form,
              memberId: e.target.value,
            })
          }
          required
          style={inputStyle}
        />

        <input
          type="date"
          value={form.joinedDate}
          onChange={(e) =>
            setForm({
              ...form,
              joinedDate: e.target.value,
            })
          }
          style={inputStyle}
        />

        <input
          type="email"
          placeholder="Email (used to send the ID card, required)"
          value={form.email}
          onChange={(e) =>
            setForm({
              ...form,
              email: e.target.value,
            })
          }
          required
          style={inputStyle}
        />

        <input
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          onChange={(e) =>
            setForm({
              ...form,
              file:
                e.target.files?.[0] ||
                null,
            })
          }
          style={inputStyle}
        />

        <button
          className="btn"
          type="submit"
          disabled={saving}
          style={primaryButton}
        >
          <Users size={17} />

          {saving
            ? editingId
              ? 'Saving Member...'
              : 'Adding Member...'
            : editingId
              ? 'Update Team Member'
              : 'Add Team Member'}
        </button>
      </form>

      {loading ? (
        <p>
          Loading team members...
        </p>
      ) : items.length === 0 ? (
        <div
          style={{
            padding: '2rem',
            textAlign: 'center',
            border:
              '1px dashed #cbd5e1',
            borderRadius: 12,
            color: '#64748b',
          }}
        >
          No team members have
          been added yet.
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gap: '2rem',
          }}
        >
          <p
            style={{
              color: '#64748b',
              fontSize: '.9rem',
              margin: 0,
            }}
          >
            Showing{' '}
            {(currentPage - 1) * pageSize + 1}–
            {Math.min(
              currentPage * pageSize,
              items.length
            )}{' '}
            of {items.length} team
            member
            {items.length === 1
              ? ''
              : 's'}
          </p>

          {Object.entries(
            groupedItems
          ).map(
            ([team, teamMembers]) => (
              <div key={team}>
                <div
                  style={{
                    display: 'flex',
                    justifyContent:
                      'space-between',
                    alignItems: 'center',
                    marginBottom: '1rem',
                    paddingBottom: '.6rem',
                    borderBottom:
                      '1px solid #e2e8f0',
                  }}
                >
                  <h3
                    style={{
                      margin: 0,
                      color: '#0f172a',
                    }}
                  >
                    {team}
                  </h3>

                  <span className="badge badge-green">
                    {teamMembers.length}{' '}
                    {teamMembers.length ===
                    1
                      ? 'Member'
                      : 'Members'}
                  </span>
                </div>

                <div
                  style={managerGrid}
                >
                  {teamMembers.map(
                    (member) => (
                      <article
                        key={member.id}
                        className="card"
                        style={{
                          overflow:
                            'hidden',
                        }}
                      >
                        <div
                          style={{
                            display: 'flex',
                            justifyContent:
                              'center',
                            alignItems:
                              'center',
                            height: 190,
                            background:
                              'linear-gradient(135deg, #f0fdf4, #ecfccb)',
                            padding: '1rem',
                          }}
                        >
                          <img
                            src={
                              member.photo_url
                                ? resolveMediaUrl(
                                    member.photo_url
                                  )
                                : '/piplad-logo.jpg'
                            }
                            alt={
                              member.name
                            }
                            style={{
                              width: 140,
                              height: 140,
                              borderRadius:
                                '50%',
                              objectFit:
                                'cover',
                              border:
                                '4px solid #fff',
                              boxShadow:
                                '0 8px 20px rgba(0,0,0,.12)',
                            }}
                          />
                        </div>

                        <div
                          style={{
                            padding: '1rem',
                          }}
                        >
                          <h3
                            style={{
                              margin:
                                '0 0 .35rem',
                            }}
                          >
                            {member.name}
                          </h3>

                          {member.role && (
                            <p
                              style={{
                                margin:
                                  '0 0 .6rem',
                                color:
                                  '#059669',
                                fontWeight:
                                  600,
                                fontSize:
                                  '.9rem',
                              }}
                            >
                              {member.role}
                            </p>
                          )}

                          {member.bio && (
                            <p
                              style={{
                                color:
                                  '#64748b',
                                fontSize:
                                  '.85rem',
                                lineHeight:
                                  1.6,
                              }}
                            >
                              {member.bio}
                            </p>
                          )}

                          <div
                            style={{
                              marginTop:
                                '.6rem',
                              display:
                                'flex',
                              flexDirection:
                                'column',
                              gap: '.35rem',
                              fontSize:
                                '.8rem',
                              color:
                                '#475569',
                            }}
                          >
                            {member.member_id && (
                              <span>
                                <strong>ID:</strong>{' '}
                                {member.member_id}
                              </span>
                            )}

                            {member.joined_date && (
                              <span>
                                <strong>Joined:</strong>{' '}
                                {member.joined_date}
                              </span>
                            )}

                            {member.email && (
                              <span
                                style={{
                                  wordBreak:
                                    'break-all',
                                }}
                              >
                                <strong>Email:</strong>{' '}
                                {member.email}
                              </span>
                            )}
                          </div>

                          <div
                            style={{
                              display: 'flex',
                              flexWrap: 'wrap',
                              gap: '.5rem',
                              marginTop:
                                '.75rem',
                            }}
                          >
                            <button
                              type="button"
                              onClick={() =>
                                startEdit(
                                  member
                                )
                              }
                              className="btn"
                              style={{
                                ...outlineButton,
                              }}
                            >
                              <Edit3
                                size={15}
                              />
                              Edit
                            </button>

                            <button
                              type="button"
                              onClick={() =>
                                downloadCard(
                                  member.id,
                                  member.name
                                )
                              }
                              className="btn"
                              style={{
                                ...outlineButton,
                              }}
                            >
                              <Eye
                                size={15}
                              />
                              ID Card
                            </button>

                            <button
                              type="button"
                              onClick={() =>
                                emailCard(
                                  member.id
                                )
                              }
                              className="btn"
                              style={{
                                ...outlineButton,
                              }}
                            >
                              <Mail
                                size={15}
                              />
                              Email Card
                            </button>

                            <button
                              type="button"
                              onClick={() =>
                                remove(
                                  member.id
                                )
                              }
                              className="btn"
                              style={{
                                ...dangerButton,
                              }}
                            >
                              <Trash2
                                size={15}
                              />
                              Remove
                            </button>
                          </div>
                        </div>
                      </article>
                    )
                  )}
                </div>
              </div>
            )
          )}

          <Pagination
            page={currentPage}
            totalPages={totalPages}
            onPage={setPage}
          />
        </div>
      )}
    </ManagerSection>
  );
}


// ============================================================
// CERTIFICATE MANAGER
// ============================================================

function CertificateManager({ refreshAll }) {
  const [items, setItems] = useState([]);

  const [form, setForm] = useState(emptyCertificateForm);

  const [editingId, setEditingId] = useState(null);

  const [removeImage, setRemoveImage] = useState(false);

  const [saving, setSaving] = useState(false);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState('');

  const pageSize = 9;

  const [page, setPage] = useState(1);

  const currentPage = Math.min(
    page,
    Math.max(
      1,
      Math.ceil(
        items.length / pageSize
      )
    )
  );

  const totalPages = Math.max(
    1,
    Math.ceil(
      items.length / pageSize
    )
  );

  const pageItems = items.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  async function load() {
    setLoading(true);

    try {
      setItems(
        await fetchAdminCertificates()
      );

      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function reset() {
    setForm(emptyCertificateForm);
    setEditingId(null);
    setRemoveImage(false);
  }

  function edit(item) {
    setEditingId(item.id);

    setRemoveImage(false);

    setForm({
      title: item.title,
      description: item.description || '',
      file: null,
    });

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  }

  async function submit(e) {
    e.preventDefault();

    setError('');

    if (!form.title.trim()) {
      setError('Please enter a certificate title.');
      return;
    }

    setSaving(true);

    try {
      if (editingId) {
        await updateAdminCertificate(
          editingId,
          {
            ...form,
            removeImage,
          }
        );
      } else {
        await createAdminCertificate(form);
      }

      reset();

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  async function remove(id) {
    if (
      !window.confirm(
        'Delete this certificate?'
      )
    ) {
      return;
    }

    try {
      await deleteAdminCertificate(id);

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <ManagerSection
      title="Certificates"
      icon={<Award size={22} />}
    >
      <ErrorMessage
        message={error}
      />

      <form
        onSubmit={submit}
        style={formGridStyle}
      >
        <input
          placeholder="Certificate title"
          value={form.title}
          onChange={(e) =>
            setForm({
              ...form,
              title: e.target.value,
            })
          }
          required
          style={inputStyle}
        />

        <textarea
          placeholder="Description (optional)"
          value={form.description}
          onChange={(e) =>
            setForm({
              ...form,
              description: e.target.value,
            })
          }
          style={textareaStyle}
        />

        <input
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          onChange={(e) =>
            setForm({
              ...form,
              file: e.target.files?.[0] || null,
            })
          }
          style={inputStyle}
        />

        {editingId && (
          <label
            style={{
              display: 'flex',
              gap: '.5rem',
              alignItems: 'center',
            }}
          >
            <input
              type="checkbox"
              checked={removeImage}
              onChange={(e) =>
                setRemoveImage(e.target.checked)
              }
            />

            Remove current image
          </label>
        )}

        <div
          style={{
            display: 'flex',
            gap: '.75rem',
            flexWrap: 'wrap',
          }}
        >
          <button
            className="btn"
            disabled={saving}
            style={primaryButton}
          >
            <Upload size={17} />

            {saving
              ? 'Saving...'
              : editingId
              ? 'Update Certificate'
              : 'Add Certificate'}
          </button>

          {editingId && (
            <button
              type="button"
              className="btn"
              onClick={reset}
            >
              Cancel
            </button>
          )}
        </div>
      </form>

      <div style={managerGrid}>
        {loading ? (
          <p>Loading...</p>
        ) : items.length === 0 ? (
          <p style={{ color: '#64748b' }}>
            No certificates added yet.
          </p>
        ) : (
          pageItems.map((item) => (
            <article
              key={item.id}
              className="card"
              style={{ overflow: 'hidden' }}
            >
              {item.image_url ? (
                <img
                  src={resolveMediaUrl(item.image_url)}
                  alt={item.title}
                  style={{
                    width: '100%',
                    height: 180,
                    objectFit: 'cover',
                  }}
                />
              ) : (
                <div
                  style={{
                    height: 180,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: '#f1f5f9',
                  }}
                >
                  <Award size={40} color="#94a3b8" />
                </div>
              )}

              <div style={{ padding: '1rem' }}>
                <h3 style={{ margin: '0 0 .4rem' }}>
                  {item.title}
                </h3>

                {item.description && (
                  <p style={{ color: '#64748b' }}>
                    {item.description}
                  </p>
                )}

                <div
                  style={{
                    display: 'flex',
                    gap: '.5rem',
                    marginTop: '.75rem',
                  }}
                >
                  <button
                    className="btn"
                    onClick={() => edit(item)}
                  >
                    <Edit3 size={15} />
                    Edit
                  </button>

                  <button
                    onClick={() => remove(item.id)}
                    className="btn"
                    style={dangerButton}
                  >
                    <Trash2 size={15} />
                    Delete
                  </button>
                </div>
              </div>
            </article>
          ))
        )}
      </div>

      <Pagination
        page={currentPage}
        totalPages={totalPages}
        onPage={setPage}
      />
    </ManagerSection>
  );
}


// ============================================================
// IMPACT METRICS MANAGER
// ============================================================

const categoryLabels = {
  people: 'People Impact',
  environmental: 'Environmental Impact',
  carbon: 'Verified Carbon Credits',
};

function ImpactManager() {
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  async function load() {
    setLoading(true);

    try {
      setMetrics(await fetchAdminImpact());
      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function updateMetric(index, patch) {
    setMetrics((current) =>
      current.map((metric, i) =>
        i === index ? { ...metric, ...patch } : metric
      )
    );
  }

  async function save(e) {
    e.preventDefault();

    setError('');
    setSaving(true);

    try {
      const payload = metrics.map((metric) => ({
        value: Number(metric.value) || 0,
        is_published: Boolean(metric.is_published),
      }));

      setMetrics(await updateAdminImpact(payload));
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  const grouped = metrics.reduce((acc, metric) => {
    const key = metric.category || 'people';
    acc[key] = acc[key] || [];
    acc[key].push(metric);
    return acc;
  }, {});

  return (
    <ManagerSection
      title="Impact Metrics"
      icon={<BarChart3 size={22} />}
    >
      <ErrorMessage message={error} />

      <p style={{ color: '#64748b', lineHeight: 1.7, marginTop: 0 }}>
        These figures appear on the public Impact page and the
        "Impact at a Glance" section of the homepage. Change a value
        and save — the website updates automatically. Carbon credits
        should stay at 0 until formally verified.
      </p>

      {loading ? (
        <p>Loading impact metrics…</p>
      ) : metrics.length === 0 ? (
        <p style={{ color: '#64748b' }}>
          No impact metrics found.
        </p>
      ) : (
        <form onSubmit={save}>
          {Object.entries(grouped).map(([category, items]) => (
            <div
              key={category}
              style={{
                marginBottom: '1.5rem',
                padding: '1.25rem',
                border: '1px solid #e2e8f0',
                borderRadius: 12,
                background: '#f8fafc',
              }}
            >
              <h3
                style={{
                  margin: '0 0 1rem',
                  fontSize: '1rem',
                  color: '#0f172a',
                }}
              >
                {categoryLabels[category] || category}
              </h3>

              <div
                style={{
                  display: 'grid',
                  gap: '1rem',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                }}
              >
                {items.map((metric) => {
                  const idx = metrics.indexOf(metric);

                  return (
                    <div
                      key={metric.id}
                      style={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '.5rem',
                        padding: '1rem',
                        background: '#fff',
                        border: '1px solid #e2e8f0',
                        borderRadius: 10,
                      }}
                    >
                      <label style={{ fontWeight: 700, fontSize: '.88rem' }}>
                        {metric.metric_name}
                      </label>

                      {metric.description && (
                        <small style={{ color: '#64748b', lineHeight: 1.5 }}>
                          {metric.description}
                        </small>
                      )}

                      <div style={{ display: 'flex', gap: '.5rem', alignItems: 'center' }}>
                        <input
                          type="number"
                          min="0"
                          step="any"
                          value={metric.value}
                          onChange={(e) =>
                            updateMetric(idx, {
                              value: e.target.value,
                            })
                          }
                          style={{ ...inputStyle, flex: 1 }}
                        />
                        {metric.unit && (
                          <span
                            style={{
                              color: '#64748b',
                              fontSize: '.82rem',
                              fontWeight: 700,
                              whiteSpace: 'nowrap',
                            }}
                          >
                            {metric.unit}
                          </span>
                        )}
                      </div>

                      <label
                        style={{
                          display: 'inline-flex',
                          gap: '.5rem',
                          alignItems: 'center',
                          fontSize: '.85rem',
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={Boolean(metric.is_published)}
                          onChange={(e) =>
                            updateMetric(idx, {
                              is_published: e.target.checked,
                            })
                          }
                        />
                        {metric.is_published
                          ? <><Eye size={15} /> Published</>
                          : <><EyeOff size={15} /> Hidden</>}
                      </label>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}

          <div
            style={{
              display: 'flex',
              gap: '.75rem',
              alignItems: 'center',
              flexWrap: 'wrap',
            }}
          >
            <button
              className="btn"
              disabled={saving}
              style={primaryButton}
            >
              <Upload size={17} />
              {saving ? 'Saving…' : 'Save Changes'}
            </button>

            {metrics.length > 0 && (
              <span style={{ color: '#64748b', fontSize: '.85rem' }}>
                Last updated:{' '}
                {metrics
                  .map((m) => m.last_updated)
                  .filter(Boolean)
                  .sort()
                  .slice(-1)[0]
                  ? new Date(
                      metrics
                        .map((m) => m.last_updated)
                        .filter(Boolean)
                        .sort()
                        .slice(-1)[0]
                    ).toLocaleDateString('en-IN', {
                      day: 'numeric',
                      month: 'short',
                      year: 'numeric',
                    })
                  : 'Never'}
              </span>
            )}
          </div>
        </form>
      )}
    </ManagerSection>
  );
}


// ============================================================
// MAIN ADMIN PAGE
// ============================================================

export default function Admin() {
  const [
    authenticated,
    setAuthenticated,
  ] = useState(
    Boolean(
      getAdminCredentials()
    )
  );

  const [tab, setTab] =
    useState('dashboard');

  const [stats, setStats] =
    useState(null);

  const [donations, setDonations] =
    useState([]);

  const [donationPage, setDonationPage] =
    useState(1);

  const [inquiryPage, setInquiryPage] =
    useState(1);

  const [inquiries, setInquiries] =
    useState([]);

  const [error, setError] =
    useState('');

  async function loadDashboard() {
    try {
      const [
        s,
        d,
        i,
      ] = await Promise.all([
        fetchAdminStats(),
        fetchDonationsList(),
        fetchContactInquiries(),
      ]);

      setStats(s);
      setDonations(d);
      setInquiries(i);
      setError('');
    } catch (e) {
      if (
        e.code ===
        'ADMIN_AUTH_REQUIRED'
      ) {
        setAuthenticated(false);
        return;
      }

      setError(e.message);
    }
  }

  useEffect(() => {
    if (authenticated) {
      loadDashboard();
    }
  }, [authenticated]);

  async function deleteInquiry(id) {
    if (
      !window.confirm(
        'Delete this contact inquiry?'
      )
    ) {
      return;
    }

    try {
      await deleteContactInquiry(id);

      setInquiries((current) =>
        current.filter((item) => item.id !== id)
      );
    } catch (e) {
      setError(e.message);
    }
  }

  if (!authenticated) {
    return (
      <AdminLogin
        onLogin={() =>
          setAuthenticated(true)
        }
      />
    );
  }

  function logout() {
    clearAdminCredentials();
    setAuthenticated(false);
  }

  const tabs = [
    [
      'dashboard',
      'Dashboard',
      LayoutDashboard,
    ],
    [
      'home',
      'Home Page',
      Home,
    ],
    [
      'visitors',
      'Visitors',
      Eye,
    ],
    [
      'donations',
      'Donations',
      Heart,
    ],
    [
      'volunteers',
      'Volunteers',
      Users,
    ],
    [
      'gallery',
      'Photos',
      ImageIcon,
    ],
    [
      'videos',
      'Videos',
      Video,
    ],
    [
      'projects',
      'Upcoming Projects',
      CalendarDays,
    ],
    [
      'causes',
      'Causes',
      HandHeart,
    ],
    [
      'team',
      'Team Members',
      UserCheck,
    ],
    [
      'founder',
      'Founder & Mentors',
      UserCheck,
    ],
    [
      'certificates',
      'Certificates',
      Award,
    ],
    [
      'cert-mgmt',
      'Cert. Management',
      BadgeCheck,
    ],
    [
      'cert-history',
      'Cert. History',
      History,
    ],
    [
      'footer',
      'Footer',
      Target,
    ],
    [
      'impact',
      'Impact Metrics',
      BarChart3,
    ],
    [
      'settings',
      'Site Settings',
      Settings,
    ],
  ];

  return (
    <div>
      {/* =====================================================
          HEADER
          ===================================================== */}

      <section
        style={{
          background: '#0f172a',
          color: '#fff',
          padding:
            '3rem 0 2rem',
        }}
      >
        <div
          className="container"
          style={{
            display: 'flex',
            justifyContent:
              'space-between',
            gap: '1rem',
            alignItems:
              'center',
            flexWrap: 'wrap',
          }}
        >
          <div>
            <span className="badge badge-green">
              <ShieldCheck
                size={16}
              />
              Admin
            </span>

            <h1
              style={{
                color: '#fff',
                margin:
                  '.6rem 0 0',
              }}
            >
              Piplad Management
            </h1>
          </div>

          <div className="admin-actions">
            <button
              className="btn admin-action-btn admin-refresh-btn"
              onClick={
                loadDashboard
              }
            >
              <RefreshCw
                size={16}
              />
              Refresh
            </button>

            <button
              className="btn admin-action-btn admin-logout-btn"
              onClick={logout}
            >
              <LogOut size={16} />
              Logout
            </button>
          </div>
        </div>
      </section>

      {/* =====================================================
          CONTENT
          ===================================================== */}

      <section
        className="section-padding"
        style={{
          background: '#f8fafc',
        }}
      >
        <div
          className="container"
          style={{
            display: 'flex',
            gap: '1.5rem',
            alignItems: 'flex-start',
            flexWrap: 'wrap',
          }}
        >
          {/* TABS */}

          <div
            className="admin-sidebar"
            style={{
              width: 250,
              flexShrink: 0,
            }}
          >
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '.45rem',
                position: 'sticky',
                top: '1rem',
              }}
            >
              <span className="admin-nav-label">
                Manage
              </span>

              {tabs.map(
                ([id, label, Icon]) => (
                  <button
                    key={id}
                    className={
                      tab === id
                        ? 'btn admin-nav-btn active'
                        : 'btn admin-nav-btn'
                    }
                    onClick={() =>
                      setTab(id)
                    }
                  >
                    <Icon
                      size={17}
                      className="admin-nav-icon"
                    />
                    <span>{label}</span>
                    {tab === id && (
                      <ChevronRight
                        size={16}
                        className="admin-nav-chevron"
                      />
                    )}
</button>
              )
            )}
            </div>
          </div>

          <div
            style={{
              flex: 1,
              minWidth: 0,
            }}
          >
            <ErrorMessage
              message={error}
            />

          {/* =================================================
              DASHBOARD
              ================================================= */}

          {tab ===
            'dashboard' && (
            <>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns:
                    'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '1rem',
                  marginBottom:
                    '2rem',
                }}
              >
                <Stat
                  icon={
                    <DollarSign />
                  }
                  label="Total Raised"
                  value={`₹${Number(
                    stats?.total_donations ||
                      0
                  ).toLocaleString(
                    'en-IN'
                  )}`}
                />

                <Stat
                  icon={
                    <Users />
                  }
                  label="Total Donors"
                  value={
                    stats?.total_donors ||
                    0
                  }
                />

                <Stat
                  icon={
                    <Heart />
                  }
                  label="Active Causes"
                  value={
                    stats?.active_causes ||
                    0
                  }
                />

                <Stat
                  icon={
                    <MessageSquare />
                  }
                  label="Contact Inquiries"
                  value={
                    stats?.inquiries_count ||
                    0
                  }
                />

                <Stat
                  icon={
                    <Eye />
                  }
                  label="Visitors Today"
                  value={
                    stats?.visitors_today ||
                    0
                  }
                />

                <Stat
                  icon={
                    <CalendarDays />
                  }
                  label="Visitors This Week"
                  value={
                    stats?.visitors_this_week ||
                    0
                  }
                />

                <Stat
                  icon={
                    <BarChart3 />
                  }
                  label="Total Visitors"
                  value={
                    stats?.total_visitors ||
                    0
                  }
                />
              </div>

              <div
                className="card"
                style={{
                  padding: '1.5rem',
                }}
              >
                <h2>
                  Content Management
                </h2>

                <p
                  style={{
                    color: '#64748b',
                    lineHeight: 1.7,
                  }}
                >
                  Use Photos, Videos,
                  Upcoming Projects,
                  Team Members and
                  Volunteers to manage
                  the corresponding
                  sections of the
                  website.
                </p>
              </div>
            </>
          )}

          {/* =================================================
              MANAGERS
              ================================================= */}

          {tab === 'gallery' && (
            <GalleryManager
              refreshAll={
                loadDashboard
              }
            />
          )}

          {tab === 'volunteers' && (
            <VolunteerManager />
          )}

          {tab === 'donations' && (
            <DonationManager />
          )}

          {tab === 'visitors' && (
            <VisitorStats />
          )}

          {tab === 'home' && (
            <HomeHeroManager />
          )}

          {tab === 'videos' && (
            <VideoManager
              refreshAll={
                loadDashboard
              }
            />
          )}

          {tab === 'projects' && (
            <ProjectManager
              refreshAll={
                loadDashboard
              }
            />
          )}

          {tab === 'causes' && (
            <CauseManager
              refreshAll={
                loadDashboard
              }
            />
          )}

          {tab === 'team' && (
            <TeamManager
              refreshAll={
                loadDashboard
              }
            />
          )}

          {tab === 'founder' && (
            <FounderMentorsManager
              refreshAll={
                loadDashboard
              }
            />
          )}

          {tab === 'certificates' && (
            <CertificateManager
              refreshAll={
                loadDashboard
              }
            />
          )}

          {tab === 'cert-mgmt' && (
            <CertificateManagement />
          )}

          {tab === 'cert-history' && (
            <CertificateHistory />
          )}

          {tab === 'footer' && (
            <FooterManager />
          )}

          {tab === 'impact' && (
            <ImpactManager />
          )}

          {tab === 'settings' && (
            <SiteSettingsManager />
          )}

          {/* =================================================
              RECENT DONATIONS / INQUIRIES
              ================================================= */}

          {tab ===
            'dashboard' && (
            <div
              style={{
                marginTop: '2rem',
              }}
            >
              <div
                className="card"
                style={{
                  overflowX:
                    'auto',
                  marginBottom:
                    '2rem',
                }}
              >
                <h2
                  style={{
                    padding:
                      '0 1rem',
                  }}
                >
                  Recent Donations
                </h2>

                <table
                  style={
                    tableStyle
                  }
                >
                  <thead>
                    <tr>
                      <th
                        style={th}
                      >
                        Donor
                      </th>

                      <th
                        style={th}
                      >
                        Amount
                      </th>

                      <th
                        style={th}
                      >
                        Status
                      </th>

                      <th
                        style={th}
                      >
                        Date
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {donations
                      .slice(
                        (donationPage - 1) * 5,
                        donationPage * 5
                      )
                      .map(
                        (d) => (
                          <tr
                            key={
                              d.id
                            }
                          >
                            <td
                              style={
                                td
                              }
                            >
                              {
                                d.donor_name
                              }
                            </td>

                            <td
                              style={
                                td
                              }
                            >
                              ₹
                              {Number(
                                d.amount
                              ).toLocaleString(
                                'en-IN'
                              )}
                            </td>

                            <td
                              style={
                                td
                              }
                            >
                              {
                                d.status
                              }
                            </td>

                            <td
                              style={
                                td
                              }
                            >
                              {new Date(
                                d.created_at
                              ).toLocaleDateString()}
                            </td>
                          </tr>
                        )
                      )}

                    {donations.length ===
                      0 && (
                      <tr>
                        <td
                          colSpan="4"
                          style={
                            td
                          }
                        >
                          No donation
                          records.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>

                {donations.length >
                  5 && (
                  <div
                    style={{
                      display:
                        'flex',
                      alignItems:
                        'center',
                      justifyContent:
                        'center',
                      gap: '.75rem',
                      padding:
                        '0.75rem 1rem',
                      flexWrap:
                        'wrap',
                    }}
                  >
                    <button
                      className="btn"
                      disabled={
                        donationPage <=
                        1
                      }
                      onClick={() =>
                        setDonationPage(
                          (p) =>
                            Math.max(
                              1,
                              p - 1
                            )
                        )
                      }
                      style={
                        outlineButton
                      }
                    >
                      Previous
                    </button>

                    <span
                      style={{
                        color: '#475569',
                        fontSize:
                          '.9rem',
                      }}
                    >
                      Page{' '}
                      {donationPage} of{' '}
                      {Math.max(
                        1,
                        Math.ceil(
                          donations.length /
                            5
                        )
                      )}
                    </span>

                    <button
                      className="btn"
                      disabled={
                        donationPage >=
                        Math.ceil(
                          donations.length /
                            5
                        )
                      }
                      onClick={() =>
                        setDonationPage(
                          (p) => p + 1
                        )
                      }
                      style={
                        outlineButton
                      }
                    >
                      Next
                    </button>
                  </div>
                )}
              </div>

              <div
                className="card"
                style={{
                  overflowX:
                    'auto',
                }}
              >
                <h2
                  style={{
                    padding:
                      '0 1rem',
                  }}
                >
                  Recent Inquiries
                </h2>

                <table
                  style={
                    tableStyle
                  }
                >
                  <thead>
                    <tr>
                      <th
                        style={th}
                      >
                        Name
                      </th>

                      <th
                        style={th}
                      >
                        Email
                      </th>

                      <th
                        style={th}
                      >
                        Phone
                      </th>

                      <th
                        style={th}
                      >
                        Subject
                      </th>

                      <th
                        style={th}
                      >
                        Message
                      </th>

                      <th
                        style={th}
                      >
                        Date
                      </th>

                      <th
                        style={th}
                      >
                        Actions
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {inquiries
                      .slice(
                        (inquiryPage - 1) * 8,
                        inquiryPage * 8
                      )
                      .map(
                        (i) => (
                          <tr
                            key={
                              i.id
                            }
                          >
                            <td
                              style={
                                td
                              }
                            >
                              {i.name}
                            </td>

                            <td
                              style={
                                td
                              }
                            >
                              {i.email}
                            </td>

                            <td
                              style={
                                td
                              }
                            >
                              {i.phone ||
                                '—'}
                            </td>

                            <td
                              style={
                                td
                              }
                            >
                              {i.subject ||
                                'General'}
                            </td>

                            <td
                              style={{
                                ...td,
                                minWidth: 220,
                              }}
                            >
                              {i.message}
                            </td>

                            <td
                              style={
                                td
                              }
                            >
                              {new Date(
                                i.created_at
                              ).toLocaleString()}
                            </td>

                            <td
                              style={td}
                            >
                              <button
                                onClick={() =>
                                  deleteInquiry(
                                    i.id
                                  )
                                }
                                className="btn"
                                style={dangerButton}
                              >
                                <Trash2
                                  size={15}
                                />
                                Delete
                              </button>
                            </td>
                          </tr>
                        )
                      )}

                    {inquiries.length ===
                      0 && (
                      <tr>
                        <td
                          colSpan="7"
                          style={
                            td
                          }
                        >
                          No inquiries.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>

                {inquiries.length >
                  8 && (
                  <Pagination
                    page={Math.min(
                      inquiryPage,
                      Math.max(
                        1,
                        Math.ceil(
                          inquiries.length /
                            8
                        )
                      )
                    )}
                    totalPages={Math.max(
                      1,
                      Math.ceil(
                        inquiries.length /
                          8
                      )
                    )}
                    onPage={
                      setInquiryPage
                    }
                  />
                )}
              </div>
            </div>
          )}

          </div>
        </div>
      </section>
    </div>
  );
}


// ============================================================
// STATS
// ============================================================

function Stat({
  icon,
  label,
  value,
}) {
  return (
    <div
      className="card"
      style={{
        padding: '1.25rem',
        display: 'flex',
        gap: '.8rem',
        alignItems: 'center',
      }}
    >
      {React.cloneElement(
        icon,
        {
          size: 22,
          color: '#059669',
        }
      )}

      <div>
        <div
          style={{
            color: '#64748b',
            fontSize: '.85rem',
          }}
        >
          {label}
        </div>

        <strong
          style={{
            fontSize: '1.35rem',
            color: '#0f172a',
          }}
        >
          {value}
        </strong>
      </div>
    </div>
  );
}


// ============================================================
// PAGINATION
// ============================================================

function Pagination({
  page,
  totalPages,
  onPage,
}) {
  if (totalPages <= 1) {
    return null;
  }

  const start = Math.max(
    1,
    page - 2
  );

  const end = Math.min(
    totalPages,
    page + 2
  );

  const pages = [];

  for (
    let i = start;
    i <= end;
    i++
  ) {
    pages.push(i);
  }

  const pagerStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '.5rem',
    flexWrap: 'wrap',
    marginTop: '1.5rem',
  };

  const dotsStyle = {
    color: '#64748b',
    padding: '0 .15rem',
  };

  return (
    <nav style={pagerStyle}>
      <button
        className="btn"
        disabled={page <= 1}
        onClick={() =>
          onPage(page - 1)
        }
        style={outlineButton}
      >
        Previous
      </button>

      {start > 2 && (
        <button
          className="btn"
          onClick={() => onPage(1)}
          style={outlineButton}
        >
          1
        </button>
      )}

      {start > 2 && (
        <span style={dotsStyle}>…</span>
      )}

      {pages.map((n) => (
        <button
          key={n}
          className="btn"
          onClick={() => onPage(n)}
          style={
            n === page
              ? primaryButton
              : outlineButton
          }
        >
          {n}
        </button>
      ))}

      {end < totalPages - 1 && (
        <span style={dotsStyle}>…</span>
      )}

      {end < totalPages && (
        <button
          className="btn"
          onClick={() =>
            onPage(totalPages)
          }
          style={outlineButton}
        >
          {totalPages}
        </button>
      )}

      <button
        className="btn"
        disabled={
          page >= totalPages
        }
        onClick={() =>
          onPage(page + 1)
        }
        style={outlineButton}
      >
        Next
      </button>
    </nav>
  );
}


// ============================================================
// FOUNDER & MENTORS MANAGER
// ============================================================

function FounderMentorsManager({ refreshAll }) {
  const [founder, setFounder] =
    useState(null);

  const [founderForm, setFounderForm] =
    useState({
      name: '',
      role: '',
      eyebrow: '',
      title: '',
      imageAlt: '',
      introduction: '',
      story: '',
      vision: '',
      quote: '',
      milestones: [],
      file: null,
      removeImage: false,
    });

  const [mentors, setMentors] =
    useState([]);

  const [mentorForm, setMentorForm] =
    useState({
      name: '',
      role: '',
      description: '',
      quote: '',
      displayOrder: 0,
      isPublished: true,
      file: null,
      removeImage: false,
    });

  const [editingMentorId, setEditingMentorId] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState('');

  async function load() {
    setLoading(true);

    try {
      const [founderData, mentorData] =
        await Promise.all([
          fetchAdminFounder(),
          fetchAdminMentors(),
        ]);

      setFounder(founderData);
      setFounderForm({
        name: founderData.name || '',
        role: founderData.role || '',
        eyebrow: founderData.eyebrow || '',
        title: founderData.title || '',
        imageAlt: founderData.imageAlt || '',
        introduction: founderData.introduction || '',
        story: founderData.story || '',
        vision: founderData.vision || '',
        quote: founderData.quote || '',
        milestones: (founderData.milestones || []).map((m) => ({
          year: m.year || '',
          title: m.title || '',
          description: m.description || '',
        })),
        file: null,
        removeImage: false,
      });

      setMentors(Array.isArray(mentorData) ? mentorData : []);

      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function updateFounderField(field, value) {
    setFounderForm({
      ...founderForm,
      [field]: value,
    });
  }

  function updateMilestone(index, field, value) {
    const next = founderForm.milestones.map((m, i) =>
      i === index ? { ...m, [field]: value } : m
    );

    updateFounderField('milestones', next);
  }

  function addMilestone() {
    const next = [
      ...founderForm.milestones,
      { year: '', title: '', description: '' },
    ];

    updateFounderField('milestones', next);
  }

  function removeMilestone(index) {
    const next = founderForm.milestones.filter(
      (_, i) => i !== index
    );

    updateFounderField('milestones', next);
  }

  async function saveFounder(e) {
    e.preventDefault();

    setError('');
    setSaving(true);

    try {
      await updateAdminFounder(founderForm);

      await load();

      refreshAll();

      alert('Founder profile saved.');
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  function resetMentorForm() {
    setEditingMentorId(null);

    setMentorForm({
      name: '',
      role: '',
      description: '',
      quote: '',
      displayOrder: 0,
      isPublished: true,
      file: null,
      removeImage: false,
    });
  }

  function startEditMentor(item) {
    setEditingMentorId(item.id);

    setMentorForm({
      name: item.name || '',
      role: item.role || '',
      description: item.description || '',
      quote: item.quote || '',
      displayOrder: item.display_order || 0,
      isPublished: item.is_published !== false,
      file: null,
      removeImage: false,
    });

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  }

  async function saveMentor(e) {
    e.preventDefault();

    setError('');

    if (!mentorForm.name.trim()) {
      setError('Please enter the mentor name.');
      return;
    }

    setSaving(true);

    try {
      if (editingMentorId) {
        await updateAdminMentor(
          editingMentorId,
          mentorForm
        );
      } else {
        await createAdminMentor(mentorForm);
      }

      resetMentorForm();

      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function removeMentor(id) {
    if (!window.confirm('Remove this mentor?')) {
      return;
    }

    try {
      await deleteAdminMentor(id);

      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  if (loading) {
    return (
      <ManagerSection
        title="Founder & Mentors"
        icon={<UserCheck size={22} />}
      >
        <p>Loading founder profile and mentors...</p>
      </ManagerSection>
    );
  }

  return (
    <ManagerSection
      title="Founder & Mentors"
      icon={<UserCheck size={22} />}
    >
      <ErrorMessage message={error} />

      <div
        className="card"
        style={{
          padding: '1.5rem',
          marginBottom: '2rem',
        }}
      >
        <h2>Founder Profile</h2>

        <p
          style={{
            color: '#64748b',
            marginBottom: '1.25rem',
          }}
        >
          These fields drive the “Founder" section of the public About page.
        </p>

        <form
          onSubmit={saveFounder}
          style={formGridStyle}
        >
          <input
            placeholder="Founder name"
            value={founderForm.name}
            onChange={(e) =>
              updateFounderField('name', e.target.value)
            }
            style={inputStyle}
            required
          />

          <input
            placeholder="Role (e.g. Founder)"
            value={founderForm.role}
            onChange={(e) =>
              updateFounderField('role', e.target.value)
            }
            style={inputStyle}
          />

          <input
            placeholder="Eyebrow (e.g. Our Founder's Vision)"
            value={founderForm.eyebrow}
            onChange={(e) =>
              updateFounderField('eyebrow', e.target.value)
            }
            style={inputStyle}
          />

          <input
            placeholder="Title"
            value={founderForm.title}
            onChange={(e) =>
              updateFounderField('title', e.target.value)
            }
            style={inputStyle}
          />

          <input
            placeholder="Image alt text"
            value={founderForm.imageAlt}
            onChange={(e) =>
              updateFounderField('imageAlt', e.target.value)
            }
            style={inputStyle}
          />

          <textarea
            placeholder="Introduction"
            value={founderForm.introduction}
            onChange={(e) =>
              updateFounderField('introduction', e.target.value)
            }
            style={textareaStyle}
          />

          <textarea
            placeholder="Story"
            value={founderForm.story}
            onChange={(e) =>
              updateFounderField('story', e.target.value)
            }
            style={textareaStyle}
          />

          <textarea
            placeholder="Vision"
            value={founderForm.vision}
            onChange={(e) =>
              updateFounderField('vision', e.target.value)
            }
            style={textareaStyle}
          />

          <textarea
            placeholder="Quote"
            value={founderForm.quote}
            onChange={(e) =>
              updateFounderField('quote', e.target.value)
            }
            style={textareaStyle}
          />

          <div style={{ marginTop: '.5rem' }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '.75rem',
              }}
            >
              <strong>Milestones</strong>

              <button
                type="button"
                className="btn"
                onClick={addMilestone}
                style={outlineButton}
              >
                + Add Milestone
              </button>
            </div>

            {founderForm.milestones.length === 0 ? (
              <p style={{ color: '#64748b' }}>
                No milestones yet.
              </p>
            ) : (
              founderForm.milestones.map((item, index) => (
                <div
                  key={index}
                  style={{
                    display: 'grid',
                    gridTemplateColumns:
                      '80px 1fr 1fr auto',
                    gap: '.5rem',
                    marginBottom: '.5rem',
                    alignItems: 'start',
                  }}
                >
                  <input
                    placeholder="Year"
                    value={item.year}
                    onChange={(e) =>
                      updateMilestone(index, 'year', e.target.value)
                    }
                    style={inputStyle}
                  />

                  <input
                    placeholder="Title"
                    value={item.title}
                    onChange={(e) =>
                      updateMilestone(index, 'title', e.target.value)
                    }
                    style={inputStyle}
                  />

                  <input
                    placeholder="Description"
                    value={item.description}
                    onChange={(e) =>
                      updateMilestone(index, 'description', e.target.value)
                    }
                    style={inputStyle}
                  />

                  <button
                    type="button"
                    onClick={() => removeMilestone(index)}
                    className="btn"
                    style={dangerButton}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))
            )}
          </div>

          <input
            type="file"
            accept="image/jpeg,image/png,image/webp,image/gif"
            onChange={(e) =>
              setFounderForm({
                ...founderForm,
                file: e.target.files?.[0] || null,
                removeImage: false,
              })
            }
            style={inputStyle}
          />

          {founder?.image_url && (
            <label
              style={{
                display: 'flex',
                gap: '.5rem',
                alignItems: 'center',
                fontSize: '.9rem',
              }}
            >
              <input
                type="checkbox"
                checked={founderForm.removeImage}
                onChange={(e) =>
                  setFounderForm({
                    ...founderForm,
                    removeImage: e.target.checked,
                  })
                }
              />
              Remove current photo
            </label>
          )}

          <button
            className="btn"
            type="submit"
            disabled={saving}
            style={primaryButton}
          >
            <Check size={17} />
            {saving ? 'Saving Profile...' : 'Save Founder Profile'}
          </button>
        </form>
      </div>

      <div
        className="card"
        style={{
          padding: '1.5rem',
        }}
      >
        <h2>Mentors</h2>

        <p
          style={{
            color: '#64748b',
            marginBottom: '1.25rem',
          }}
        >
          Mentors appear below the founder on the public About page.
        </p>

        <form
          onSubmit={saveMentor}
          style={formGridStyle}
        >
          <input
            placeholder="Mentor name"
            value={mentorForm.name}
            onChange={(e) =>
              setMentorForm({ ...mentorForm, name: e.target.value })
            }
            style={inputStyle}
            required
          />

          <input
            placeholder="Role"
            value={mentorForm.role}
            onChange={(e) =>
              setMentorForm({ ...mentorForm, role: e.target.value })
            }
            style={inputStyle}
          />

          <textarea
            placeholder="Description"
            value={mentorForm.description}
            onChange={(e) =>
              setMentorForm({ ...mentorForm, description: e.target.value })
            }
            style={textareaStyle}
          />

          <textarea
            placeholder="Quote"
            value={mentorForm.quote}
            onChange={(e) =>
              setMentorForm({ ...mentorForm, quote: e.target.value })
            }
            style={textareaStyle}
          />

          <div style={{ display: 'grid', gap: '.9rem' }}>
            <input
              type="number"
              placeholder="Display order"
              value={mentorForm.displayOrder}
              onChange={(e) =>
                setMentorForm({
                  ...mentorForm,
                  displayOrder: Number(e.target.value),
                })
              }
              style={inputStyle}
            />

            <label
              style={{
                display: 'flex',
                gap: '.5rem',
                alignItems: 'center',
              }}
            >
              <input
                type="checkbox"
                checked={mentorForm.isPublished}
                onChange={(e) =>
                  setMentorForm({ ...mentorForm, isPublished: e.target.checked })
                }
              />
              Published
            </label>
          </div>

          <input
            type="file"
            accept="image/jpeg,image/png,image/webp,image/gif"
            onChange={(e) =>
              setMentorForm({
                ...mentorForm,
                file: e.target.files?.[0] || null,
                removeImage: false,
              })
            }
            style={inputStyle}
          />

          {editingMentorId && (
            <label
              style={{
                display: 'flex',
                gap: '.5rem',
                alignItems: 'center',
                fontSize: '.9rem',
              }}
            >
              <input
                type="checkbox"
                checked={mentorForm.removeImage}
                onChange={(e) =>
                  setMentorForm({ ...mentorForm, removeImage: e.target.checked })
                }
              />
              Remove current photo
            </label>
          )}

          <div style={{ display: 'flex', gap: '.75rem' }}>
            <button
              className="btn"
              type="submit"
              disabled={saving}
              style={primaryButton}
            >
              {editingMentorId ? <Edit3 size={17} /> : <Users size={17} />}
              {saving
                ? 'Saving...'
                : editingMentorId
                  ? 'Update Mentor'
                  : 'Add Mentor'}
            </button>

            {editingMentorId && (
              <button
                type="button"
                className="btn"
                onClick={resetMentorForm}
                style={outlineButton}
              >
                Cancel
              </button>
            )}
          </div>
        </form>

        {mentors.length === 0 ? (
          <div
            style={{
              padding: '2rem',
              textAlign: 'center',
              border: '1px dashed #cbd5e1',
              borderRadius: 12,
              color: '#64748b',
            }}
          >
            No mentors yet.
          </div>
        ) : (
          <div style={managerGrid}>
            {mentors.map((mentor) => (
              <article
                key={mentor.id}
                className="card"
                style={{ overflow: 'hidden' }}
              >
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    height: 150,
                    background: 'linear-gradient(135deg, #f0fdf4, #ecfccb)',
                  }}
                >
                  <img
                    src={
                      mentor.image_url
                        ? resolveMediaUrl(mentor.image_url)
                        : '/piplad-logo.jpg'
                    }
                    alt={mentor.name}
                    style={{
                      width: 110,
                      height: 110,
                      borderRadius: '50%',
                      objectFit: 'cover',
                      border: '4px solid #fff',
                      boxShadow: '0 8px 20px rgba(0,0,0,.12)',
                    }}
                  />
                </div>

                <div style={{ padding: '1rem' }}>
                  <h3 style={{ margin: '0 0 .25rem' }}>{mentor.name}</h3>

                  {mentor.role && (
                    <p
                      style={{
                        margin: '0 0 .5rem',
                        color: '#059669',
                        fontWeight: 600,
                        fontSize: '.85rem',
                      }}
                    >
                      {mentor.role}
                    </p>
                  )}

                  {mentor.is_published === false && (
                    <span className="badge">Hidden</span>
                  )}

                  <div
                    style={{
                      display: 'flex',
                      gap: '.5rem',
                      marginTop: '.75rem',
                    }}
                  >
                    <button
                      type="button"
                      onClick={() => startEditMentor(mentor)}
                      className="btn"
                      style={outlineButton}
                    >
                      <Edit3 size={15} />
                      Edit
                    </button>

                    <button
                      type="button"
                      onClick={() => removeMentor(mentor.id)}
                      className="btn"
                      style={dangerButton}
                    >
                      <Trash2 size={15} />
                      Delete
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </ManagerSection>
  );
}


// ============================================================
// FOOTER FOCUS MANAGER
// ============================================================

function FooterManager() {
  const [items, setItems] = useState([]);

  const [form, setForm] = useState({
    text: '',
    displayOrder: 0,
    isPublished: true,
  });

  const [editingId, setEditingId] = useState(null);

  const [links, setLinks] = useState([]);

  const [linkForm, setLinkForm] = useState({
    label: '',
    path: '',
    displayOrder: 0,
    isPublished: true,
  });

  const [linkEditingId, setLinkEditingId] = useState(null);

  const [settingsForm, setSettingsForm] = useState({
    mission: '',
    copyright: '',
  });

  const [loading, setLoading] = useState(true);

  const [saving, setSaving] = useState(false);

  const [settingsSaving, setSettingsSaving] = useState(false);

  const [error, setError] = useState('');

  async function load() {
    setLoading(true);

    try {
      const [focusData, linkData, settingsData] = await Promise.all([
        fetchAdminFooterFocus(),
        fetchAdminFooterQuickLinks(),
        fetchSiteSettings(),
      ]);

      setItems(Array.isArray(focusData) ? focusData : []);

      setLinks(Array.isArray(linkData) ? linkData : []);

      if (settingsData && typeof settingsData === 'object') {
        setSettingsForm({
          mission: settingsData.mission || '',
          copyright: settingsData.copyright || '',
        });
      }

      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function saveSettings(e) {
    e.preventDefault();

    setError('');

    if (!settingsForm.mission.trim()) {
      setError('Please enter the footer mission statement.');
      return;
    }

    setSettingsSaving(true);

    try {
      await updateSiteSettings({
        mission: settingsForm.mission,
        copyright: settingsForm.copyright,
      });

      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setSettingsSaving(false);
    }
  }

  function resetLink() {
    setLinkEditingId(null);

    setLinkForm({
      label: '',
      path: '',
      displayOrder: 0,
      isPublished: true,
    });
  }

  function startEditLink(link) {
    setLinkEditingId(link.id);

    setLinkForm({
      label: link.label || '',
      path: link.path || '',
      displayOrder: link.display_order || 0,
      isPublished: link.is_published !== false,
    });

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  }

  async function submitLink(e) {
    e.preventDefault();

    setError('');

    if (!linkForm.label.trim()) {
      setError('Please enter the link label.');
      return;
    }

    if (!linkForm.path.trim()) {
      setError('Please enter the link path, e.g. /about or https://example.com.');
      return;
    }

    setSaving(true);

    try {
      if (linkEditingId) {
        await updateAdminFooterQuickLink(linkEditingId, linkForm);
      } else {
        await createAdminFooterQuickLink(linkForm);
      }

      resetLink();

      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function removeLink(id) {
    if (!window.confirm('Delete this footer quick link?')) {
      return;
    }

    try {
      await deleteAdminFooterQuickLink(id);

      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  async function moveLink(index, direction) {
    const next = [...links];

    const target = index + direction;

    if (target < 0 || target >= next.length) {
      return;
    }

    const current = next[index];

    next[index] = next[target];

    next[target] = current;

    setLinks(next);

    try {
      await reorderAdminFooterQuickLinks(
        next.map((link) => link.id)
      );
    } catch (e) {
      setError(e.message);
      await load();
    }
  }

  function reset() {
    setEditingId(null);

    setForm({
      text: '',
      displayOrder: 0,
      isPublished: true,
    });
  }

  function startEdit(item) {
    setEditingId(item.id);

    setForm({
      text: item.text || '',
      displayOrder: item.display_order || 0,
      isPublished: item.is_published !== false,
    });

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  }

  async function submit(e) {
    e.preventDefault();

    setError('');

    if (!form.text.trim()) {
      setError('Please enter the focus item text.');
      return;
    }

    setSaving(true);

    try {
      if (editingId) {
        await updateAdminFooterFocus(editingId, form);
      } else {
        await createAdminFooterFocus(form);
      }

      reset();

      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function remove(id) {
    if (!window.confirm('Delete this footer focus item?')) {
      return;
    }

    try {
      await deleteAdminFooterFocus(id);

      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  async function move(index, direction) {
    const next = [...items];

    const target = index + direction;

    if (target < 0 || target >= next.length) {
      return;
    }

    const current = next[index];

    next[index] = next[target];

    next[target] = current;

    setItems(next);

    try {
      await reorderAdminFooterFocus(
        next.map((item) => item.id)
      );
    } catch (e) {
      setError(e.message);
      await load();
    }
  }

  return (
    <>
      <ErrorMessage message={error} />

      <ManagerSection
        title="Footer Settings"
        icon={<Settings size={22} />}
      >
        <div
          style={{
            padding: '1rem',
            marginBottom: '1.5rem',
            borderRadius: 12,
            background: '#f0fdf4',
            border: '1px solid #bbf7d0',
            color: '#166534',
            lineHeight: 1.6,
          }}
        >
          The mission statement (Column 1) and the copyright line (bottom bar)
          shown in the footer of every page.
        </div>

        <form
          onSubmit={saveSettings}
          style={formGridStyle}
        >
          <textarea
            placeholder="Mission statement, e.g. Creating Opportunities, Creating Lives..."
            value={settingsForm.mission}
            onChange={(e) =>
              setSettingsForm({ ...settingsForm, mission: e.target.value })
            }
            style={textareaStyle}
            required
          />

          <input
            placeholder="Copyright line, e.g. Piplad Welfare Foundation"
            value={settingsForm.copyright}
            onChange={(e) =>
              setSettingsForm({ ...settingsForm, copyright: e.target.value })
            }
            style={inputStyle}
          />

          <div style={{ display: 'flex', gap: '.75rem' }}>
            <button
              className="btn"
              type="submit"
              disabled={settingsSaving}
              style={primaryButton}
            >
              {settingsSaving ? 'Saving...' : 'Save Footer Settings'}
            </button>
          </div>
        </form>
      </ManagerSection>

      <ManagerSection
        title="Quick Links"
        icon={<Link2 size={22} />}
      >
        <div
          style={{
            padding: '1rem',
            marginBottom: '1.5rem',
            borderRadius: 12,
            background: '#f0fdf4',
            border: '1px solid #bbf7d0',
            color: '#166534',
            lineHeight: 1.6,
          }}
        >
          These links power the “Quick Links" column of the footer. Use paths
          like /about, /impact or full https:// URLs. Unpublished links are
          hidden from visitors.
        </div>

        <form
          onSubmit={submitLink}
          style={formGridStyle}
        >
          <input
            placeholder="Link label, e.g. About Our Foundation"
            value={linkForm.label}
            onChange={(e) =>
              setLinkForm({ ...linkForm, label: e.target.value })
            }
            style={inputStyle}
            required
          />

          <input
            placeholder="Path, e.g. /about or https://example.com"
            value={linkForm.path}
            onChange={(e) =>
              setLinkForm({ ...linkForm, path: e.target.value })
            }
            style={inputStyle}
            required
          />

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '.9rem',
            }}
          >
            <input
              type="number"
              placeholder="Display order"
              value={linkForm.displayOrder}
              onChange={(e) =>
                setLinkForm({ ...linkForm, displayOrder: Number(e.target.value) })
              }
              style={inputStyle}
            />

            <label
              style={{
                display: 'flex',
                gap: '.5rem',
                alignItems: 'center',
                padding: '0 0.25rem',
              }}
            >
              <input
                type="checkbox"
                checked={linkForm.isPublished}
                onChange={(e) =>
                  setLinkForm({ ...linkForm, isPublished: e.target.checked })
                }
              />
              Published
            </label>
          </div>

          <div style={{ display: 'flex', gap: '.75rem' }}>
            <button
              className="btn"
              type="submit"
              disabled={saving}
              style={primaryButton}
            >
              {saving
                ? 'Saving...'
                : linkEditingId
                  ? 'Update Link'
                  : 'Add Link'}
            </button>

            {linkEditingId && (
              <button
                type="button"
                className="btn"
                onClick={resetLink}
                style={outlineButton}
              >
                Cancel
              </button>
            )}
          </div>
        </form>

        {loading ? (
          <p>Loading quick links...</p>
        ) : links.length === 0 ? (
          <div
            style={{
              padding: '2rem',
              textAlign: 'center',
              border: '1px dashed #cbd5e1',
              borderRadius: 12,
              color: '#64748b',
            }}
          >
            No quick links yet. The default links are shown to visitors until
            you add some.
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '.75rem' }}>
            {links.map((link, index) => (
              <div
                key={link.id}
                className="card"
                style={{
                  padding: '1rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: '1rem',
                  flexWrap: 'wrap',
                }}
              >
                <div>
                  <strong>{link.label}</strong>

                  <p
                    style={{
                      margin: '.25rem 0 0',
                      color: '#64748b',
                      fontSize: '.8rem',
                    }}
                  >
                    {link.path}
                    {' — '}Order: {link.display_order}
                    {link.is_published === false ? ' — Hidden' : ''}
                  </p>
                </div>

                <div
                  style={{
                    display: 'flex',
                    gap: '.5rem',
                    flexWrap: 'wrap',
                  }}
                >
                  <button
                    type="button"
                    className="btn"
                    onClick={() => moveLink(index, -1)}
                    style={outlineButton}
                    disabled={index === 0}
                  >
                    ↑ Up
                  </button>

                  <button
                    type="button"
                    className="btn"
                    onClick={() => moveLink(index, 1)}
                    style={outlineButton}
                    disabled={index === links.length - 1}
                  >
                    ↓ Down
                  </button>

                  <button
                    type="button"
                    onClick={() => startEditLink(link)}
                    className="btn"
                    style={outlineButton}
                  >
                    <Edit3 size={15} />
                    Edit
                  </button>

                  <button
                    type="button"
                    onClick={() => removeLink(link.id)}
                    className="btn"
                    style={dangerButton}
                  >
                    <Trash2 size={15} />
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </ManagerSection>

      <ManagerSection
        title="Core Focus"
        icon={<Target size={22} />}
      >
      <div
        style={{
          padding: '1rem',
          marginBottom: '1.5rem',
          borderRadius: 12,
          background: '#f0fdf4',
          border: '1px solid #bbf7d0',
          color: '#166534',
          lineHeight: 1.6,
        }}
      >
        These bullet items drive the “Our Core Focus" list at the bottom of
        every page. Unpublished items are hidden from visitors.
      </div>

      <form
        onSubmit={submit}
        style={formGridStyle}
      >
        <textarea
          placeholder="Focus item text, e.g. Childhood Cancer Healthcare"
          value={form.text}
          onChange={(e) =>
            setForm({ ...form, text: e.target.value })
          }
          style={textareaStyle}
          required
        />

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '.9rem',
          }}
        >
          <input
            type="number"
            placeholder="Display order"
            value={form.displayOrder}
            onChange={(e) =>
              setForm({ ...form, displayOrder: Number(e.target.value) })
            }
            style={inputStyle}
          />

          <label
            style={{
              display: 'flex',
              gap: '.5rem',
              alignItems: 'center',
              padding: '0 0.25rem',
            }}
          >
            <input
              type="checkbox"
              checked={form.isPublished}
              onChange={(e) =>
                setForm({ ...form, isPublished: e.target.checked })
              }
            />
            Published
          </label>
        </div>

        <div style={{ display: 'flex', gap: '.75rem' }}>
          <button
            className="btn"
            type="submit"
            disabled={saving}
            style={primaryButton}
          >
            {saving
              ? 'Saving...'
              : editingId
                ? 'Update Item'
                : 'Add Item'}
          </button>

          {editingId && (
            <button
              type="button"
              className="btn"
              onClick={reset}
              style={outlineButton}
            >
              Cancel
            </button>
          )}
        </div>
      </form>

      {loading ? (
        <p>Loading focus items...</p>
      ) : items.length === 0 ? (
        <div
          style={{
            padding: '2rem',
            textAlign: 'center',
            border: '1px dashed #cbd5e1',
            borderRadius: 12,
            color: '#64748b',
          }}
        >
          No focus items yet.
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '.75rem' }}>
          {items.map((item, index) => (
            <div
              key={item.id}
              className="card"
              style={{
                padding: '1rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: '1rem',
                flexWrap: 'wrap',
              }}
            >
              <div>
                <strong>{item.text}</strong>

                <p
                  style={{
                    margin: '.25rem 0 0',
                    color: '#64748b',
                    fontSize: '.8rem',
                  }}
                >
                  Order: {item.display_order}
                  {item.is_published === false ? ' — Hidden' : ''}
                </p>
              </div>

              <div
                style={{
                  display: 'flex',
                  gap: '.5rem',
                  flexWrap: 'wrap',
                }}
              >
                <button
                  type="button"
                  className="btn"
                  onClick={() => move(index, -1)}
                  style={outlineButton}
                  disabled={index === 0}
                >
                  ↑ Up
                </button>

                <button
                  type="button"
                  className="btn"
                  onClick={() => move(index, 1)}
                  style={outlineButton}
                  disabled={index === items.length - 1}
                >
                  ↓ Down
                </button>

                <button
                  type="button"
                  onClick={() => startEdit(item)}
                  className="btn"
                  style={outlineButton}
                >
                  <Edit3 size={15} />
                  Edit
                </button>

                <button
                  type="button"
                  onClick={() => remove(item.id)}
                  className="btn"
                  style={dangerButton}
                >
                  <Trash2 size={15} />
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      </ManagerSection>
    </>
  );
}


// ============================================================
// SITE SETTINGS MANAGER
// ============================================================

function SiteSettingsManager() {
  const [form, setForm] = useState({
    phone: '',
    email: '',
    address: '',
    map_query: '',
  });

  const [loading, setLoading] = useState(true);

  const [saving, setSaving] = useState(false);

  const [error, setError] = useState('');

  const [info, setInfo] = useState('');

  async function load() {
    setLoading(true);

    try {
      const data =
        await fetchSiteSettings();

      setForm({
        phone: data.phone || '',
        email: data.email || '',
        address: data.address || '',
        map_query: data.map_query || '',
      });

      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function submit(e) {
    e.preventDefault();

    setError('');
    setInfo('');

    if (
      !form.phone.trim() ||
      !form.email.trim()
    ) {
      setError(
        'Phone number and email are required.'
      );
      return;
    }

    setSaving(true);

    try {
      const data =
        await updateSiteSettings(form);

      setForm({
        phone: data.phone || form.phone,
        email: data.email || form.email,
        address: data.address || form.address,
        map_query:
          data.map_query || form.map_query,
      });

      setInfo(
        'Settings saved and live across the website.'
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  const fields = [
    [
      'phone',
      'Phone Number',
      'Shown in the top bar, footer and contact page. e.g. +91-8981266033',
      true,
    ],
    [
      'email',
      'Email ID',
      'Shown in the top bar, footer, contact page and support emails. e.g. info@pipladfoundation.in',
      true,
    ],
    [
      'address',
      'Headquarters Address',
      'Full postal address shown in the footer and contact page.',
      false,
    ],
    [
      'map_query',
      'Google Maps Location',
      'Search text used for the embedded map and directions on the contact page. e.g. Manik Pur Buzurg, Bihar',
      false,
    ],
  ];

  return (
    <ManagerSection
      title="Site Settings"
      icon={<Settings size={22} />}
    >
      <ErrorMessage message={error} />

      {info && (
        <div
          style={{
            padding: '.9rem 1rem',
            marginBottom: '1.25rem',
            borderRadius: 10,
            background: '#f0fdf4',
            border: '1px solid #bbf7d0',
            color: '#166534',
            display: 'flex',
            alignItems: 'center',
            gap: '.5rem',
          }}
        >
          <Check size={18} />
          {info}
        </div>
      )}

      <div
        style={{
          padding: '1rem',
          marginBottom: '1.5rem',
          borderRadius: 12,
          background: '#f0f9ff',
          border: '1px solid #bae6fd',
          color: '#0c4a6e',
          lineHeight: 1.6,
        }}
      >
        These contact details are shown across the website — top bar,
        footer, contact page, refund policy and verification/support
        emails. Changes go live immediately.
      </div>

      {loading ? (
        <p>Loading settings...</p>
      ) : (
        <form
          onSubmit={submit}
          style={formGridStyle}
        >
          {fields.map(
            ([
              key,
              label,
              hint,
              isInput,
            ]) => (
              <div key={key}>
                <label
                  style={{
                    fontWeight: 600,
                    display: 'block',
                    marginBottom: '.35rem',
                  }}
                >
                  {label}
                </label>

                {isInput ? (
                  <input
                    type="text"
                    value={form[key]}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        [key]:
                          e.target.value,
                      })
                    }
                    style={inputStyle}
                  />
                ) : (
                  <textarea
                    value={form[key]}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        [key]:
                          e.target.value,
                      })
                    }
                    style={{
                      ...textareaStyle,
                      minHeight: 80,
                    }}
                  />
                )}

                {hint && (
                  <div
                    style={{
                      marginTop: '.35rem',
                      color: '#64748b',
                      fontSize: '.8rem',
                      lineHeight: 1.5,
                    }}
                  >
                    {hint}
                  </div>
                )}
              </div>
            )
          )}

          <div
            style={{
              display: 'flex',
              gap: '.75rem',
            }}
          >
            <button
              type="submit"
              className="btn"
              disabled={saving}
              style={primaryButton}
            >
              {saving
                ? 'Saving...'
                : 'Save Settings'}
            </button>

            <button
              type="button"
              className="btn"
              onClick={load}
              style={outlineButton}
              disabled={loading}
            >
              Reload
            </button>
          </div>
        </form>
      )}
    </ManagerSection>
  );
}


// ============================================================
// HOME PAGE HERO SLIDES
// ============================================================

const emptyHomeSlideForm = {
  eyebrow: '',
  title: '',
  highlight: '',
  text: '',
  isActive: true,
  file: null,
};

function HomeHeroManager() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(emptyHomeSlideForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  async function load() {
    setLoading(true);
    try {
      const slides = await fetchAdminHomeSlides();
      if (slides && slides.length > 0) {
        setItems(slides);
      } else {
        setItems(
          defaultHeroSlides.map((slide, index) => ({
            id: -(index + 1),
            ...slide,
            image_url: slide.image,
            is_active: true,
          }))
        );
      }
      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function patchItem(id, patch) {
    setItems((current) =>
      current.map((item) =>
        item.id === id ? { ...item, ...patch } : item
      )
    );
  }

  async function saveSlide(id) {
    const item = items.find((slide) => slide.id === id);
    if (!item) return;

    if (!item.title.trim()) {
      setError('Slide title is required.');
      return;
    }

    setBusyId(id);
    setError('');
    setNotice('');

    try {
      const fields = {
        eyebrow: item.eyebrow || '',
        title: item.title || '',
        highlight: item.highlight || '',
        text: item.text || '',
        display_order: item.display_order || 0,
        is_active: item.is_active,
        file: item.file || null,
      };

      if (item.id < 0) {
        await createAdminHomeSlide({
          ...fields,
          imageUrl: item.file ? '' : item.image_url || '',
        });
        await load();
        setNotice('Slide created and saved.');
      } else {
        const updated = await updateAdminHomeSlide(id, {
          ...fields,
          imageUrl: item.image_url || null,
        });

        setItems((current) =>
          current.map((slide) =>
            slide.id === id ? { ...updated, file: null } : { ...slide, file: null }
          )
        );

        setNotice('Slide saved.');
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setBusyId(null);
    }
  }

  async function submitNewSlide(e) {
    e.preventDefault();

    setError('');
    setNotice('');

    if (!form.title.trim()) {
      setError('Slide title is required.');
      return;
    }

    if (!form.file) {
      setError('Please choose a background image for the slide.');
      return;
    }

    setSaving(true);

    try {
      await createAdminHomeSlide({
        eyebrow: form.eyebrow,
        title: form.title,
        highlight: form.highlight,
        text: form.text,
        is_active: form.isActive,
        file: form.file,
      });

      setForm(emptyHomeSlideForm);
      setNotice('Slide added. It is now live on the homepage.');
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function removeSlide(id) {
    if (!window.confirm('Delete this home slide?')) {
      return;
    }

    if (id < 0) {
      setItems((current) => current.filter((slide) => slide.id !== id));
      setNotice('Slide removed. It will not appear on the homepage.');
      return;
    }

    setBusyId(id);
    setError('');
    setNotice('');

    try {
      await deleteAdminHomeSlide(id);
      setNotice('Slide deleted.');
      await load();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusyId(null);
    }
  }

  async function moveSlide(index, direction) {
    const target = index + direction;
    if (target < 0 || target >= items.length) return;

    const next = [...items];
    const current = next[index];
    next[index] = next[target];
    next[target] = current;

    setItems(next);

    if (items.some((slide) => slide.id < 0)) {
      setNotice('Order updated. Reorder is saved permanently once all slides are created.');
      return;
    }

    try {
      await reorderAdminHomeSlides(next.map((slide) => slide.id));
      await load();
    } catch (e) {
      setError(e.message);
      await load();
    }
  }

  const fieldLabelStyle = {
    fontWeight: 600,
    display: 'block',
    marginBottom: '.35rem',
    fontSize: '.85rem',
    color: '#334155',
  };

  return (
    <ManagerSection
      title="Home Page Hero Slides"
      icon={<Home size={22} />}
    >
      <ErrorMessage message={error} />

      {notice && (
        <div
          style={{
            padding: '0.85rem 1rem',
            marginBottom: '1rem',
            borderRadius: 8,
            background: '#dcfce7',
            color: '#166534',
          }}
        >
          {notice}
        </div>
      )}

      <div
        style={{
          padding: '1rem',
          marginBottom: '1.5rem',
          borderRadius: 12,
          background: '#f0f9ff',
          border: '1px solid #bae6fd',
          color: '#0c4a6e',
          lineHeight: 1.6,
        }}
      >
        These are the rotating banner slides at the top of the homepage. The
        current 4 default slides are shown below — edit them and press Save to
        persist your changes, or use the form above to add brand-new slides.
      </div>

      <form
        onSubmit={submitNewSlide}
        style={formGridStyle}
      >
        <div
          style={{
            display: 'grid',
            gap: '.9rem',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          }}
        >
          <div>
            <label style={fieldLabelStyle}>Eyebrow (small label)</label>
            <input
              placeholder="e.g. Education for All"
              value={form.eyebrow}
              onChange={(e) =>
                setForm({ ...form, eyebrow: e.target.value })
              }
              style={inputStyle}
            />
          </div>

          <div>
            <label style={fieldLabelStyle}>Title (required)</label>
            <input
              placeholder="e.g. Empowering Minds,"
              value={form.title}
              onChange={(e) =>
                setForm({ ...form, title: e.target.value })
              }
              required
              style={inputStyle}
            />
          </div>

          <div>
            <label style={fieldLabelStyle}>Highlight (bold part of title)</label>
            <input
              placeholder="e.g. Illuminating Futures"
              value={form.highlight}
              onChange={(e) =>
                setForm({ ...form, highlight: e.target.value })
              }
              style={inputStyle}
            />
          </div>
        </div>

        <textarea
          placeholder="Slide text (shown under the title)"
          value={form.text}
          onChange={(e) =>
            setForm({ ...form, text: e.target.value })
          }
          style={{ ...textareaStyle, minHeight: 70 }}
        />

        <div
          style={{
            display: 'flex',
            gap: '.9rem',
            flexWrap: 'wrap',
            alignItems: 'center',
          }}
        >
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp,image/gif"
            onChange={(e) =>
              setForm({ ...form, file: e.target.files?.[0] || null })
            }
            required
            style={{
              ...inputStyle,
              width: 'auto',
              flex: 1,
              minWidth: 220,
            }}
          />

          <label
            style={{
              display: 'flex',
              gap: '.5rem',
              alignItems: 'center',
              fontWeight: 600,
              color: '#334155',
            }}
          >
            <input
              type="checkbox"
              checked={form.isActive}
              onChange={(e) =>
                setForm({ ...form, isActive: e.target.checked })
              }
            />
            Active
          </label>

          <button
            className="btn"
            type="submit"
            disabled={saving}
            style={primaryButton}
          >
            <Plus size={16} />
            {saving ? 'Adding...' : 'Add Slide'}
          </button>
        </div>
      </form>

      <div
        style={{
          display: 'grid',
          gap: '1.5rem',
        }}
      >
        {loading ? (
          <p>Loading...</p>
        ) : items.length === 0 ? (
          <p style={{ color: '#64748b' }}>
            No custom slides yet. The default slides are live on the homepage —
            use the form above to add your own.
          </p>
        ) : (
          items.map((item, index) => (
            <article
              key={item.id}
              className="card"
              style={{ overflow: 'hidden' }}
            >
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'minmax(200px, 300px) 1fr',
                  gap: 0,
                }}
              >
                <div>
                  {item.image_url ? (
                    <img
                      src={resolveMediaUrl(item.image_url)}
                      alt={item.title}
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover',
                        minHeight: 200,
                      }}
                    />
                  ) : (
                    <div
                      style={{
                        width: '100%',
                        height: '100%',
                        minHeight: 200,
                        display: 'grid',
                        placeItems: 'center',
                        background: '#e2e8f0',
                        color: '#64748b',
                      }}
                    >
                      No image
                    </div>
                  )}
                </div>

                <div
                  style={{
                    padding: '1.25rem',
                    display: 'grid',
                    gap: '.75rem',
                    alignContent: 'start',
                  }}
                >
                  <div
                    style={{
                      display: 'grid',
                      gap: '.75rem',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                    }}
                  >
                    <div>
                      <label style={fieldLabelStyle}>Eyebrow</label>
                      <input
                        value={item.eyebrow || ''}
                        onChange={(e) =>
                          patchItem(item.id, { eyebrow: e.target.value })
                        }
                        style={inputStyle}
                      />
                    </div>

                    <div>
                      <label style={fieldLabelStyle}>Title</label>
                      <input
                        value={item.title || ''}
                        onChange={(e) =>
                          patchItem(item.id, { title: e.target.value })
                        }
                        style={inputStyle}
                      />
                    </div>

                    <div>
                      <label style={fieldLabelStyle}>Highlight</label>
                      <input
                        value={item.highlight || ''}
                        onChange={(e) =>
                          patchItem(item.id, { highlight: e.target.value })
                        }
                        style={inputStyle}
                      />
                    </div>
                  </div>

                  <div>
                    <label style={fieldLabelStyle}>Slide text</label>
                    <textarea
                      value={item.text || ''}
                      onChange={(e) =>
                        patchItem(item.id, { text: e.target.value })
                      }
                      style={{ ...textareaStyle, minHeight: 60 }}
                    />
                  </div>

                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp,image/gif"
                    onChange={(e) =>
                      patchItem(item.id, { file: e.target.files?.[0] || null })
                    }
                    style={inputStyle}
                  />

                  <div
                    style={{
                      display: 'flex',
                      gap: '.5rem',
                      flexWrap: 'wrap',
                      alignItems: 'center',
                    }}
                  >
                    <label
                      style={{
                        display: 'flex',
                        gap: '.5rem',
                        alignItems: 'center',
                        fontWeight: 600,
                        color: '#334155',
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={item.is_active}
                        onChange={(e) =>
                          patchItem(item.id, { is_active: e.target.checked })
                        }
                      />
                      Active
                    </label>

                    <button
                      className="btn"
                      onClick={() => saveSlide(item.id)}
                      disabled={busyId === item.id || loading}
                      style={primaryButton}
                    >
                      <Save size={15} />
                      {busyId === item.id ? 'Saving...' : 'Save'}
                    </button>

                    <button
                      className="btn"
                      onClick={() => moveSlide(index, -1)}
                      disabled={index === 0 || loading}
                      style={outlineButton}
                      title="Move up"
                    >
                      <ArrowUp size={15} />
                    </button>

                    <button
                      className="btn"
                      onClick={() => moveSlide(index, 1)}
                      disabled={index === items.length - 1 || loading}
                      style={outlineButton}
                      title="Move down"
                    >
                      <ArrowDown size={15} />
                    </button>

                    <button
                      className="btn"
                      onClick={() => removeSlide(item.id)}
                      disabled={busyId === item.id || loading}
                      style={dangerButton}
                    >
                      <Trash2 size={15} />
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            </article>
          ))
        )}
      </div>
    </ManagerSection>
  );
}


// ============================================================
// STYLES
// ============================================================

const inputStyle = {
  width: '100%',
  boxSizing: 'border-box',
  padding: '0.75rem',
  border:
    '1px solid #cbd5e1',
  borderRadius: 8,
  background: '#fff',
};

const textareaStyle = {
  ...inputStyle,
  minHeight: 100,
  resize: 'vertical',
};

const formGridStyle = {
  display: 'grid',
  gap: '.9rem',
  marginBottom: '2rem',
};

const managerGrid = {
  display: 'grid',
  gridTemplateColumns:
    'repeat(auto-fit, minmax(260px, 1fr))',
  gap: '1.25rem',
};

const primaryButton = {
  background: '#059669',
  color: '#fff',
  border: 0,
};

const dangerButton = {
  background: '#fff',
  color: '#b91c1c',
  border:
    '1px solid #fecaca',
};

const outlineButton = {
  background: '#fff',
  color: '#0f172a',
  border:
    '1px solid #cbd5e1',
};

const tableStyle = {
  width: '100%',
  borderCollapse:
    'collapse',
  textAlign: 'left',
};

const th = {
  padding: '1rem',
  background: '#f1f5f9',
  color: '#334155',
};

const td = {
  padding: '1rem',
  borderBottom:
    '1px solid #e2e8f0',
  color: '#475569',
};
