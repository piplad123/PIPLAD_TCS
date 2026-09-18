import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { verifyCertificate } from '../api';
import VerificationShell from '../components/verify/VerificationShell';
import '../styles/verify.css';

const TYPE_LABELS = {
  appreciation: 'Certificate of Appreciation',
  completion: 'Certificate of Completion',
  internship: 'Certificate of Internship',
  participation: 'Certificate of Participation',
  certificate: 'Certificate',
};

function Field({ label, value, full }) {
  if (!value) return null;
  return (
    <div className={`verify-field ${full ? 'full' : ''}`}>
      <span>{label}</span>
      <b>{value}</b>
    </div>
  );
}

function formatDate(value) {
  if (!value) return null;
  const parts = String(value).split('-');
  if (parts.length !== 3) return value;
  const [year, month, day] = parts;
  return `${day}/${month}/${year}`;
}

function RelevantDates({ startingDate, endDate, competitionDate }) {
  const items = [];
  if (startingDate) items.push(['Program Start', startingDate]);
  if (endDate) items.push(['Program End', endDate]);
  if (competitionDate) items.push(['Competition Date', competitionDate]);
  if (items.length === 0) return null;
  return (
    <div className="verify-dates">
      <span className="verify-dates-label">Relevant Dates</span>
      {items.map(([label, value]) => (
        <div key={label} className="verify-dates-item">
          <b>{label}</b>
          <b>{formatDate(value)}</b>
        </div>
      ))}
    </div>
  );
}

import usePageMeta from '../hooks/usePageMeta';

export default function VerifyCertificate() {
  usePageMeta(
    'Verify Certificate',
    'Verify a certificate issued by Piplad Welfare Foundation.'
  );
  const { identifier } = useParams();
  const [state, setState] = useState({ loading: true, data: null, error: null });

  useEffect(() => {
    let active = true;
    verifyCertificate(identifier)
      .then((data) => active && setState({ loading: false, data, error: null }))
      .catch((err) => active && setState({ loading: false, data: null, error: err.message }));
    return () => { active = false; };
  }, [identifier]);

  if (state.loading) {
    return (
      <VerificationShell
        documentLabel="certificate"
        heading="Verifying…"
        badgeKind="loading"
        qrIdentifier={identifier}
      />
    );
  }

  const data = state.data;

  if (state.error || !data) {
    return (
      <VerificationShell
        documentLabel="certificate"
        heading="Certificate Not Found"
        badgeKind="unknown"
        description={state.error || 'We were unable to validate this certificate with the identifier provided.'}
        qrIdentifier={identifier}
      />
    );
  }

  if (data.valid && data.recipient_name !== 'Unknown') {
    return (
      <VerificationShell
        documentLabel="certificate"
        heading="Certificate Verified"
        badgeKind="valid"
        qrIdentifier={identifier}
      >
        <div className="verify-details">
          <Field label="Recipient" value={data.recipient_name} full />
          <Field label="Certificate Type" value={TYPE_LABELS[data.certificate_type] || data.certificate_type} />
          <Field label="Program" value={data.program_name} full />
          <Field label="Certificate Number" value={data.certificate_number} />
          <Field label="Issue Date" value={formatDate(data.issue_date)} />
          <Field label="Issued By" value={data.issued_by} full />
        </div>
        <RelevantDates
          startingDate={data.starting_date}
          endDate={data.end_date}
          competitionDate={data.competition_date}
        />
        <Field label="Organisation" value={data.organisation_name} full />
        <Field label="Competition Location" value={data.competition_location} full />
      </VerificationShell>
    );
  }

  if (data.revoked) {
    return (
      <VerificationShell
        documentLabel="certificate"
        heading="Certificate Revoked"
        badgeKind="revoked"
        description={data.reason || 'This certificate has been revoked by the issuer.'}
        qrIdentifier={identifier}
      >
        <div className="verify-details">
          <Field label="Certificate Number" value={data.certificate_number} full />
        </div>
      </VerificationShell>
    );
  }

  if (data.expired) {
    return (
      <VerificationShell
        documentLabel="certificate"
        heading="Certificate Expired"
        badgeKind="expired"
        description={data.reason || 'This certificate is no longer valid.'}
        qrIdentifier={identifier}
      />
    );
  }

  return (
    <VerificationShell
      documentLabel="certificate"
      heading="Certificate Not Found"
      badgeKind="unknown"
      description={data.reason || 'We were unable to validate this certificate with the identifier provided.'}
      qrIdentifier={identifier}
    />
  );
}