
import {
  AlertTriangle,
  ArrowLeft,
  Check,
  Loader2,
  Mail,
  Phone,
  QrCode,
  ShieldCheck,
  X,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useSiteSettings, telHref } from '../../hooks/useSiteSettings';

const STATUS_ROW = {
  valid: 'VALID',
  revoked: 'REVOKED',
  expired: 'EXPIRED',
  unknown: 'INVALID',
  loading: 'CHECKING…',
};

function BadgeIcon({ kind }) {
  if (kind === 'loading') return <Loader2 size="34" className="spin" />;
  if (kind === 'valid') return <Check size="34" strokeWidth={3} />;
  if (kind === 'revoked' || kind === 'expired') return <AlertTriangle size="34" />;
  return <X size="34" strokeWidth={3} />;
}

export default function VerificationShell({
  linkTo = '/',
  documentLabel = 'document',
  heading = 'Verification',
  badgeKind = 'unknown',
  description = '',
  qrIdentifier = '',
  children = null,
}) {
  const currentUrl = typeof window !== 'undefined' ? window.location.href : '';
  const { settings } = useSiteSettings();

  return (
    <div className="verify-page">
      <div className="verify-shell">
        <div className="verify-card">
          <div className="verify-brand">
            <img
              loading="lazy"
              decoding="async"
              src="/piplad-logo.png"
              alt="Piplad Welfare Foundation logo"
              className="verify-logo"
            />
            <div>
              <div className="verify-brand-name">PIPLAD WELFARE FOUNDATION</div>
              <div className="verify-brand-tag">Creating Opportunities, Creating Lives</div>
            </div>
          </div>
          <div className="verify-brand-rule" aria-hidden="true" />

          <div className="verify-status" aria-live="polite">
            <div className={`verify-badge ${badgeKind}`} aria-hidden="true">
              <BadgeIcon kind={badgeKind} />
            </div>
            <h1>{heading}</h1>
            <p className="verify-institution">Piplad Welfare Foundation</p>
            {description ? <p className="verify-description">{description}</p> : null}

            <div className={`verify-status-row ${badgeKind}`}>
              <ShieldCheck size={16} />
              Status: {STATUS_ROW[badgeKind] || 'CHECKING'}
            </div>
          </div>

          {children}

          {badgeKind === 'valid' ? (
            <div className="verify-message">
              <ShieldCheck size={20} />
              <span>
                This {documentLabel} has been digitally verified through Piplad Welfare
                Foundation.
              </span>
            </div>
          ) : null}

          <div className="verify-qr">
            <div className="verify-qr-title">
              <QrCode size={15} />
              QR Scan Result
            </div>
            <div className="verify-qr-row">
              <b>Scanned identifier:</b> {qrIdentifier || '—'}
            </div>
            <div className="verify-qr-row">
              <b>Verification page:</b> {currentUrl}
            </div>
          </div>

          <div className="verify-support">
            <h4>Need help with verification?</h4>
            <div className="verify-support-row">
              <Mail size={15} />
              <a href={`mailto:${settings.email}`}>{settings.email}</a>
            </div>
            <div className="verify-support-row">
              <Phone size={15} />
              <a href={telHref(settings.phone)}>{settings.phone}</a>
            </div>
            <div className="verify-support-row" style={{ marginTop: 6 }}>
              Contact our team via the <Link to="/contact">Contact page</Link> for any
              discrepancy or further information.
            </div>
          </div>

          <div className="verify-actions">
            <Link className="back-link" to={linkTo}>
              <ArrowLeft size="16" /> Back to Piplad Welfare Foundation
            </Link>
          </div>

          <div className="verify-footnote">
            This page is the official verification source for {documentLabel}s issued by
            Piplad Welfare Foundation. If a status here differs from the printed badge,
            please contact our team before relying on the document.
          </div>
        </div>
      </div>
    </div>
  );
}