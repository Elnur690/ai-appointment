import React, { useEffect } from 'react';
import { useDataStore } from '../store/dataStore';
import { useAuthStore } from '../store/authStore';
import { CreditCard, Banknote, ShieldCheck, CheckCircle2, XCircle } from 'lucide-react';

const GATEWAY_ICONS = {
  cash: Banknote,
  payriff: CreditCard,
  paymegate: ShieldCheck,
  paymengate: ShieldCheck,
};

const PaymentGateways = () => {
  const { paymentGateways, fetchPaymentGateways, togglePaymentGateway } = useDataStore();
  const { language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';

  useEffect(() => {
    fetchPaymentGateways();
  }, [fetchPaymentGateways]);

  return (
    <div className="page-container">
      <div className="flex-between" style={{ marginBottom: '2rem' }}>
        <div>
          <h1>{isAz ? 'Ödəniş Şlüzlərinin İdarə Edilməsi' : 'Payment Gateways Control'}</h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            {isAz
              ? 'Randevu.vip platformasındakı bütün bizneslər üçün ödəniş şlüzlərini (Nağd, Payriff, Paymegate) aktiv və ya deaktiv edin.'
              : 'Enable or disable payment gateways platform-wide across all businesses on Randevu.vip.'}
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.5rem' }}>
        {paymentGateways.map((gw, idx) => {
          const IconComponent = GATEWAY_ICONS[gw.provider] || CreditCard;
          const isEnabled = Boolean(gw.enabled);

          return (
            <div
              key={gw.provider}
              className="glass-card"
              style={{
                padding: '2rem',
                display: 'flex',
                flexDirection: 'column',
                border: isEnabled ? '1px solid rgba(16, 185, 129, 0.35)' : '1px solid var(--border-color)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                  <div
                    style={{
                      width: '44px',
                      height: '44px',
                      borderRadius: '10px',
                      background: isEnabled ? 'rgba(16, 185, 129, 0.15)' : 'rgba(255,255,255,0.05)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <IconComponent size={24} color={isEnabled ? 'var(--success)' : 'var(--text-secondary)'} />
                  </div>
                  <div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--primary-start)', textTransform: 'uppercase' }}>
                      {isAz ? `Şlüz #${idx + 1}` : `Gateway #${idx + 1}`} • {gw.provider}
                    </div>
                    <h2 style={{ fontSize: '1.3rem', margin: '0.15rem 0 0' }}>{gw.name}</h2>
                  </div>
                </div>

                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.35rem',
                    padding: '0.3rem 0.75rem',
                    borderRadius: '999px',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    background: isEnabled ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                    color: isEnabled ? 'var(--success)' : 'var(--error)',
                  }}
                >
                  {isEnabled ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
                  {isEnabled ? (isAz ? 'Aktiv' : 'Enabled') : isAz ? 'Deaktiv' : 'Disabled'}
                </span>
              </div>

              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6, flex: 1, marginBottom: '1.5rem' }}>
                {gw.description}
              </p>

              <div
                style={{
                  paddingTop: '1rem',
                  borderTop: '1px solid var(--border-color)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {gw.requires_credentials
                    ? gw.env_configured
                      ? isAz
                        ? `.env konfiqurasiyası: Aktiv (${gw.env_hint})`
                        : `.env configured (${gw.env_hint})`
                      : isAz
                      ? `.env açarı təyin edilməyib (${gw.provider === 'paymegate' ? 'PAYMEGATE_API_KEY' : 'PAYRIFF_SECRET_KEY'})`
                      : `Set ${gw.provider === 'paymegate' ? 'PAYMEGATE_API_KEY' : 'PAYRIFF_SECRET_KEY'} in .env`
                    : isAz
                    ? 'Daxili kassa / nağd ödəniş üsulu'
                    : 'Built-in Ledger Method'}
                </span>

                <button
                  type="button"
                  className={isEnabled ? 'btn btn-secondary' : 'btn btn-primary'}
                  onClick={() => togglePaymentGateway(gw.provider, !isEnabled)}
                  style={{ minWidth: '150px', justifyContent: 'center' }}
                >
                  {isEnabled
                    ? isAz
                      ? 'Şlüzü Söndür'
                      : 'Disable Gateway'
                    : isAz
                    ? 'Şlüzü Aktivləşdir'
                    : 'Enable Gateway'}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PaymentGateways;
