import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { BrandLogo } from '../components/common/BrandLogo';
import api from '../api/client';
import { Copy, CheckCircle2, LogOut, Users, DollarSign, Percent, Wallet } from 'lucide-react';

const PartnerPortal = () => {
  const { user, logout, language, setLanguage } = useAuthStore();
  const navigate = useNavigate();
  const isAz = (language || 'az') !== 'en';
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!user || user.role !== 'reseller') {
      navigate('/login');
      return;
    }
    api
      .get('/resellers/me')
      .then((res) => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [user, navigate]);

  const handleCopy = () => {
    if (data?.partner?.referral_url && navigator.clipboard) {
      navigator.clipboard.writeText(data.partner.referral_url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'var(--text-secondary)' }}>{isAz ? 'Partnyor portalı yüklənir...' : 'Loading Partner Portal...'}</p>
      </div>
    );
  }

  const partner = data?.partner;
  const businesses = data?.referred_businesses || [];
  const payouts = data?.payouts || [];

  return (
    <div style={{ minHeight: '100vh', maxWidth: '1200px', margin: '0 auto', padding: '1.5rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <BrandLogo size={36} fontSize="1.45rem" />
          <span className="badge badge-gold">{isAz ? 'Partnyor Portalı' : 'Partner Portal'}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setLanguage(isAz ? 'en' : 'az')}
          >
            {isAz ? 'EN' : 'AZ'}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => {
              logout();
              navigate('/login');
            }}
          >
            <LogOut size={16} />
            {isAz ? 'Çıxış' : 'Logout'}
          </button>
        </div>
      </header>

      {!partner ? (
        <div className="glass-card" style={{ padding: '2rem', textAlign: 'center' }}>
          <p>{isAz ? 'Partnyor məlumatları tapılmadı.' : 'Partner profile not found.'}</p>
        </div>
      ) : (
        <>
          <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h2 style={{ marginBottom: '0.25rem' }}>{partner.name} {partner.company_name ? `(${partner.company_name})` : ''}</h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>
                {isAz ? 'Sizin referal linkiniz:' : 'Your referral link:'}{' '}
                <code style={{ color: 'var(--primary)' }}>{partner.referral_url}</code>
              </p>
            </div>
            <button type="button" className="btn btn-gold" onClick={handleCopy}>
              {copied ? <CheckCircle2 size={16} /> : <Copy size={16} />}
              {copied ? (isAz ? 'Kopyalandı' : 'Copied') : isAz ? 'Linki Kopyala' : 'Copy Referral Link'}
            </button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 220px), 1fr))', gap: '1rem', marginBottom: '2rem' }}>
            <div className="glass-card" style={{ padding: '1.25rem' }}>
              <Users size={20} color="var(--primary)" />
              <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                {isAz ? 'Aktiv Bizneslər' : 'Active Businesses'}
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800 }}>
                {partner.active_businesses_count} / {partner.referred_businesses_count}
              </div>
            </div>
            <div className="glass-card" style={{ padding: '1.25rem' }}>
              <Percent size={20} color="var(--emerald)" />
              <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                {isAz ? 'Komissiya Dərəcəsi' : 'Commission Rate'}
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800 }}>{partner.commission_rate_percent}%</div>
            </div>
            <div className="glass-card" style={{ padding: '1.25rem' }}>
              <DollarSign size={20} color="var(--gold)" />
              <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                {isAz ? 'Aylıq Komissiya' : 'Monthly Commission'}
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800 }}>{Number(partner.monthly_commission_azn).toFixed(2)} AZN</div>
            </div>
            <div className="glass-card" style={{ padding: '1.25rem' }}>
              <Wallet size={20} color="var(--warning)" />
              <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                {isAz ? 'Gözləyən Ödəniş' : 'Pending Payout'}
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800 }}>{Number(partner.pending_payout_azn).toFixed(2)} AZN</div>
            </div>
          </div>

          <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>{isAz ? 'Qoşduğunuz Bizneslər' : 'Referred Businesses'}</h3>
            {businesses.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)' }}>
                {isAz ? 'Hələ referal linkinizlə qeydiyyatdan keçən biznes yoxdur.' : 'No referred businesses yet.'}
              </p>
            ) : (
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>{isAz ? 'Biznes' : 'Business'}</th>
                      <th>{isAz ? 'Paket' : 'Plan'}</th>
                      <th>{isAz ? 'Aylıq Qiymət' : 'Plan Price'}</th>
                      <th>{isAz ? 'Status' : 'Status'}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {businesses.map((b) => (
                      <tr key={b.id}>
                        <td>{b.name}</td>
                        <td>{b.plan_name}</td>
                        <td>{Number(b.plan_price).toFixed(2)} AZN</td>
                        <td>{b.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="glass-card" style={{ padding: '1.5rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>{isAz ? 'Ödəniş Tarixçəsi' : 'Payout History'}</h3>
            {payouts.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)' }}>
                {isAz ? 'Hələ ödəniş qeydə alınmayıb.' : 'No payouts recorded yet.'}
              </p>
            ) : (
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>{isAz ? 'Məbləğ' : 'Amount'}</th>
                      <th>{isAz ? 'Üsul' : 'Method'}</th>
                      <th>{isAz ? 'Status' : 'Status'}</th>
                      <th>{isAz ? 'Tarix' : 'Date'}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {payouts.map((po) => (
                      <tr key={po.id}>
                        <td>{Number(po.amount_azn).toFixed(2)} AZN</td>
                        <td>{po.payment_method}</td>
                        <td>{po.status}</td>
                        <td>{po.created_at ? po.created_at.slice(0, 10) : '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default PartnerPortal;
