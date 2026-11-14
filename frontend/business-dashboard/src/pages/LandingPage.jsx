import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/client';
import {
  Sparkles,
  MessageSquare,
  Calendar,
  ShieldCheck,
  Globe,
  Check,
  Mic,
  RefreshCw,
  Zap,
  Gift,
  BookOpen,
  ArrowRight,
} from 'lucide-react';

const getAppOrigin = () => {
  if (typeof window === 'undefined') return 'https://app.randevu.vip';
  const { protocol, hostname } = window.location;
  if (hostname === 'randevu.vip' || hostname === 'www.randevu.vip') {
    return `${protocol}//app.randevu.vip`;
  }
  return window.location.origin;
};

const TRANSLATIONS = {
  az: {
    navFeatures: 'Xüsusiyyətlər',
    navHowItWorks: 'Necə İşləyir',
    navPricing: 'Paketlər və Qiymətlər',
    navSignIn: 'Daxil Ol',
    navStartTrial: 'Pulsuz Başla',
    heroBadge: 'Salonlar, Klinikalar və Studiyalar üçün Süni İntellekt Randevu və Gəlir Platforması',
    heroTitlePrefix: 'WhatsApp və Instagram-ınızı ',
    heroTitleHighlight: '24/7 AI Resepşnə',
    heroTitleSuffix: ' Çevirin',
    heroSubtitle:
      'Cavabsız qalan mesajlara və üst-üstə düşən randevulara görə müştəri itirməyin. Randevu.vip mətn və səsli mesajlara saniyələr içində cavab verir, ustanın canlı təqviminə uyğun rezervasiya edir və 24 saat / 2 saat öncədən avtomatik xatırlatmalar göndərir.',
    heroPrimaryCta: 'app.randevu.vip-də Biznes Hesabını Yarat',
    heroSecondaryCta: 'Mövcud Hesaba Daxil Ol',
    howTitle: '3 Sadə Addımda İşə Başlayın',
    howSubtitlePrefix: 'Bütün idarəetmə ',
    howSubtitleHighlight: 'app.randevu.vip',
    howSubtitleSuffix: ' üzərindəki şəxsi biznes panelinizdən həyata keçirilir.',
    steps: [
      {
        badge: 'ADDIM 01',
        color: 'var(--primary)',
        title: 'Biznes Hesabınızı Yaradın',
        desc: 'Salon, klinika və ya studiyanızı qeydiyyatdan keçirin; xidmətlərinizi, müddətləri, qiymətləri və usta növbələrini daxil edin.',
      },
      {
        badge: 'ADDIM 02',
        color: 'var(--secondary)',
        title: 'WhatsApp QR Kodunu Skan Edin',
        desc: 'Mövcud biznes WhatsApp nömrənizi idarəetmə panelinin tənzimləmələr bölməsindən bir skanla qoşun.',
      },
      {
        badge: 'ADDIM 03',
        color: 'var(--success)',
        title: 'AI Avtomatik Yazır və Xatırladır',
        desc: 'Süni intellekt köməkçiniz sorğuları cavablandırır, randevu yazır və istənilən an bir kliklə söhbəti öz üzərinizə götürməyə imkan verir.',
      },
    ],
    featuresTitle: 'Müasir Xidmət Biznesləri Üçün Yaradılıb',
    featuresSubtitle:
      'Tam avtomatlaşdırılmış randevu qəbulu, gəlir qorunması və müştəri loyallığı tək bir platformada.',
    features: [
      {
        icon: MessageSquare,
        color: 'var(--primary)',
        title: 'WhatsApp və Instagram AI Resepşn',
        desc: 'Azərbaycan, Rus, Türk və İngilis dillərində 24/7 cavab verir, boş saatları yoxlayır və avtomatik randevu yazır.',
      },
      {
        icon: Mic,
        color: 'var(--secondary)',
        title: 'Səsli Mesajların Anlaşılması',
        desc: 'Müştərilər WhatsApp-da səsli mesaj göndərə bilər — AI səsi mətnə çevirir və istənilən vaxta uyğun randevu təyin edir.',
      },
      {
        icon: Calendar,
        color: 'var(--success)',
        title: 'Növbə Əsaslı Usta Qrafiki',
        desc: 'Səhər, Axşam və Tam gün növbələrini, fasilə vaxtlarını, əlavə iş saatlarını (overtime) və canlı operatora keçidi dəstəkləyir.',
      },
      {
        icon: ShieldCheck,
        color: 'var(--warning)',
        title: 'Gəlməmə (No-Show) Qorunması və Ödənişlər',
        desc: 'Payriff və EPoint vasitəsilə onlayn beh (depozit) qəbul edir və salonun bütün gəlir statistikasını izləyir.',
      },
      {
        icon: RefreshCw,
        color: 'var(--primary)',
        title: 'Avtomatik Təkrar Randevu Xatırlatması',
        desc: 'Müştərinin növbəti saç kəsimi, manikür və ya prosedur vaxtı çatdıqda avtomatik xatırlatma göndərir.',
      },
      {
        icon: Zap,
        color: 'var(--secondary)',
        title: 'Son Dəqiqə Endirimləri və Gözləmə Siyahısı',
        desc: 'Ləğv edilmiş və ya boş qalan saatları gözləmə siyahısındakı müştərilərə xüsusi təklif göndərərək avtomatik doldurur.',
      },
      {
        icon: Gift,
        color: 'var(--success)',
        title: 'Rəqəmsal Hədiyyə Kartları və VIP Loyallıq',
        desc: 'WhatsApp üzərindən hədiyyə kuponları satın və daimi müştərilərinizi Gümüş və VIP Qızıl statusları ilə mükafatlandırın.',
      },
      {
        icon: BookOpen,
        color: 'var(--warning)',
        title: 'RAG Bilik Bazası ("Səhvlərdən Öyrənmə")',
        desc: 'Parkinq məlumatlarını, daxili qaydaları və qiymət düzəlişlərini birbaşa süni intellektin yaddaşına öyrədin.',
      },
      {
        icon: Globe,
        color: 'var(--primary)',
        title: 'Şəxsi Domen (White-Label CNAME)',
        desc: 'Tam brendləşdirilmiş onlayn randevu səhifəsi üçün öz domen adınızı CNAME (cname.randevu.vip) ilə qoşun.',
      },
    ],
    pricingTitle: 'Şəffaf Abunəlik Paketləri',
    pricingSubtitle:
      'Starter paketi ilə başlayın, komandanız və randevu həcminiz böyüdükcə istənilən vaxt paketinizi yeniləyin.',
    perMonth: '/ay',
    unlimitedMessages: 'Limitsiz AI mesaj',
    messagesPerMonth: (count) => `Ayda ${Number(count).toLocaleString()} AI mesaj`,
    upToBranches: (count) => `${count || 1} filiala qədər dəstək`,
    omniBooking: 'WhatsApp, Instagram və Veb Randevu',
    voiceBooking: 'WhatsApp Səsli Mesajla Randevu',
    onlinePayments: 'Payriff və EPoint Onlayn Beh (Depozit)',
    customDomain: 'Şəxsi Domen (White-Label CNAME)',
    planCta: (name) => `${name} ilə Başla`,
    footerTagline: 'AI Randevu və Biznes İdarəetmə Platforması',
    footerLogin: 'İdarəetmə Paneli (app.randevu.vip)',
    footerRegister: 'Biznes Qeydiyyatı',
  },
  en: {
    navFeatures: 'Features',
    navHowItWorks: 'How It Works',
    navPricing: 'Plans & Pricing',
    navSignIn: 'Sign In',
    navStartTrial: 'Start Free Trial',
    heroBadge: 'AI Appointment & Revenue Platform for Salons, Clinics & Studios',
    heroTitlePrefix: 'Turn Your WhatsApp & Instagram Into a ',
    heroTitleHighlight: '24/7 AI Receptionist',
    heroTitleSuffix: '',
    heroSubtitle:
      'Stop losing clients to missed messages and double-bookings. Randevu.vip replies to texts and voice notes in seconds, books appointments into your live staff calendar, and sends automated 24h & 2h reminders.',
    heroPrimaryCta: 'Launch Your Workspace on app.randevu.vip',
    heroSecondaryCta: 'Sign In to Existing Account',
    howTitle: 'Go Live in 3 Simple Steps',
    howSubtitlePrefix: 'Everything is managed from your dedicated workspace at ',
    howSubtitleHighlight: 'app.randevu.vip',
    howSubtitleSuffix: '.',
    steps: [
      {
        badge: 'STEP 01',
        color: 'var(--primary)',
        title: 'Create Your Business Account',
        desc: 'Register your salon, clinic, or studio and configure your services, durations, prices, and staff shifts.',
      },
      {
        badge: 'STEP 02',
        color: 'var(--secondary)',
        title: 'Scan the WhatsApp QR Code',
        desc: 'Pair your existing business WhatsApp number directly inside your dashboard settings in one scan.',
      },
      {
        badge: 'STEP 03',
        color: 'var(--success)',
        title: 'AI Books & Reminds Automatically',
        desc: 'Your AI receptionist handles inquiries, schedules appointments, and lets you take over any chat with one click.',
      },
    ],
    featuresTitle: 'Built for Modern Service Businesses',
    featuresSubtitle:
      'Complete booking automation, revenue protection, and client retention in one platform.',
    features: [
      {
        icon: MessageSquare,
        color: 'var(--primary)',
        title: 'WhatsApp & Instagram AI Receptionist',
        desc: 'Replies 24/7 in Azerbaijani, Russian, Turkish, and English to check availability and book appointments automatically.',
      },
      {
        icon: Mic,
        color: 'var(--secondary)',
        title: 'Voice Note Understanding',
        desc: 'Customers can send WhatsApp voice messages naturally — the AI transcribes and books the exact requested slot.',
      },
      {
        icon: Calendar,
        color: 'var(--success)',
        title: 'Shift-Aware Staff Scheduling',
        desc: 'Supports Morning, Evening, and Full-Day shifts, buffer times, overtime rules, and instant human takeover.',
      },
      {
        icon: ShieldCheck,
        color: 'var(--warning)',
        title: 'No-Show Protection & Local Payments',
        desc: 'Collects automated online deposits via Payriff and EPoint for high-risk bookings and tracks full salon revenue.',
      },
      {
        icon: RefreshCw,
        color: 'var(--primary)',
        title: 'Predictive Cadence Rebooking',
        desc: 'Automatically reminds clients when their next haircut, manicure, or treatment cycle is due.',
      },
      {
        icon: Zap,
        color: 'var(--secondary)',
        title: 'Last-Minute Flash Drops & Waitlist',
        desc: 'Fills cancelled or empty slots automatically by notifying waitlisted clients with time-limited offers.',
      },
      {
        icon: Gift,
        color: 'var(--success)',
        title: 'Digital Gift Vouchers & VIP Loyalty',
        desc: 'Sell digital gift cards directly over WhatsApp and reward repeat customers with Silver & VIP Gold tiers.',
      },
      {
        icon: BookOpen,
        color: 'var(--warning)',
        title: 'RAG Knowledge Base ("Learn from Mistakes")',
        desc: 'Teach your AI your exact parking info, policies, and pricing corrections powered by PostgreSQL pgvector.',
      },
      {
        icon: Globe,
        color: 'var(--primary)',
        title: 'White-Label Custom Domains',
        desc: 'Connect your own domain via CNAME (cname.randevu.vip) for a fully branded booking experience.',
      },
    ],
    pricingTitle: 'Transparent Subscription Plans',
    pricingSubtitle:
      'Start on Starter and upgrade anytime as your team and booking volume grow.',
    perMonth: '/month',
    unlimitedMessages: 'Unlimited AI messages',
    messagesPerMonth: (count) => `${Number(count).toLocaleString()} AI messages / month`,
    upToBranches: (count) => `Up to ${count || 1} branch(es)`,
    omniBooking: 'WhatsApp, Instagram & Web Booking',
    voiceBooking: 'WhatsApp Voice Note Booking',
    onlinePayments: 'Payriff & EPoint Online Deposits',
    customDomain: 'White-Label Custom CNAME Domain',
    planCta: (name) => `Get Started with ${name}`,
    footerTagline: 'AI Appointment & Booking Platform',
    footerLogin: 'Workspace Login (app.randevu.vip)',
    footerRegister: 'Register Business',
  },
};

