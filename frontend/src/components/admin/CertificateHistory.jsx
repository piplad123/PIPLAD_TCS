import { useEffect, useState } from 'react';
import {
  AlertCircle,
  BadgeCheck,
  ChevronLeft,
  ChevronRight,
  Download,
  Eye,
  Inbox,
  Info,
  Loader2,
  Mail,
  Search,
  ShieldX,
} from 'lucide-react';
import {
  downloadAdminCertificate,
  downloadAdminVolunteerCard,
  fetchCertificateHistory,
  fetchManagedDocumentPdf,
  revokeAdminCertificate,
  revokeAdminVolunteerCard,
  sendManagedDocumentEmail,
} from '../../api';
import '../../styles/admin.css';

const TYPE_OPTIONS = [
  ['all', 'All'],
  ['appreciation', 'Appreciation'],
  ['internship', 'Internship'],
  ['completion', 'Completion'],
  ['participation', 'Participation'],
  ['volunteer', 'Volunteer'],
];

const STATUS_OPTIONS = [
  ['all', 'All'],
  ['valid', 'Valid'],
  ['revoked', 'Revoked'],
];

const PAGE_SIZE = 8;

function ErrorMessage({ message }) {
  if (!message) return null;
  return (
    <div className="adm-alert adm-alert-error" role="alert">
      <AlertCircle size={17} />
      <span>{message}</span>
    </div>
  );
}

function InfoMessage({ message }) {
  if (!message) return null;
  return (
    <div className="adm-alert adm-alert-success" role="status">
      <Info size={17} />
      <span>{message}</span>
    </div>
  );
}

function formatDate(value) {
  if (!value) return '—';
  const parts = String(value).split('-');
  if (parts.length !== 3) return value;
  const [year, month, day] = parts;
  return `${day}/${month}/${year}`;
}

function StatusBadge({ status }) {
  const valid = status === 'valid';
  return (
    <span className={`adm-pill ${valid ? 'adm-pill-valid' : 'adm-pill-revoked'}`}>
      {valid ? 'Valid' : 'Revoked'}
    </span>
  );
}

const TYPE_PILLS = {
  appreciation: 'adm-pill-blue',
  internship: 'adm-pill-violet',
  completion: 'adm-pill-emerald',
  participation: 'adm-pill-amber',
  volunteer: 'adm-pill-cyan',
  certificate: 'adm-pill-slate',
};

function TypePill({ label }) {
  const cls =
    TYPE_PILLS[String(label).toLowerCase()] ||
    'adm-pill-slate';

  return (
    <span className={`adm-pill adm-pill-kind ${cls}`}>
      {label}
    </span>
  );
}

