
import { FileText } from 'lucide-react';
import { useSiteSettings } from '../hooks/useSiteSettings';

import usePageMeta from '../hooks/usePageMeta';

export default function Terms() {
  usePageMeta(
    'Terms & Privacy Policy',
    'Terms, conditions, and privacy policy for Piplad Welfare Foundation.'
  );
  const { settings } = useSiteSettings();

  return (
    <div>
      <section style={{ background: '#0f172a', color: '#ffffff', padding: '4rem 0 3rem 0', textAlign: 'center' }}>
        <div className="container">
          <span className="badge badge-green" style={{ marginBottom: '0.75rem' }}>
            <FileText size={16} /> Legal Guidelines
          </span>
          <h1 className="heading-xl" style={{ color: '#ffffff', marginBottom: '0.75rem' }}>Refund & Cancellation Policy</h1>
          <p className="subheading" style={{ color: '#94a3b8', margin: '0 auto' }}>
            Terms governing donations, cancellations, and tax receipt issuance at Piplad Welfare Foundation.
          </p>
        </div>
      </section>

      <section className="section-padding" style={{ background: '#ffffff' }}>
        <div className="container" style={{ maxWidth: '850px' }}>
          <div className="card" style={{ padding: '2.5rem', lineHeight: 1.7, color: '#334155' }}>
            <h2 className="heading-md" style={{ marginBottom: '1rem', color: '#0f172a' }}>1. Donation Refunds</h2>
            <p style={{ marginBottom: '1.5rem' }}>
              Piplad Welfare Foundation takes utmost care in processing donations as per the instructions given by our donors online and offline. However, in the event of an erroneous or duplicate transaction, donors may request a refund within <strong>7 days</strong> of making the contribution.
            </p>

            <h2 className="heading-md" style={{ marginBottom: '1rem', color: '#0f172a' }}>2. How to Request a Refund</h2>
            <p style={{ marginBottom: '1.5rem' }}>
              To request a refund, please write an email to <strong>{settings.email}</strong> with your donation details, transaction reference ID, payment method used, and reason for refund. Refund requests will be reviewed by our board within 5 working days.
            </p>

            <h2 className="heading-md" style={{ marginBottom: '1rem', color: '#0f172a' }}>3. 80G Tax Receipt Terms</h2>
            <p style={{ marginBottom: '1.5rem' }}>
              Once an 80G tax exemption certificate has been issued and filed with the Income Tax Department, the corresponding donation cannot be refunded or cancelled as per Indian statutory tax regulations.
            </p>

            <h2 className="heading-md" style={{ marginBottom: '1rem', color: '#0f172a' }}>4. Cancellation Policy</h2>
            <p>
              Recurring or monthly pledges can be paused or cancelled at any time by sending a request to our support helpline at <strong>{settings.phone}</strong> or emailing support.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
