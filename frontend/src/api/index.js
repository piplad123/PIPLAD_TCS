const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api').replace(/\/$/, '');

const API_ORIGIN = API_BASE_URL.replace(/\/api$/, '');

export function resolveMediaUrl(url) {
  if (!url) return '';
  if (/^https?:\/\//i.test(url)) return url;
  if (url.startsWith('/')) return `${API_ORIGIN}${url}`;
  return `${API_ORIGIN}/${url}`;
}

// Rewrite a Cloudinary image URL to add responsive transform params
// (width cropping, auto compression and next-gen format). Non-Cloudinary
// URLs pass through unchanged.
export function cloudinaryUrl(url, options = {}) {
  if (!url) return '';
  if (!/res\.cloudinary\.com\//i.test(url)) return url;
  const { width, quality = 'auto', format = 'auto' } = options;
  const parts = [];
  if (width) parts.push(`w_${width}`, 'c_limit');
  if (quality) parts.push(`q_${quality}`);
  if (format) parts.push(`f_${format}`);
  if (!parts.length) return url;
  return url.replace(/\/image\/upload\//, `/image/upload/${parts.join(',')}/`);
}

export async function fetchCauses() {
  const res = await fetch(`${API_BASE_URL}/causes`);
  if (!res.ok) throw new Error('Failed to fetch causes');
  return res.json();
}

// ============================================================
// PUBLIC SITE SETTINGS (contact details etc.)
// ============================================================

export async function fetchSiteSettings() {
  const res = await fetch(`${API_BASE_URL}/settings`);

  if (!res.ok) {
    throw new Error('Failed to fetch site settings');
  }

  return res.json();
}


// ============================================================
// PUBLIC VISITOR TRACKING
// ============================================================

const VISITOR_KEY_STORAGE = 'pwf_visitor_key';

function getVisitorKey() {
  try {
    let key = localStorage.getItem(VISITOR_KEY_STORAGE);

    if (!key) {
      key =
        globalThis.crypto && typeof crypto.randomUUID === 'function'
          ? crypto.randomUUID()
          : `v-${Date.now()}-${Math.random().toString(36).slice(2)}`;
      localStorage.setItem(VISITOR_KEY_STORAGE, key);
    }

    return key;
  } catch {
    return null;
  }
}

export async function trackVisit() {
  const visitorKey = getVisitorKey();
  if (!visitorKey) return null;

  try {
    const res = await fetch(`${API_BASE_URL}/visits/track`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ visitor_key: visitorKey }),
    });

    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function submitContact(data) {
  const res = await fetch(`${API_BASE_URL}/contact`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!res.ok) throw new Error('Failed to submit contact form');
  return res.json();
}

export async function submitVolunteerApplication(data) {
  const form = new FormData();

  form.append('full_name', data.full_name || '');
  form.append('email', data.email || '');
  form.append('phone', data.phone || '');
  form.append('interest_area', data.interest_area || '');

  if (data.about_yourself) {
    form.append('about_yourself', data.about_yourself);
  }

  if (data.profile_pic) {
    form.append('profile_pic', data.profile_pic);
  }

  if (data.website) {
    form.append('website', data.website);
  }

  const res = await fetch(`${API_BASE_URL}/volunteers`, {
    method: 'POST',
    body: form,
  });

  if (!res.ok) {
    const response = await res.json().catch(() => ({}));
    throw new Error(response.detail || 'Failed to submit volunteer application');
  }

  return res.json();
}

export async function createRazorpayOrder(data) {
  const res = await fetch(`${API_BASE_URL}/donate/create-order`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || 'Failed to create donation order');
  }
  return res.json();
}

export async function verifyPayment(data) {
  const res = await fetch(`${API_BASE_URL}/donate/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || 'Failed to verify payment');
  }
  return res.json();
}


// ============================================================
// ADMIN AUTHENTICATION
// ============================================================

const ADMIN_STORAGE_KEY = 'pwf_admin_basic_auth';

export function getAdminCredentials() {
  try {
    const raw = sessionStorage.getItem(ADMIN_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setAdminCredentials(username, password) {
  sessionStorage.setItem(
    ADMIN_STORAGE_KEY,
    JSON.stringify({ username, password })
  );
}

export function clearAdminCredentials() {
  sessionStorage.removeItem(ADMIN_STORAGE_KEY);
}


// ============================================================
// ADMIN REQUEST HELPER
// ============================================================

async function adminFetch(path, options = {}) {
  const credentials = getAdminCredentials();

  if (!credentials) {
    const error = new Error('ADMIN_AUTH_REQUIRED');
    error.code = 'ADMIN_AUTH_REQUIRED';
    throw error;
  }

  const headers = new Headers(options.headers || {});

  headers.set(
    'Authorization',
    `Basic ${btoa(`${credentials.username}:${credentials.password}`)}`
  );

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    cache: 'no-store',
    headers,
  });

  if (response.status === 401) {
    clearAdminCredentials();

    const error = new Error('ADMIN_AUTH_REQUIRED');
    error.code = 'ADMIN_AUTH_REQUIRED';
    throw error;
  }

  if (!response.ok) {
    let message = `Request failed (${response.status})`;

    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      // Keep the generic message.
    }

    throw new Error(message);
  }

  if (response.status === 204) return null;

  return response.json();
}


// ============================================================
// ADMIN DASHBOARD
// ============================================================

export async function fetchAdminStats() {
  return adminFetch('/admin/stats');
}

export async function fetchAdminVisits(days = 30, months = 6) {
  return adminFetch(`/admin/visits?days=${days}&months=${months}`);
}

export async function updateSiteSettings(values) {
  return adminFetch('/admin/settings', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(values),
  });
}

// ============================================================
// HOME PAGE HERO SLIDES
// ============================================================

export async function fetchHomeSlides() {
  const res = await fetch(`${API_BASE_URL}/home/slides`);
  if (!res.ok) throw new Error('Failed to fetch home slides');
  return res.json();
}

export async function fetchAdminHomeSlides() {
  return adminFetch('/admin/home/slides');
}

export async function createAdminHomeSlide(form) {
  const data = new FormData();
  data.append('title', form.title || '');
  if (form.eyebrow) data.append('eyebrow', form.eyebrow);
  if (form.highlight) data.append('highlight', form.highlight);
  if (form.text) data.append('text', form.text);
  if (form.display_order) data.append('display_order', String(form.display_order));
  data.append('is_active', form.is_active !== false ? 'true' : 'false');
  if (form.file) data.append('image', form.file);
  else if (form.imageUrl) data.append('image_url', form.imageUrl);

  return adminFetch('/admin/home/slides', {
    method: 'POST',
    body: data,
  });
}

export async function updateAdminHomeSlide(id, form) {
  const data = new FormData();
  if (form.title !== undefined) data.append('title', form.title || '');
  if (form.eyebrow !== undefined) data.append('eyebrow', form.eyebrow || '');
  if (form.highlight !== undefined) data.append('highlight', form.highlight || '');
  if (form.text !== undefined) data.append('text', form.text || '');
  if (form.display_order !== undefined) data.append('display_order', String(form.display_order));
  if (form.is_active !== undefined) data.append('is_active', form.is_active ? 'true' : 'false');
  if (form.file) data.append('image', form.file);
  else if (form.imageUrl !== undefined && form.imageUrl !== null) data.append('image_url', form.imageUrl || '');

  return adminFetch(`/admin/home/slides/${id}`, {
    method: 'PUT',
    body: data,
  });
}

export async function deleteAdminHomeSlide(id) {
  return adminFetch(`/admin/home/slides/${id}`, {
    method: 'DELETE',
  });
}

export async function reorderAdminHomeSlides(orderedIds) {
  return adminFetch('/admin/home/slides/reorder', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(orderedIds),
  });
}

export async function fetchAdminVolunteers() {
  return adminFetch('/admin/volunteers');
}

export async function updateAdminVolunteerStatus(id, status) {
  return adminFetch(`/admin/volunteers/${id}/status?status_value=${encodeURIComponent(status)}`, {
    method: 'PATCH',
  });
}

export async function deleteAdminVolunteer(id) {
  return adminFetch(`/admin/volunteers/${id}`, { method: 'DELETE' });
}

export async function resendAdminVolunteerCard(id) {
  return adminFetch(`/admin/volunteers/${id}/resend-card`, {
    method: 'POST',
  });
}

export async function resendAdminVolunteerRejection(id) {
  return adminFetch(`/admin/volunteers/${id}/resend-rejection-email`, {
    method: 'POST',
  });
}


// ============================================================
// ADMIN GALLERY
// ============================================================

export async function fetchAdminGallery() {
  return adminFetch('/admin/gallery');
}

export async function fetchAdminGalleryCategories() {
  return adminFetch('/admin/gallery/categories');
}

export async function uploadAdminGalleryImage({
  title,
  description,
  category,
  files,
}) {
  const form = new FormData();

  form.append('title', title);

  if (category) {
    form.append('category', category);
  }

  if (description) {
    form.append('description', description);
  }

  for (const file of files) {
    form.append('files', file);
  }

  return adminFetch('/admin/gallery/upload', {
    method: 'POST',
    body: form,
  });
}

export async function deleteAdminGalleryImage(id) {
  return adminFetch(`/admin/gallery/${id}`, {
    method: 'DELETE',
  });
}


// ============================================================
// ADMIN VIDEOS
// ============================================================

export async function fetchAdminVideos() {
  return adminFetch('/admin/videos');
}

export async function fetchAdminVideoCategories() {
  return adminFetch('/admin/videos/categories');
}

export async function uploadAdminVideo({
  title,
  description,
  category,
  files,
}) {
  const form = new FormData();

  form.append('title', title);

  if (category) {
    form.append('category', category);
  }

  if (description) {
    form.append('description', description);
  }

  for (const file of files) {
    form.append('files', file);
  }

  return adminFetch('/admin/videos/upload', {
    method: 'POST',
    body: form,
  });
}

export async function deleteAdminVideo(id) {
  return adminFetch(`/admin/videos/${id}`, {
    method: 'DELETE',
  });
}


// ============================================================
// ADMIN PROJECTS
// ============================================================

export async function fetchAdminProjects() {
  return adminFetch('/admin/projects');
}

export async function createAdminProject({
  title,
  description,
  expectedDate,
  file,
}) {
  const form = new FormData();

  form.append('title', title);

  if (description) {
    form.append('description', description);
  }

  if (expectedDate) {
    form.append('expected_date', expectedDate);
  }

  if (file) {
    form.append('file', file);
  }

  return adminFetch('/admin/projects', {
    method: 'POST',
    body: form,
  });
}

export async function updateAdminProject(
  id,
  {
    title,
    description,
    expectedDate,
    file,
    removeImage,
  }
) {
  const form = new FormData();

  form.append('title', title);

  if (description) {
    form.append('description', description);
  }

  if (expectedDate) {
    form.append('expected_date', expectedDate);
  }

  form.append('remove_image', String(Boolean(removeImage)));

  if (file) {
    form.append('file', file);
  }

  return adminFetch(`/admin/projects/${id}`, {
    method: 'PUT',
    body: form,
  });
}

export async function deleteAdminProject(id) {
  return adminFetch(`/admin/projects/${id}`, {
    method: 'DELETE',
  });
}


// ============================================================
// ADMIN CAUSES
// ============================================================

export async function fetchAdminCauses() {
  return adminFetch('/admin/causes');
}

export async function createAdminCause({
  title,
  category,
  shortDescription,
  fullDescription,
  targetAmount,
  file,
}) {
  const form = new FormData();

  form.append('title', title);
  form.append('short_description', shortDescription || '');

  if (category) {
    form.append('category', category);
  }

  if (fullDescription) {
    form.append('full_description', fullDescription);
  }

  if (targetAmount) {
    form.append('target_amount', String(targetAmount));
  }

  if (file) {
    form.append('file', file);
  }

  return adminFetch('/admin/causes', {
    method: 'POST',
    body: form,
  });
}

export async function updateAdminCause(
  id,
  {
    title,
    category,
    shortDescription,
    fullDescription,
    targetAmount,
    file,
    removeImage,
  }
) {
  const form = new FormData();

  form.append('title', title);
  form.append('short_description', shortDescription || '');

  if (category) {
    form.append('category', category);
  }

  if (fullDescription) {
    form.append('full_description', fullDescription);
  }

  if (targetAmount) {
    form.append('target_amount', String(targetAmount));
  }

  form.append('remove_image', String(Boolean(removeImage)));

  if (file) {
    form.append('file', file);
  }

  return adminFetch(`/admin/causes/${id}`, {
    method: 'PUT',
    body: form,
  });
}

export async function deleteAdminCause(id) {
  return adminFetch(`/admin/causes/${id}`, {
    method: 'DELETE',
  });
}


// ============================================================
// PUBLIC GALLERY
// ============================================================

export async function fetchGalleryItems() {
  const res = await fetch(`${API_BASE_URL}/gallery`);

  if (!res.ok) {
    throw new Error('Failed to fetch gallery items');
  }

  return res.json();
}


// ============================================================
// PUBLIC VIDEOS
// ============================================================

export async function fetchVideos() {
  const res = await fetch(`${API_BASE_URL}/videos`);

  if (!res.ok) {
    throw new Error('Failed to fetch videos');
  }

  return res.json();
}


// ============================================================
// PUBLIC UPCOMING PROJECTS
// ============================================================

export async function fetchCertificates() {
  const res = await fetch(`${API_BASE_URL}/certificates`);
  if (!res.ok) throw new Error('Failed to fetch certificates');
  return res.json();
}

export async function fetchUpcomingProjects() {
  const res = await fetch(`${API_BASE_URL}/projects?status=upcoming`);

  if (!res.ok) {
    throw new Error('Failed to fetch upcoming projects');
  }

  return res.json();
}


// ============================================================
// DONATIONS
// ============================================================

export async function fetchDonationsList() {
  const res = await fetch(`${API_BASE_URL}/donate`);

  if (!res.ok) {
    throw new Error('Failed to fetch donations');
  }

  return res.json();
}

export async function fetchAdminDonations(page = 1, pageSize = 10) {
  return adminFetch(`/admin/donations?page=${page}&page_size=${pageSize}`);
}

export async function resendAdminDonationReceipt(id) {
  return adminFetch(`/admin/donations/${id}/resend-receipt`, {
    method: 'POST',
  });
}

export async function fetchAdminDonationEmailPreview(id) {
  return adminFetch(`/admin/donations/${id}/email-preview`);
}


// ============================================================
// CONTACT
// ============================================================

export async function fetchContactInquiries() {
  return adminFetch('/contact');
}

// ============================================================
// TEAM
// ============================================================

export async function fetchTeam() {
  const res = await fetch(`${API_BASE_URL}/team`);

  if (!res.ok) {
    throw new Error('Failed to fetch team');
  }

  return res.json();
}


// ============================================================
// ADMIN TEAM
// ============================================================

export async function fetchAdminTeam() {
  return adminFetch('/admin/team');
}
export async function createAdminTeamMember({
  name,
  role,
  team,
  bio,
  file,
  memberId,
  joinedDate,
  email,
}) {
  const form = new FormData();

  form.append('name', name);

  if (role) {
    form.append('role', role);
  }

  form.append(
    'team',
    team || 'General'
  );

  if (bio) {
    form.append('bio', bio);
  }

  if (memberId) {
    form.append('member_id', memberId);
  }

  if (joinedDate) {
    form.append('joined_date', joinedDate);
  }

  if (email) {
    form.append('email', email);
  }

  // Photo is optional.
  if (file) {
    form.append('file', file);
  }

  return adminFetch('/admin/team', {
    method: 'POST',
    body: form,
  });
}

export async function updateAdminTeamMember(
  id,
  {
    name,
    role,
    team,
    bio,
    file,
    memberId,
    joinedDate,
    email,
    removeImage,
  }
) {
  const form = new FormData();

  form.append('name', name);

  if (role) {
    form.append('role', role);
  }

  form.append(
    'team',
    team || 'General'
  );

  if (bio) {
    form.append('bio', bio);
  }

  if (memberId) {
    form.append('member_id', memberId);
  }

  if (joinedDate) {
    form.append('joined_date', joinedDate);
  }

  if (email) {
    form.append('email', email);
  }

  form.append('remove_image', String(Boolean(removeImage)));

  // Photo is optional.
  if (file) {
    form.append('file', file);
  }

  return adminFetch(`/admin/team/${id}`, {
    method: 'PUT',
    body: form,
  });
}

export async function deleteAdminTeamMember(id) {
  return adminFetch(`/admin/team/${id}`, {
    method: 'DELETE',
  });
}

async function adminFetchBlob(path, options = {}) {
  const credentials = getAdminCredentials();

  if (!credentials) {
    const error = new Error('ADMIN_AUTH_REQUIRED');
    error.code = 'ADMIN_AUTH_REQUIRED';
    throw error;
  }

  const headers = new Headers(options.headers || {});
  headers.set(
    'Authorization',
    `Basic ${btoa(`${credentials.username}:${credentials.password}`)}`
  );

  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: 'no-store',
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearAdminCredentials();

    const error = new Error('ADMIN_AUTH_REQUIRED');
    error.code = 'ADMIN_AUTH_REQUIRED';
    throw error;
  }

  if (!response.ok) {
    let message = `Request failed (${response.status})`;

    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      // Keep the generic message.
    }

    throw new Error(message);
  }

  return response.blob();
}

export async function fetchAdminTeamCard(id) {
  return adminFetchBlob(`/admin/team/${id}/card`);
}

export async function sendAdminTeamCard(id) {
  return adminFetch(`/admin/team/${id}/card/send`, {
    method: 'POST',
  });
}

// ============================================================
// ADMIN CERTIFICATES
// ============================================================

export async function fetchAdminCertificates() {
  return adminFetch('/admin/certificates');
}

export async function createAdminCertificate({
  title,
  description,
  file,
}) {
  const form = new FormData();

  form.append('title', title);

  if (description) {
    form.append('description', description);
  }

  if (file) {
    form.append('file', file);
  }

  return adminFetch('/admin/certificates', {
    method: 'POST',
    body: form,
  });
}

export async function updateAdminCertificate(
  id,
  {
    title,
    description,
    file,
    removeImage,
  }
) {
  const form = new FormData();

  form.append('title', title);

  if (description) {
    form.append('description', description);
  }

  form.append('remove_image', String(Boolean(removeImage)));

  if (file) {
    form.append('file', file);
  }

  return adminFetch(`/admin/certificates/${id}`, {
    method: 'PUT',
    body: form,
  });
}

export async function deleteAdminCertificate(id) {
  return adminFetch(`/admin/certificates/${id}`, {
    method: 'DELETE',
  });
}

// ============================================================
// CONTACT INQUIRIES
// ============================================================

export async function deleteContactInquiry(id) {
  return adminFetch(`/contact/${id}`, {
    method: 'DELETE',
  });
}

// ============================================================
// PUBLIC BLOG
// ============================================================

export async function fetchBlogPosts({ category, q } = {}) {
  const params = new URLSearchParams();
  if (category && category !== 'All') params.set('category', category);
  if (q) params.set('q', q);
  const query = params.toString();

  const res = await fetch(`${API_BASE_URL}/blog${query ? `?${query}` : ''}`);

  if (!res.ok) {
    throw new Error('Failed to fetch blog posts');
  }

  return res.json();
}

export async function fetchBlogPost(id) {
  const res = await fetch(`${API_BASE_URL}/blog/${id}`);

  if (!res.ok) {
    if (res.status === 404) {
      throw new Error('Blog post not found');
    }

    throw new Error('Failed to fetch blog post');
  }

  return res.json();
}

// ============================================================
// IMPACT
// ============================================================

export async function fetchPublicImpact() {
  const res = await fetch(`${API_BASE_URL}/impact`);

  if (!res.ok) {
    throw new Error('Failed to fetch impact data');
  }

  return res.json();
}

export async function fetchAdminImpact() {
  return adminFetch('/impact/admin');
}

export async function updateAdminImpact(metrics) {
  return adminFetch('/impact/admin', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ metrics }),
  });
}


// ============================================================
// PUBLIC ABOUT (FOUNDER & MENTORS)
// ============================================================

async function publicGet(path) {
  const res = await fetch(`${API_BASE_URL}${path}`);

  if (!res.ok) {
    throw new Error(`Failed to fetch ${path}`);
  }

  return res.json();
}

export async function fetchFounder() {
  return publicGet('/about/founder');
}

export async function fetchMentors() {
  return publicGet('/about/mentors');
}

export async function fetchFooterFocus() {
  return publicGet('/about/footer-focus');
}

export async function fetchFooterQuickLinks() {
  return publicGet('/about/footer-links');
}


// ============================================================
// ADMIN ABOUT (FOUNDER & MENTORS)
// ============================================================

export async function fetchAdminFounder() {
  return adminFetch('/admin/about/founder');
}

export async function updateAdminFounder({
  name,
  role,
  eyebrow,
  title,
  imageAlt,
  introduction,
  story,
  vision,
  quote,
  milestones,
  removeImage,
  file,
}) {
  const form = new FormData();

  if (name) form.append('name', name);
  if (role) form.append('role', role);
  if (eyebrow) form.append('eyebrow', eyebrow);
  if (title) form.append('title', title);
  if (imageAlt) form.append('image_alt', imageAlt);
  if (introduction) form.append('introduction', introduction);
  if (story) form.append('story', story);
  if (vision) form.append('vision', vision);
  if (quote) form.append('quote', quote);

  if (milestones) {
    form.append('milestones', JSON.stringify(milestones));
  }

  form.append('remove_image', String(Boolean(removeImage)));

  if (file) {
    form.append('file', file);
  }

  return adminFetch('/admin/about/founder', {
    method: 'PUT',
    body: form,
  });
}

export async function fetchAdminMentors() {
  return adminFetch('/admin/about/mentors');
}

export async function createAdminMentor({
  name,
  role,
  description,
  quote,
  displayOrder,
  isPublished,
  file,
}) {
  const form = new FormData();

  form.append('name', name);

  if (role) form.append('role', role);
  if (description) form.append('description', description);
  if (quote) form.append('quote', quote);

  form.append('display_order', String(displayOrder || 0));
  form.append('is_published', String(Boolean(isPublished)));

  if (file) {
    form.append('file', file);
  }

  return adminFetch('/admin/about/mentors', {
    method: 'POST',
    body: form,
  });
}

export async function updateAdminMentor(
  id,
  {
    name,
    role,
    description,
    quote,
    displayOrder,
    isPublished,
    removeImage,
    file,
  }
) {
  const form = new FormData();

  if (name) form.append('name', name);
  if (role) form.append('role', role);
  if (description) form.append('description', description);
  if (quote) form.append('quote', quote);

  form.append('display_order', String(displayOrder || 0));
  form.append('is_published', String(Boolean(isPublished)));
  form.append('remove_image', String(Boolean(removeImage)));

  if (file) {
    form.append('file', file);
  }

  return adminFetch(`/admin/about/mentors/${id}`, {
    method: 'PUT',
    body: form,
  });
}

export async function deleteAdminMentor(id) {
  return adminFetch(`/admin/about/mentors/${id}`, {
    method: 'DELETE',
  });
}


// ============================================================
// ADMIN FOOTER FOCUS
// ============================================================

export async function fetchAdminFooterFocus() {
  return adminFetch('/admin/footer-focus');
}

export async function createAdminFooterFocus({ text, displayOrder, isPublished }) {
  const form = new FormData();

  form.append('text', text);
  form.append('display_order', String(displayOrder || 0));
  form.append('is_published', String(Boolean(isPublished)));

  return adminFetch('/admin/footer-focus', {
    method: 'POST',
    body: form,
  });
}

export async function updateAdminFooterFocus(
  id,
  { text, displayOrder, isPublished }
) {
  const form = new FormData();

  form.append('text', text);
  form.append('display_order', String(displayOrder || 0));
  form.append('is_published', String(Boolean(isPublished)));

  return adminFetch(`/admin/footer-focus/${id}`, {
    method: 'PUT',
    body: form,
  });
}

export async function deleteAdminFooterFocus(id) {
  return adminFetch(`/admin/footer-focus/${id}`, {
    method: 'DELETE',
  });
}

export async function reorderAdminFooterFocus(order) {
  return adminFetch('/admin/footer-focus/reorder', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ order }),
  });
}

export async function fetchAdminFooterQuickLinks() {
  return adminFetch('/admin/footer-links');
}

export async function createAdminFooterQuickLink({ label, path, displayOrder, isPublished }) {
  const form = new FormData();

  form.append('label', label);
  form.append('path', path);
  form.append('display_order', String(displayOrder || 0));
  form.append('is_published', String(Boolean(isPublished)));

  return adminFetch('/admin/footer-links', {
    method: 'POST',
    body: form,
  });
}

export async function updateAdminFooterQuickLink(
  id,
  { label, path, displayOrder, isPublished }
) {
  const form = new FormData();

  form.append('label', label);
  form.append('path', path);
  form.append('display_order', String(displayOrder || 0));
  form.append('is_published', String(Boolean(isPublished)));

  return adminFetch(`/admin/footer-links/${id}`, {
    method: 'PUT',
    body: form,
  });
}

export async function deleteAdminFooterQuickLink(id) {
  return adminFetch(`/admin/footer-links/${id}`, {
    method: 'DELETE',
  });
}

export async function reorderAdminFooterQuickLinks(order) {
  return adminFetch('/admin/footer-links/reorder', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ order }),
  });
}


// ============================================================
// PUBLIC VERIFICATION (QR codes / certificate numbers)
// ============================================================

export async function verifyCertificate(identifier) {
  const res = await fetch(`${API_BASE_URL}/verify/certificate/${encodeURIComponent(identifier)}`, {
    cache: 'no-store',
  });
  if (!res.ok) throw new Error('Verification service unreachable');
  return res.json();
}

export async function verifyVolunteer(identifier) {
  const res = await fetch(`${API_BASE_URL}/verify/volunteer/${encodeURIComponent(identifier)}`, {
    cache: 'no-store',
  });
  if (!res.ok) throw new Error('Verification service unreachable');
  return res.json();
}


// ============================================================
// ADMIN GENERATED DOCUMENTS – shared download / revoke helpers
// ============================================================

function downloadBlob(blob, fallbackName) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fallbackName;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export async function downloadAdminCertificate(id, format = 'jpg') {
  const blob = await adminFetchBlob(`/admin/generated/certificates/${id}/download?format=${format}`);
  downloadBlob(blob, `certificate-${format === 'pdf' ? 'pdf' : 'jpg'}`);
}

export async function downloadAdminVolunteerCard(id, format = 'jpg') {
  const blob = await adminFetchBlob(`/admin/generated/volunteers/${id}/download?format=${format}`);
  downloadBlob(blob, `volunteer-id-card-${format === 'pdf' ? 'pdf' : 'jpg'}`);
}

export async function revokeAdminCertificate(id) {
  return adminFetch(`/admin/generated/certificates/${id}/revoke`, { method: 'POST' });
}

export async function revokeAdminVolunteerCard(id) {
  return adminFetch(`/admin/generated/volunteers/${id}/revoke`, { method: 'POST' });
}


// ============================================================
// ADMIN CERTIFICATE MANAGEMENT (admin generate flow)
// ============================================================

export async function fetchCertManagementStats() {
  return adminFetch('/admin/cert-management/stats');
}

export async function previewManagedDocument(payload) {
  return adminFetchBlob('/admin/cert-management/preview', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export async function generateManagedDocument(payload) {
  return adminFetch('/admin/cert-management/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export async function sendManagedDocumentEmail(kind, recordId) {
  return adminFetch(`/admin/cert-management/${kind}/${recordId}/send-email`, {
    method: 'POST',
  });
}

export async function fetchManagedDocumentPdf(kind, recordId) {
  const endpoint =
    kind === 'certificate'
      ? `/admin/generated/certificates/${recordId}/download?format=pdf`
      : `/admin/generated/volunteers/${recordId}/download?format=pdf`;
  return adminFetchBlob(endpoint);
}

export async function fetchCertificateHistory({
  search = '',
  type = 'all',
  status = 'all',
  page = 1,
  pageSize = 20,
} = {}) {
  const params = new URLSearchParams({ page, page_size: pageSize });
  if (search) params.set('search', search);
  if (type && type !== 'all') params.set('type', type);
  if (status && status !== 'all') params.set('status', status);
  return adminFetch(`/admin/cert-management/history?${params.toString()}`);
}

// ============================================================
// NEWSLETTER
// ============================================================

export async function subscribeNewsletter({ email, name, website = '' }) {
  const res = await fetch(`${API_BASE_URL}/newsletter/subscribe`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, name, website }),
  });

  if (!res.ok) {
    let detail = 'Unable to subscribe. Please try again.';
    try {
      const data = await res.json();
      if (data && data.detail) detail = data.detail;
    } catch {
      // ignore JSON parse errors, keep default message
    }
    throw new Error(detail);
  }

  return res.json();
}

export async function fetchNewsletterSubscribers() {
  return adminFetch('/admin/newsletter');
}

export async function exportNewsletterSubscribers() {
  const credentials = getAdminCredentials();
  const response = await fetch(`${API_BASE_URL}/admin/newsletter/export`, {
    headers: {
      Authorization: `Basic ${btoa(`${credentials.username}:${credentials.password}`)}`,
    },
  });

  if (!response.ok) {
    throw new Error('Unable to export newsletter subscribers.');
  }

  return response.blob();
}