export default function CertificateHistory() {
  const [search, setSearch] = useState('');
  const [type, setType] = useState('all');
  const [status, setStatus] = useState('all');
  const [page, setPage] = useState(1);
  const [data, setData] = useState({ items: [], total: 0, page: 1, page_size: PAGE_SIZE });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [busy, setBusy] = useState('');

  const load = async (queryPage = page) => {
    setLoading(true);
    setError('');
    try {
      const result = await fetchCertificateHistory({
        search: search.trim(),
        type,
        status,
        page: queryPage,
        pageSize: PAGE_SIZE,
      });
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(page);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, type, status]);

  const handleSearch = () => {
    setPage(1);
    load(1);
  };

  const totalPages = Math.max(1, Math.ceil(data.total / PAGE_SIZE));
  const from = data.total === 0 ? 0 : (data.page - 1) * PAGE_SIZE + 1;
  const to = Math.min(data.page * PAGE_SIZE, data.total);

  const openPdf = async (row) => {
    setBusy(`view-${row.record_id}`);
    try {
      const blob = await fetchManagedDocumentPdf(row.kind, row.record_id);
      window.open(URL.createObjectURL(blob), '_blank');
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy('');
    }
  };

  const downloadPdf = async (row) => {
    setBusy(`download-${row.record_id}`);
    try {
      if (row.kind === 'volunteer') {
        await downloadAdminVolunteerCard(row.record_id, 'pdf');
      } else {
        await downloadAdminCertificate(row.record_id, 'pdf');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy('');
    }
  };

  const sendEmail = async (row) => {
    setBusy(`send-${row.record_id}`);
    setError('');
    setInfo('');
    try {
      const result = await sendManagedDocumentEmail(row.kind, row.record_id);
      if (result.sent) {
        setInfo(result.message);
      } else {
        setError(result.message);
      }
      load(page);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy('');
    }
  };

  const revoke = async (row) => {
    const label = row.document_number;
    // eslint-disable-next-line no-alert
    const confirmed = window.confirm(`Revoke ${label}? This makes it appear revoked on the public verify page.`);
    if (!confirmed) return;
    setBusy(`revoke-${row.record_id}`);
    setError('');
    setInfo('');
    try {
      if (row.kind === 'volunteer') {
        await revokeAdminVolunteerCard(row.record_id);
      } else {
        await revokeAdminCertificate(row.record_id);
      }
      setInfo(`${label} was revoked.`);
      load(page);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy('');
    }
  };

  return (
    <div className="adm">
      <section className="card adm-panel">
        <h2 className="adm-heading">
          <BadgeCheck size={20} /> Certificate History
        </h2>

        <ErrorMessage message={error} />
        <InfoMessage message={info} />

        <div className="adm-toolbar">
          <form
            onSubmit={(event) => {
              event.preventDefault();
              handleSearch();
            }}
          >
            <label className="adm-filter-label" htmlFor="ch-search">
              Search
            </label>
            <div className="adm-search">
              <Search size={16} />
              <input
                id="ch-search"
                className="adm-input"
                type="search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search name, number or email"
              />
            </div>
          </form>

          <div className="adm-filter">
            <label className="adm-filter-label" htmlFor="ch-type">
              Certificate Type
            </label>
            <select
              id="ch-type"
              className="adm-input"
              value={type}
              onChange={(event) => {
                setType(event.target.value);
                setPage(1);
              }}
            >
              {TYPE_OPTIONS.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div className="adm-filter">
            <label className="adm-filter-label" htmlFor="ch-status">
              Status
            </label>
            <select
              id="ch-status"
              className="adm-input"
              value={status}
              onChange={(event) => {
                setStatus(event.target.value);
                setPage(1);
              }}
            >
              {STATUS_OPTIONS.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {loading ? (
          <div className="adm-loading">
            <Loader2 size={18} className="spin" /> Loading records…
          </div>
        ) : data.items.length === 0 ? (
          <div className="adm-empty">
            <span className="adm-empty-icon">
              <Inbox size={22} />
            </span>
            <strong>No records found</strong>
            <small>Try adjusting the search or filters; generated certificates appear here.</small>
          </div>
        ) : (
          <div className="adm-table-wrap">
            <table className="adm-table">
              <thead>
                <tr>
                  <th>Certificate</th>
                  <th>Recipient</th>
                  <th>Program</th>
                  <th>Issue Date</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((row) => (
                  <tr key={`${row.kind}-${row.record_id}`}>
                    <td className="adm-num">
                      <div>{row.document_number}</div>
                      <div className="adm-sub" style={{ marginTop: '0.25rem' }}>
                        <TypePill label={row.type_label} />
                      </div>
                    </td>
                    <td style={{ whiteSpace: 'nowrap' }}>
                      <div className="adm-recipient">{row.recipient_name}</div>
                      {row.email ? (
                        <div className={`adm-sub ${row.email_sent ? 'adm-sub-sent' : ''}`}>
                          {row.email_sent ? '✓ Email sent' : 'Email not sent'}
                        </div>
                      ) : (
                        <div className="adm-sub">No email on record</div>
                      )}
                    </td>
                    <td>{row.program || '—'}</td>
                    <td style={{ whiteSpace: 'nowrap' }}>
                      <b>{formatDate(row.issue_date)}</b>
                    </td>
                    <td style={{ whiteSpace: 'nowrap' }}>
                      <StatusBadge status={row.status} />
                    </td>
                    <td>
                      <div className="adm-actions">
                        <button
                          type="button"
                          title="View PDF"
                          className="adm-icon-btn"
                          onClick={() => openPdf(row)}
                          disabled={busy === `view-${row.record_id}`}
                        >
                          {busy === `view-${row.record_id}` ? (
                            <Loader2 size={14} className="spin" />
                          ) : (
                            <Eye size={14} />
                          )}
                        </button>
                        <button
                          type="button"
                          title="Download PDF"
                          className="adm-icon-btn adm-icon-btn-blue"
                          onClick={() => downloadPdf(row)}
                          disabled={busy === `download-${row.record_id}`}
                        >
                          {busy === `download-${row.record_id}` ? (
                            <Loader2 size={14} className="spin" />
                          ) : (
                            <Download size={14} />
                          )}
                        </button>
                        <button
                          type="button"
                          title={row.email ? 'Email the official PDF to the recipient' : 'No recipient email on this record'}
                          className="adm-icon-btn adm-icon-btn-email"
                          onClick={() => sendEmail(row)}
                          disabled={busy === `send-${row.record_id}` || !row.email}
                        >
                          {busy === `send-${row.record_id}` ? (
                            <Loader2 size={14} className="spin" />
                          ) : (
                            <Mail size={14} />
                          )}
                        </button>
                        {row.verified_url ? (
                          <a
                            href={row.verified_url}
                            target="_blank"
                            rel="noreferrer"
                            title="Open public verify page"
                            className="adm-icon-btn adm-icon-btn-verify"
                          >
                            <BadgeCheck size={14} />
                          </a>
                        ) : null}
                        {row.status === 'valid' ? (
                          <button
                            type="button"
                            title="Revoke"
                            className="adm-icon-btn adm-icon-btn-danger"
                            onClick={() => revoke(row)}
                            disabled={busy === `revoke-${row.record_id}`}
                          >
                            {busy === `revoke-${row.record_id}` ? (
                              <Loader2 size={14} className="spin" />
                            ) : (
                              <ShieldX size={14} />
                            )}
                          </button>
                        ) : null}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!loading && data.total > 0 ? (
          <div className="adm-pagination">
            <span>
              Showing {from}–{to} of {data.total} records
            </span>
            <div className="adm-pager">
              <button
                type="button"
                className="adm-btn adm-btn-ghost"
                disabled={page <= 1}
                onClick={() => setPage((prev) => Math.max(1, prev - 1))}
              >
                <ChevronLeft size={15} /> Prev
              </button>
              <span className="adm-pager-info">
                Page {data.page} of {totalPages}
              </span>
              <button
                type="button"
                className="adm-btn adm-btn-ghost"
                disabled={page >= totalPages}
                onClick={() => setPage((prev) => prev + 1)}
              >
                Next <ChevronRight size={15} />
              </button>
            </div>
          </div>
        ) : null}
      </section>
    </div>
  );
}