const LandingPage = () => {
  const [searchParams] = useSearchParams();
  const refCode = searchParams.get('ref') || '';
  const [plans, setPlans] = useState([]);
  const [lang, setLang] = useState(() => {
    try {
      const saved = localStorage.getItem('randevu_lang');
      return saved === 'en' ? 'en' : 'az';
    } catch {
      return 'az';
    }
  });

  const handleLanguageChange = (nextLang) => {
    setLang(nextLang);
    try {
      localStorage.setItem('randevu_lang', nextLang);
    } catch {
      // Ignore storage error
    }
  };

  useEffect(() => {
    api
      .get('/auth/plans')
      .then((res) => setPlans(res.data || []))
      .catch(() => setPlans([]));
  }, []);

  const t = TRANSLATIONS[lang] || TRANSLATIONS.az;
  const appOrigin = getAppOrigin();
  const loginUrl = `${appOrigin}/login${refCode ? `?ref=${encodeURIComponent(refCode)}` : ''}`;
  const registerUrl = `${appOrigin}/register${refCode ? `?ref=${encodeURIComponent(refCode)}` : ''}`;

  return (
    <div style={{ minHeight: '100vh', color: 'var(--text-primary)' }}>
      {/* Top Navigation */}
      <header
        style={{
          maxWidth: '1240px',
          margin: '0 auto',
          padding: '1.5rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Sparkles size={28} color="var(--primary)" />
          <span className="text-gradient" style={{ fontSize: '1.6rem', fontWeight: 700 }}>
            Randevu.vip
          </span>
        </div>

        <nav style={{ display: 'flex', alignItems: 'center', gap: '1.4rem', flexWrap: 'wrap' }}>
          <a href="#features" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontWeight: 500 }}>
            {t.navFeatures}
          </a>
          <a href="#how-it-works" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontWeight: 500 }}>
            {t.navHowItWorks}
          </a>
          <a href="#pricing" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontWeight: 500 }}>
            {t.navPricing}
          </a>

          {/* Language Switcher (AZ default | EN) */}
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              background: 'var(--glass-bg, rgba(255, 255, 255, 0.05))',
              border: '1px solid var(--border)',
              borderRadius: '999px',
              padding: '0.2rem',
            }}
          >
            <button
              type="button"
              onClick={() => handleLanguageChange('az')}
              style={{
                border: 'none',
                cursor: 'pointer',
                padding: '0.35rem 0.7rem',
                borderRadius: '999px',
                fontSize: '0.8rem',
                fontWeight: 700,
                background: lang === 'az' ? 'var(--primary)' : 'transparent',
                color: lang === 'az' ? '#fff' : 'var(--text-secondary)',
                transition: 'all 0.2s ease',
              }}
            >
              AZ
            </button>
            <button
              type="button"
              onClick={() => handleLanguageChange('en')}
              style={{
                border: 'none',
                cursor: 'pointer',
                padding: '0.35rem 0.7rem',
                borderRadius: '999px',
                fontSize: '0.8rem',
                fontWeight: 700,
                background: lang === 'en' ? 'var(--primary)' : 'transparent',
                color: lang === 'en' ? '#fff' : 'var(--text-secondary)',
                transition: 'all 0.2s ease',
              }}
            >
              EN
            </button>
          </div>

          <a href={loginUrl} className="btn btn-secondary" style={{ textDecoration: 'none' }}>
            {t.navSignIn}
          </a>
          <a href={registerUrl} className="btn btn-primary" style={{ textDecoration: 'none' }}>
            {t.navStartTrial} <ArrowRight size={16} />
          </a>
        </nav>
      </header>

      {/* Hero Section */}
      <section
        style={{
          maxWidth: '1100px',
          margin: '0 auto',
          padding: '4rem 1.5rem 3.5rem',
          textAlign: 'center',
        }}
      >
        <span className="badge badge-info" style={{ marginBottom: '1.25rem', display: 'inline-block', fontSize: '0.85rem' }}>
          {t.heroBadge}
        </span>
        <h1 style={{ fontSize: 'clamp(2.2rem, 5vw, 3.6rem)', lineHeight: 1.15, marginBottom: '1.5rem', fontWeight: 800 }}>
          {t.heroTitlePrefix}
          <span className="text-gradient">{t.heroTitleHighlight}</span>
          {t.heroTitleSuffix}
        </h1>
        <p
          style={{
            color: 'var(--text-secondary)',
            fontSize: '1.15rem',
            lineHeight: 1.65,
            maxWidth: '780px',
            margin: '0 auto 2.5rem',
          }}
        >
          {t.heroSubtitle}
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <a
            href={registerUrl}
            className="btn btn-primary"
            style={{ padding: '0.9rem 1.75rem', fontSize: '1rem', textDecoration: 'none' }}
          >
            {t.heroPrimaryCta} <ArrowRight size={18} />
          </a>
          <a
            href={loginUrl}
            className="btn btn-secondary"
            style={{ padding: '0.9rem 1.75rem', fontSize: '1rem', textDecoration: 'none' }}
          >
            {t.heroSecondaryCta}
          </a>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" style={{ maxWidth: '1200px', margin: '0 auto', padding: '3rem 1.5rem' }}>
        <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '0.5rem' }}>{t.howTitle}</h2>
        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '2.5rem' }}>
          {t.howSubtitlePrefix}
          <strong>{t.howSubtitleHighlight}</strong>
          {t.howSubtitleSuffix}
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
          {t.steps.map((step, idx) => (
            <div key={idx} className="glass-card" style={{ padding: '2rem' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: step.color, marginBottom: '0.5rem' }}>
                {step.badge}
              </div>
              <h3 style={{ marginBottom: '0.75rem' }}>{step.title}</h3>
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Feature Grid */}
      <section id="features" style={{ maxWidth: '1240px', margin: '0 auto', padding: '3rem 1.5rem' }}>
        <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '0.5rem' }}>{t.featuresTitle}</h2>
        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '2.5rem' }}>
          {t.featuresSubtitle}
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
          {t.features.map((f, idx) => (
            <div key={idx} className="glass-card" style={{ padding: '1.75rem' }}>
              <f.icon size={26} color={f.color} style={{ marginBottom: '1rem' }} />
              <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>{f.title}</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', lineHeight: 1.6, margin: 0 }}>
                {f.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Live Subscription Plans */}
      <section id="pricing" style={{ maxWidth: '1200px', margin: '0 auto', padding: '3.5rem 1.5rem' }}>
        <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '0.5rem' }}>{t.pricingTitle}</h2>
        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '2.5rem' }}>
          {t.pricingSubtitle}
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {plans.map((p) => (
            <div key={p.id} className="glass-card" style={{ padding: '2.25rem', display: 'flex', flexDirection: 'column' }}>
              <h3 style={{ fontSize: '1.4rem', marginBottom: '0.5rem' }}>{p.name}</h3>
              <div style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--primary)', marginBottom: '1.5rem' }}>
                {p.price} AZN
                <span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', fontWeight: 400 }}>{t.perMonth}</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '2rem', flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <Check size={16} color="var(--success)" />
                  <span>
                    {p.message_limit >= 100000
                      ? t.unlimitedMessages
                      : t.messagesPerMonth(p.message_limit)}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <Check size={16} color="var(--success)" />
                  <span>{t.upToBranches(p.max_branches)}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <Check size={16} color="var(--success)" />
                  <span>{t.omniBooking}</span>
                </div>
                {p.allows_voice_messages && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    <Check size={16} color="var(--success)" />
                    <span>{t.voiceBooking}</span>
                  </div>
                )}
                {p.allows_online_payments && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    <Check size={16} color="var(--success)" />
                    <span>{t.onlinePayments}</span>
                  </div>
                )}
                {p.allows_custom_domain && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    <Check size={16} color="var(--success)" />
                    <span>{t.customDomain}</span>
                  </div>
                )}
              </div>

              <a
                href={registerUrl}
                className="btn btn-primary"
                style={{ justifyContent: 'center', textDecoration: 'none', width: '100%' }}
              >
                {t.planCta(p.name)}
              </a>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer
        style={{
          borderTop: '1px solid var(--border)',
          marginTop: '3rem',
          padding: '2.5rem 1.5rem',
          textAlign: 'center',
          color: 'var(--text-secondary)',
          fontSize: '0.9rem',
        }}
      >
        <div
          style={{
            maxWidth: '1200px',
            margin: '0 auto',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={18} color="var(--primary)" />
            <strong style={{ color: 'var(--text-primary)' }}>Randevu.vip</strong> — {t.footerTagline}
          </div>
          <div style={{ display: 'flex', gap: '1.5rem' }}>
            <a href={loginUrl} style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>
              {t.footerLogin}
            </a>
            <a href={registerUrl} style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>
              {t.footerRegister}
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
