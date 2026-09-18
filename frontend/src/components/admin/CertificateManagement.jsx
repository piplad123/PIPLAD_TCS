import { useEffect, useState } from 'react';
import {
  AlertCircle,
  Award,
  BadgeCheck,
  Download,
  Eye,
  FileText,
  GraduationCap,
  Info,
  Loader2,
  Mail,
  PlusCircle,
  RefreshCw,
  Send,
  ShieldCheck,
  Trophy,
} from 'lucide-react';
import {
  downloadAdminCertificate,
  downloadAdminVolunteerCard,
  fetchCertManagementStats,
  fetchManagedDocumentPdf,
  generateManagedDocument,
  previewManagedDocument,
  resolveMediaUrl,
  sendManagedDocumentEmail,
} from '../../api';
import '../../styles/admin.css';

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

function FieldControl({
  field: [key, label, control, , options],
  form,
  onPhotoChange,
  photoPreview,
  setField,
}) {
  return (
    <div>
      <label className="adm-label" htmlFor={`cmf-${key}`}>
        {label}
      </label>
      {control === 'file' ? (
        <>
          <input
            id={`cmf-${key}`}
            className="adm-input"
            type="file"
            accept="image/jpeg,image/jpg,image/png,image/webp"
            onChange={onPhotoChange}
          />
          {photoPreview ? (
            <img className="adm-photo" src={photoPreview} alt="Photo preview" />
          ) : null}
        </>
      ) : control === 'select' ? (
        <select
          id={`cmf-${key}`}
          className="adm-input"
          value={form[key] || 'issued'}
          onChange={(event) => setField(key, event.target.value)}
        >
          {(options || []).map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      ) : (
        <input
          id={`cmf-${key}`}
          className="adm-input"
          type={control}
          value={form[key] || ''}
          onChange={(event) => setField(key, event.target.value)}
          placeholder={label}
        />
      )}
    </div>
  );
}

const TYPE_DEFS = [
  {
    value: 'appreciation',
    label: 'Appreciation',
    blurb: 'Certificate of Appreciation',
    icon: Award,
  },
  {
    value: 'internship',
    label: 'Internship',
    blurb: 'Certificate of Internship',
    icon: GraduationCap,
  },
  {
    value: 'completion',
    label: 'Completion',
    blurb: 'Certificate of Completion',
    icon: Trophy,
  },
  {
    value: 'participation',
    label: 'Participation',
    blurb: 'Certificate of Participation',
    icon: FileText,
  },
  {
    value: 'volunteer',
    label: 'Volunteer ID Card',
    blurb: 'CR80 wallet-size ID card',
    icon: BadgeCheck,
  },
];

const TYPE_FIELDS = {
  appreciation: {
    Recipient: [
      ['first_name', 'First Name', 'text', true],
      ['last_name', 'Last Name', 'text', false],
      ['recipient_email', 'Recipient Email', 'email', true],
    ],
    Credential: [['program_name', 'Program / Event', 'text', true]],
    Dates: [['issue_date', 'Issue Date', 'date', false]],
  },
  internship: {
    Recipient: [
      ['first_name', 'First Name', 'text', true],
      ['last_name', 'Last Name', 'text', false],
      ['recipient_email', 'Recipient Email', 'email', true],
    ],
    Credential: [['program_name', 'Program / Internship', 'text', true]],
    Dates: [
      ['starting_date', 'Starting Date', 'date', true],
      ['end_date', 'End Date', 'date', true],
      ['issue_date', 'Issue Date', 'date', false],
    ],
  },
  completion: {
    Recipient: [
      ['first_name', 'First Name', 'text', true],
      ['last_name', 'Last Name', 'text', false],
      ['recipient_email', 'Recipient Email', 'email', true],
    ],
    Credential: [
      ['program_name', 'Program / Competition', 'text', true],
      ['organisation_name', 'Organisation Name', 'text', true],
    ],
    Dates: [
      ['competition_date', 'Competition Date', 'date', true],
      ['issue_date', 'Issue Date', 'date', false],
    ],
  },
  participation: {
    Recipient: [
      ['first_name', 'First Name', 'text', true],
      ['last_name', 'Last Name', 'text', false],
      ['recipient_email', 'Recipient Email', 'email', true],
    ],
    Credential: [['program_name', 'Program / Event', 'text', true]],
    Dates: [['issue_date', 'Issue Date', 'date', false]],
  },
  volunteer: {
    Recipient: [
      ['first_name', 'First Name', 'text', true],
      ['last_name', 'Last Name', 'text', false],
      ['recipient_email', 'Email', 'email', true],
    ],
    Contact: [
      ['phone', 'Phone', 'text', true],
      ['designation', 'Designation / Interest Area', 'text', true],
    ],
    Dates: [['issue_date', 'Joining Date', 'date', false]],
    Administration: [
      ['status', 'Status', 'select', false, ['issued', 'accepted', 'active']],
      ['photo', 'Photo', 'file', false],
    ],
  },
};

const allFields = (documentType) =>
  Object.values(TYPE_FIELDS[documentType] || {}).flat();

const requiredField = (field) => field[3] === true;
const humanLabel = (field) => field[1];

function certificatePayload(documentType, form) {
  const keys = allFields(documentType)
    .filter((field) => field[2] !== 'file')
    .map((field) => field[0]);
  return Object.fromEntries(
    keys
      .filter((key) => form[key] !== '')
      .map((key) => [key, form[key]])
  );
}

const STAT_DEFS = [
  ['total_certificates', 'Total Certificates', ShieldCheck],
  ['by_type.appreciation', 'Appreciation', Award],
  ['by_type.internship', 'Internship', GraduationCap],
  ['by_type.completion', 'Completion', Trophy],
  ['by_type.participation', 'Participation', FileText],
  ['total_volunteer_cards', 'Volunteer IDs', BadgeCheck],
];

function statValue(stats, path) {
  const [group, key] = path.split('.');
  return key ? (stats[group] || {})[key] : stats[group];
}

function StatCard({ icon: Icon, label, value }) {
  return (
    <div className="adm-stat card">
      <span className="adm-stat-icon">
        <Icon size={20} />
      </span>
      <div>
        <div className="adm-stat-label">{label}</div>
        <strong className="adm-stat-value">{value ?? 0}</strong>
      </div>
    </div>
  );
}

export default function CertificateManagement() {
  const [stats, setStats] = useState({
    total_certificates: 0,
    by_type: { appreciation: 0, internship: 0, completion: 0, participation: 0 },
    total_volunteer_cards: 0,
  });
  const [documentType, setDocumentType] = useState('appreciation');
  const [form, setForm] = useState({});
  const [photoPreview, setPhotoPreview] = useState('');
  const [previewUrl, setPreviewUrl] = useState('');
  const [previewing, setPreviewing] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [sendingEmail, setSendingEmail] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [loadingStats, setLoadingStats] = useState(true);

  const loadStats = async () => {
    try {
      setStats(await fetchCertManagementStats());
    } catch (err) {
      if (err.code === 'ADMIN_AUTH_REQUIRED') throw err;
      setError(err.message);
    } finally {
      setLoadingStats(false);
    }
  };

  useEffect(() => {
    loadStats().catch(() => {});
  }, []);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      if (photoPreview) URL.revokeObjectURL(photoPreview);
    };
  }, [previewUrl, photoPreview]);

  const setField = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const chooseType = (value) => {
    setDocumentType(value);
    setError('');
    setForm({});
    setPreviewUrl('');
    setPhotoPreview('');
  };

  const onPhotoChange = (event) => {
    const file = event.target.files && event.target.files[0];
    if (!file) {
      setField('photo_data_url', '');
      setPhotoPreview('');
      return;
    }
    if (!/^image\/(jpe?g|png|webp)$/.test(file.type)) {
      setError('Photo must be JPG, PNG or WebP.');
      return;
    }
    if (photoPreview) URL.revokeObjectURL(photoPreview);
    setPhotoPreview(URL.createObjectURL(file));
    const reader = new FileReader();
    reader.onload = () => setField('photo_data_url', reader.result);
    reader.readAsDataURL(file);
  };

  const validateRequired = () => {
    const missing = allFields(documentType)
      .filter((field) => requiredField(field))
      .filter((field) => !(form[field[0]] && String(form[field[0]]).trim()))
      .map(humanLabel);
    if (missing.length) {
      setError(`Please fill in: ${missing.join(', ')}.`);
      setInfo('');
      return false;
    }
    setError('');
    return true;
  };

  const handlePreview = async (event) => {
    event.preventDefault();
    if (!validateRequired()) return;
    setPreviewing(true);
    setError('');
    setInfo('');
    const payload = {
      document_type: documentType,
      ...certificatePayload(documentType, form),
      ...(documentType === 'volunteer' && form.photo_data_url
        ? { photo_data_url: form.photo_data_url }
        : {}),
    };
    try {
      const blob = await previewManagedDocument(payload);
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      setPreviewUrl(URL.createObjectURL(blob));
      setInfo('Preview shows how the document will look. Nothing has been saved yet.');
    } catch (err) {
      setError(err.message);
    } finally {
      setPreviewing(false);
    }
  };

  const handleGenerate = async (event) => {
    event.preventDefault();
    if (!validateRequired()) return;
    setGenerating(true);
    setError('');
    setInfo('');
    const payload = {
      document_type: documentType,
      ...certificatePayload(documentType, form),
      ...(documentType === 'volunteer' && form.photo_data_url
        ? { photo_data_url: form.photo_data_url }
        : {}),
    };
    try {
      const data = await generateManagedDocument(payload);
      setResult(data);
      setPreviewUrl('');
      setInfo(
        `${data.kind === 'volunteer' ? 'Volunteer ID card' : 'Certificate'} created and saved.`
      );
      loadStats().catch(() => {});
    } catch (err) {
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  };

  const openPdf = async () => {
    try {
      const blob = await fetchManagedDocumentPdf(result.kind, result.record_id);
      window.open(URL.createObjectURL(blob), '_blank');
    } catch (err) {
      setError(err.message);
    }
  };

  const downloadPdf = async () => {
    try {
      if (result.kind === 'certificate') {
        await downloadAdminCertificate(result.record_id, 'pdf');
      } else {
        await downloadAdminVolunteerCard(result.record_id, 'pdf');
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSendEmail = async () => {
    if (!result) return;
    setSendingEmail(true);
    setError('');
    setInfo('');
    try {
      const data = await sendManagedDocumentEmail(result.kind, result.record_id);
      if (data.sent) {
        setInfo(data.message);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSendingEmail(false);
    }
  };

  const handleGenerateAgain = () => {
    setResult(null);
    setForm({});
    setPhotoPreview('');
    setPreviewUrl('');
    setError('');
    setInfo('');
  };

  const fieldsets = Object.entries(TYPE_FIELDS[documentType] || {});

  return (
    <div className="adm">
      {loadingStats ? (
        <div className="adm-stats">
          {Array.from({ length: 6 }).map((_, index) => (
            <div className="adm-stat card" key={index}>
              <div className="adm-stat-icon adm-skeleton" style={{ width: 42, height: 42 }} />
              <div style={{ flex: 1 }}>
                <div className="adm-skeleton" style={{ width: '55%', marginBottom: 6 }} />
                <div className="adm-skeleton" style={{ width: '38%' }} />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="adm-stats">
          {STAT_DEFS.map(([path, label, Icon]) => (
            <StatCard key={path} icon={Icon} label={label} value={statValue(stats, path)} />
          ))}
        </div>
      )}

      <section className="card adm-panel">
        <h2 className="adm-heading">
          <PlusCircle size={20} /> Generate {documentType === 'volunteer' ? 'Volunteer ID Card' : 'Certificate'}
        </h2>

        <ErrorMessage message={error} />
        <InfoMessage message={info} />

        <div className="adm-type-grid">
          {TYPE_DEFS.map((type) => {
            const Icon = type.icon;
            const active = documentType === type.value;
            return (
              <button
                key={type.value}
                type="button"
                className="adm-type-card"
                aria-pressed={active}
                onClick={() => chooseType(type.value)}
              >
                <span className="adm-type-icon">
                  <Icon size={17} />
                </span>
                <span>
                  {type.label}
                  <span className="adm-sub">{type.blurb}</span>
                </span>
              </button>
            );
          })}
        </div>

        <form onSubmit={handlePreview}>
          {fieldsets.map(([groupName, fields]) => (
            <div className="adm-fieldset" key={groupName}>
              <p className="adm-fieldset-title">{groupName}</p>
              <div className="adm-field-grid">
                {fields.map((field) => (
                  <FieldControl
                    key={field[0]}
                    field={field}
                    form={form}
                    setField={setField}
                    onPhotoChange={onPhotoChange}
                    photoPreview={photoPreview}
                  />
                ))}
              </div>
            </div>
          ))}

          <p className="adm-hint">
            {documentType === 'volunteer'
              ? 'The volunteer ID number is auto-generated on save (PWF-YEAR-NNNN).'
              : 'The certificate number is auto-generated on save (e.g. PWF-APPR-2026-0001).'}
          </p>

          <div style={{ display: 'flex', gap: '.75rem', flexWrap: 'wrap' }}>
            <button type="submit" className="adm-btn adm-btn-ghost" disabled={previewing}>
              {previewing ? <Loader2 size={16} className="spin" /> : <Eye size={16} />}
              Preview
            </button>
            <button
              type="button"
              onClick={handleGenerate}
              className="adm-btn adm-btn-primary"
              disabled={generating}
            >
              {generating ? <Loader2 size={16} className="spin" /> : <Award size={16} />}
              Generate {documentType === 'volunteer' ? 'ID Card' : 'Certificate'}
            </button>
          </div>
        </form>
      </section>

      {previewUrl ? (
        <section className="card adm-panel">
          <div className="adm-preview-head">
            <span className="adm-preview-title">
              <Eye size={18} /> Preview
            </span>
            <span className="adm-chip adm-chip-amber">Not saved</span>
          </div>
          <img className="adm-preview-img" src={previewUrl} alt="Document preview" />
        </section>
      ) : null}

      {result ? (
        <section className="card adm-panel">
          <div className="adm-alert adm-alert-success">
            <ShieldCheck size={19} />
            <div>
              <strong>
                {result.kind === 'volunteer' ? 'Volunteer ID card' : 'Certificate'} generated and
                saved
              </strong>
              <div style={{ marginTop: '.2rem' }}>
                {result.kind === 'volunteer' ? 'Volunteer ID' : 'Certificate Number'}:{' '}
                <strong>{result.document_number}</strong> · Recipient:{' '}
                <strong>{result.recipient_name}</strong>
              </div>
            </div>
          </div>

          <dl className="adm-result-meta">
            <div className="adm-meta-item">
              <dt>{result.kind === 'volunteer' ? 'Volunteer ID' : 'Certificate Number'}</dt>
              <dd>{result.document_number}</dd>
            </div>
            <div className="adm-meta-item">
              <dt>Recipient</dt>
              <dd>{result.recipient_name}</dd>
            </div>
            {result.verified_url ? (
              <div className="adm-meta-item">
                <dt>Public verify link</dt>
                <dd>
                  <a href={result.verified_url} target="_blank" rel="noreferrer">
                    {result.verified_url}
                  </a>
                </dd>
              </div>
            ) : null}
          </dl>

          {result.rendered_url ? (
            <img
              className="adm-result-img"
              src={resolveMediaUrl(result.rendered_url)}
              alt="Generated document"
            />
          ) : null}

          <div style={{ display: 'flex', gap: '.65rem', flexWrap: 'wrap' }}>
            <button type="button" onClick={openPdf} className="adm-btn adm-btn-ghost">
              <Eye size={16} /> View PDF
            </button>
            <button type="button" onClick={downloadPdf} className="adm-btn adm-btn-ghost">
              <Download size={16} /> Download PDF
            </button>
            <button
              type="button"
              onClick={handleSendEmail}
              className="adm-btn adm-btn-primary"
              disabled={sendingEmail}
            >
              {sendingEmail ? <Loader2 size={16} className="spin" /> : <Send size={16} />}
              Send Email
            </button>
            <button
              type="button"
              onClick={handleGenerateAgain}
              className="adm-btn adm-btn-ghost"
            >
              <RefreshCw size={16} /> Generate Again
            </button>
          </div>
          {result.recipient_email ? (
            <p className="adm-email-note">
              <Mail size={14} style={{ verticalAlign: '-2px', marginRight: '.3rem' }} />
              Will be emailed to {result.recipient_email} when you send it.
            </p>
          ) : null}
        </section>
      ) : null}
    </div>
  );
}