import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/client';
import { getPlanFeatureItems } from '../i18n/translations';
import {
  Sparkles,
  MessageSquare,
  Calendar,
  ShieldCheck,
  Globe,
  Check,
  X,
  Mic,
  RefreshCw,
  Zap,
  Gift,
  BookOpen,
  Send,
  Instagram,
  Building2,
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

const FALLBACK_PLANS = [
  {
    id: 'starter-tier',
    name: 'Starter',
    price: 29,
    max_branches: 1,
    max_whatsapp_numbers: 1,
    ai_message_quota: 1000,
    message_limit: 1000,
    allows_free_trial: true,
    trial_days: 14,
    allows_whatsapp: true,
    allows_instagram: false,
    allows_telegram: false,
    features: { assigned_model: 'gemini-3.5-flash' },
  },
  {
    id: 'pro-tier',
    name: 'Pro',
    price: 79,
    max_branches: 3,
    max_whatsapp_numbers: 3,
    ai_message_quota: 5000,
    message_limit: 5000,
    allows_free_trial: true,
    trial_days: 14,
    allows_whatsapp: true,
    allows_instagram: true,
    allows_telegram: true,
    allows_voice_messages: true,
    allows_online_payments: true,
    allows_no_show_deposits: true,
    allows_shift_management: true,
    allows_cadence_engine: true,
    allows_flash_drops: true,
    allows_gift_vouchers: true,
    allows_loyalty_program: true,
    allows_combo_packages: true,
    allows_dynamic_pricing: true,
    allows_winback_campaigns: true,
    allows_gcal_sync: true,
    allows_apple_cal_sync: true,
    allows_geo_routing: true,
    features: { assigned_model: 'claude-3-7-sonnet' },
  },
  {
    id: 'enterprise-tier',
    name: 'Enterprise',
    price: 199,
    max_branches: 20,
    max_whatsapp_numbers: 20,
    ai_message_quota: 50000,
    message_limit: 50000,
    allows_free_trial: true,
    trial_days: 14,
    allows_whatsapp: true,
    allows_instagram: true,
    allows_telegram: true,
    allows_voice_messages: true,
    allows_online_payments: true,
    allows_no_show_deposits: true,
    allows_shift_management: true,
    allows_cadence_engine: true,
    allows_flash_drops: true,
    allows_gift_vouchers: true,
    allows_loyalty_program: true,
    allows_combo_packages: true,
    allows_dynamic_pricing: true,
    allows_winback_campaigns: true,
    allows_gcal_sync: true,
    allows_apple_cal_sync: true,
    allows_geo_routing: true,
    allows_custom_domain: true,
    allows_branch_level_ai_tone: true,
    allows_emergency_reassignment: true,
    allows_growth_advisor: true,
    allows_group_bookings: true,
    allows_product_upsells: true,
    allows_discovery: true,
    features: { assigned_model: 'gpt-4o' },
  },
];

const TRANSLATIONS = {
  az: {
    navFeatures: 'Xüsusiyyətlər',
    navHowItWorks: 'Necə İşləyir',
    navPricing: 'Paketlər və Qiymətlər',
    navFaq: 'FAQ',
    navSignIn: 'Daxil Ol',
    navStartTrial: 'Pulsuz Sınağa Başla',
    heroBadge: 'Bütün Xidmət və Randevu Biznesləri Üçün Çoxkanallı Süni İntellekt Platforması',
    heroTitlePrefix: 'WhatsApp, Instagram və Telegram-ınızı ',
    heroTitleHighlight: '24/7 AI Resepşnə',
    heroTitleSuffix: ' Çevirin',
    heroSubtitle:
      'Tibb mərkəzləri, stomatologiya, gözəllik və sağlamlıq mərkəzləri, avtoservislər, hüquq və konsaltinq şirkətləri, tədris mərkəzləri və çoxfiliallı şəbəkələr üçün vahid AI rezervasiya sistemi. Randevu.vip mətn və səsli mesajlara saniyələr içində cavab verir, mütəxəssisin canlı təqviminə uyğun növbə yazır və avtomatik xatırlatmalar göndərir.',
    industriesLabel: 'İstənilən sahəyə uyğunlaşan universal arxitektura:',
    industries: [
      'Klinikalar və Tibb Mərkəzləri',
      'Stomatologiya və Estetika',
      'Gözəllik, Bərbər və SPA',
      'Avtoservis və Detaylinq',
      'Hüquq, Maliyyə və Konsaltinq',
      'Fitnes, İdman və Reabilitasiya',
      'Tədris və Kurs Mərkəzləri',
      'Çoxfiliallı Korporativ Şəbəkələr',
    ],
    heroPrimaryCta: 'app.randevu.vip-də Biznes Hesabını Yarat',
    heroSecondaryCta: 'Mövcud Hesaba Daxil Ol',
    howTitle: '3 Sadə Addımda İşə Başlayın',
    howSubtitlePrefix: 'Bütün kanallar və ödənişlər ',
    howSubtitleHighlight: 'app.randevu.vip',
    howSubtitleSuffix: ' üzərindəki şəxsi biznes panelinizdən idarə olunur.',
    steps: [
      {
        badge: 'ADDIM 01',
        color: 'var(--primary)',
        title: 'Biznesinizi və Xidmətlərinizi Qeydiyyatdan Keçirin',
        desc: 'Müəssisənizi yaradın, filiallarınızı, xidmət növlərini, müddətləri, qiymətləri və əməkdaşların növbə qrafiklərini daxil edin.',
      },
      {
        badge: 'ADDIM 02',
        color: 'var(--secondary)',
        title: 'WhatsApp, Instagram və Telegram-ı Qoşun',
        desc: 'WhatsApp nömrənizi 1 QR skanla (standart paketdə), Instagram Direct hesabınızı və Telegram Botunuzu (@BotFather tokeni ilə 1 kliklə) birbaşa Tənzimləmələrdən aktivləşdirin.',
      },
      {
        badge: 'ADDIM 03',
        color: 'var(--success)',
        title: 'AI Avtomatik Randevu Yazır və Ödəniş Qəbul Edir',
        desc: 'Süni intellekt 24/7 sorğuları cavablandırır, Nağd / Payriff / Paymegate ilə beh qəbul edir və istənilən an 1 kliklə söhbəti canlı operatora ötürür.',
      },
    ],
    featuresTitle: 'Bütün Xidmət Sahələri Üçün Tam Avtomatlaşdırma',
    featuresSubtitle:
      'WhatsApp, Instagram Direct, Telegram Bot, ödəniş şlüzləri və müştəri loyallığı tək bir platformada.',
    features: [
      {
        icon: MessageSquare,
        color: 'var(--success)',
        title: 'WhatsApp Biznes AI Resepşn (Standart Paket)',
        desc: 'Bütün paketlərə daxildir. 1 QR kod skanı ilə qoşulur, Azərbaycan, Rus, Türk və İngilis dillərində 24/7 boş saatları yoxlayır və randevu yazır.',
      },
      {
        icon: Instagram,
        color: 'var(--primary)',
        title: 'Instagram Direct AI İnteqrasiyası',
        desc: 'Meta Graph API üzərindən biznesinizin Instagram DM mesajlarını dərhal cavablandırır, qiymətlər barədə məlumat verir və müştərini birbaşa təqvimə yazır.',
      },
      {
        icon: Send,
        color: 'var(--secondary)',
        title: 'Telegram Bot (@BotFather) AI İnteqrasiyası',
        desc: 'Telegram-da @BotFather tokeninizi daxil edin — sistem Webhook-u avtomatik quraşdırır və Telegram üzərindən 24/7 randevu qəbul edir.',
      },
      {
        icon: Mic,
        color: 'var(--warning)',
        title: 'Səsli Mesajların Anlaşılması (Voice AI)',
        desc: 'Müştərilər səsli mesaj göndərdikdə AI səsi mətnə çevirir, istənilən xidməti və saatı anlayaraq dəqiq rezervasiya edir.',
      },
      {
        icon: ShieldCheck,
        color: 'var(--primary)',
        title: 'Nağd, Payriff və Paymegate Ödəniş Şlüzləri',
        desc: 'Həm müəssisədə nağd ödəniş uçotu, həm də gəlməmə (no-show) hallarına qarşı Payriff və Paymegate (api.paymegate.com) ilə avtomatik onlayn beh (depozit).',
      },
      {
        icon: Calendar,
        color: 'var(--success)',
        title: 'Növbəli İş Qrafiki və Təcili Əvəzləmə',
        desc: 'Səhər, Axşam və Tam gün növbələri, fasilələr, əlavə iş saatları (overtime) və əməkdaş xəstələndikdə avtomatik başqa mütəxəssisə yönləndirmə.',
      },
      {
        icon: RefreshCw,
        color: 'var(--secondary)',
        title: 'Proqnozlaşdırıcı Təkrar Müraciət (Cadence Engine)',
        desc: 'Hər xidmət üçün təkrar müayinə, texniki baxış və ya prosedur dövrü təyin edin — vaxtı çatdıqda AI müştəriyə avtomatik xatırlatma göndərir.',
      },
      {
        icon: Zap,
        color: 'var(--warning)',
        title: 'Son Dəqiqə Endirimləri (Flash Drops) və Gözləmə Siyahısı',
        desc: 'Ləğv edilmiş və ya boş qalan saatları gözləmə siyahısındakı müştərilərə xüsusi təklif göndərərək avtomatik doldurur.',
      },
      {
        icon: Gift,
        color: 'var(--success)',
        title: 'Rəqəmsal Hədiyyə Kartları və VIP Loyallıq',
        desc: 'Mesajlaşma üzərindən rəqəmsal hədiyyə kuponları satın və daimi müştərilərinizi Gümüş və VIP Qızıl statusları ilə mükafatlandırın.',
      },
      {
        icon: BookOpen,
        color: 'var(--primary)',
        title: 'RAG Bilik Bazası ("Səhvlərdən Öyrənmə")',
        desc: 'Ünvan, parkinq, daxili qaydalar və xüsusi şərtləri PostgreSQL pgvector yaddaşına əlavə edin — AI hər suala dəqiq cavab versin.',
      },
      {
        icon: Building2,
        color: 'var(--secondary)',
        title: 'Çoxfiliallı Konum (Geo-Location) Yönləndirməsi',
        desc: 'Müştəri konum göndərdikdə sistem ən yaxın filialı tapır və həmin filialın boş saatlarını təklif edir.',
      },
      {
        icon: Globe,
        color: 'var(--warning)',
        title: 'Şəxsi Domen (White-Label CNAME)',
        desc: 'Tam brendləşdirilmiş onlayn randevu səhifəsi üçün öz domen adınızı CNAME (cname.randevu.vip) ilə qoşun.',
      },
    ],
    pricingTitle: 'Hər Biznes Həcminə Uyğun Fərqləndirilmiş Paketlər',
    pricingSubtitle:
      'Starter, Pro və Enterprise paketləri komandanızın ölçüsünə və ehtiyac duyduğunuz kanallara görə fərqli imkanlar təqdim edir.',
    tierSubtitles: {
      starter: 'Tək filiallı bizneslər və fərdi mütəxəssislər üçün əsas WhatsApp AI paketi:',
      pro: 'Starter-dəki hər şey + Instagram, Telegram, Səsli AI və Onlayn Ödənişlər:',
      enterprise: 'Pro-dakı hər şey + 20 Filial, Şəxsi Domen (CNAME) və Korporativ AI:',
    },
    showAllComparison: 'Bütün 29 Xüsusiyyətin Müqayisəsini Göstər',
    showOnlyIncluded: 'Yalnız Paketə Daxil Olanları Göstər',
    perMonth: '/ay',
    planCta: (name) => `${name} Paketi ilə Başla`,
    faqTitle: 'Tez-tez Verilən Suallar (FAQ)',
    faqs: [
      {
        q: 'Randevu.vip yalnız salonlar üçündür, yoxsa digər bizneslər də istifadə edə bilər?',
        a: 'Randevu.vip bütün randevu və növbə əsaslı bizneslər üçün yaradılıb: klinikalar, stomatoloqlar, laboratoriyalar, gözəllik və SPA mərkəzləri, avtoservislər, hüquq və konsaltinq büroları, tədris mərkəzləri, idman studiyaları və çoxfiliallı şirkətlər.',
      },
      {
        q: 'WhatsApp, Instagram və Telegram kanalları necə qoşulur?',
        a: 'WhatsApp Biznes bütün paketlərə standart daxildir və 1 QR kod skanı ilə qoşulur. Pro və Enterprise paketlərində əlavə olaraq Instagram Direct və Telegram Bot (@BotFather tokeni ilə avtomatik Webhook qeydiyyatı) aktivləşdirilir.',
      },
      {
        q: 'Starter, Pro və Enterprise paketləri arasındakı əsas fərq nədir?',
        a: 'Starter paketi (29 AZN) 1 filial, 1 WhatsApp nömrəsi, 1,000 AI mesaj və nağd ödəniş uçotu təqdim edir. Pro paketi (79 AZN) 3 filial, 5,000 mesaj, Instagram Direct, Telegram Bot, Səsli mesajlar, Payriff/Paymegate onlayn beh və loyallıq modullarını açır. Enterprise (199 AZN) isə 20 filial, 50,000 mesaj, Şəxsi Domen (CNAME), təcili usta əvəzləməsi və həftəlik AI biznes məsləhətçisini əhatə edir.',
      },
      {
        q: 'Hansı ödəniş şlüzləri (Payment Gateways) dəstəklənir?',
        a: 'Randevu.vip həm yerində Nağd (Cash) ödəniş uçotunu, həm də Payriff və Paymegate (api.paymegate.com) vasitəsilə onlayn beh (depozit) və kart ödənişlərini dəstəkləyir.',
      },
    ],
    footerTagline: 'Çoxkanallı AI Randevu və Biznes İdarəetmə Platforması',
    footerLogin: 'İdarəetmə Paneli (app.randevu.vip)',
    footerRegister: 'Biznes Qeydiyyatı',
  },
  en: {
    navFeatures: 'Features',
    navHowItWorks: 'How It Works',
    navPricing: 'Plans & Pricing',
    navFaq: 'FAQ',
    navSignIn: 'Sign In',
    navStartTrial: 'Start Free Trial',
    heroBadge: 'Universal Omnichannel AI Booking & Revenue Platform for Service Businesses',
    heroTitlePrefix: 'Turn Your WhatsApp, Instagram & Telegram Into a ',
    heroTitleHighlight: '24/7 AI Receptionist',
    heroTitleSuffix: '',
    heroSubtitle:
      'Built for medical & dental clinics, wellness & beauty studios, auto service centers, legal & consulting firms, fitness centers, education providers, and multi-branch enterprises. Randevu.vip replies to texts and voice notes in seconds, books into your live team calendar, and sends automated 24h & 2h reminders.',
    industriesLabel: 'Engineered for every appointment-driven industry:',
    industries: [
      'Medical & Healthcare Clinics',
      'Dental & Aesthetic Practices',
      'Beauty, Barber & Wellness',
      'Auto Service & Detailing',
      'Legal, Finance & Consulting',
      'Fitness, Sports & Rehab',
      'Education & Tutoring Centers',
      'Multi-Branch Enterprises',
    ],
    heroPrimaryCta: 'Launch Your Workspace on app.randevu.vip',
    heroSecondaryCta: 'Sign In to Existing Account',
    howTitle: 'Go Live in 3 Simple Steps',
    howSubtitlePrefix: 'All channels and payment gateways are managed from your workspace at ',
    howSubtitleHighlight: 'app.randevu.vip',
    howSubtitleSuffix: '.',
    steps: [
      {
        badge: 'STEP 01',
        color: 'var(--primary)',
        title: 'Register Your Business & Services',
        desc: 'Create your business account and configure your branches, service catalog, durations, pricing, and team shift schedules.',
      },
      {
        badge: 'STEP 02',
        color: 'var(--secondary)',
        title: 'Connect WhatsApp, Instagram & Telegram',
        desc: 'Pair WhatsApp in 1 QR scan (default included), connect Instagram Direct via Meta Graph API, and link your Telegram Bot (@BotFather token) with 1-click auto-webhook setup.',
      },
      {
        badge: 'STEP 03',
        color: 'var(--success)',
        title: 'AI Books, Reminds & Collects Deposits 24/7',
        desc: 'Your AI receptionist handles inquiries, collects Cash / Payriff / Paymegate deposits, and lets human staff take over any chat with one click.',
      },
    ],
    featuresTitle: 'Complete Automation for Any Service Business',
    featuresSubtitle:
      'WhatsApp, Instagram Direct, Telegram Bot, multi-gateway payments, and client retention in one platform.',
    features: [
      {
        icon: MessageSquare,
        color: 'var(--success)',
        title: 'WhatsApp Business AI Receptionist (Default Package)',
        desc: 'Included in every plan. Pair in one QR scan to reply 24/7 in Azerbaijani, Russian, Turkish, and English and book appointments automatically.',
      },
      {
        icon: Instagram,
        color: 'var(--primary)',
        title: 'Instagram Direct AI Integration',
        desc: 'Connects via Meta Graph API to answer Instagram DMs instantly, check live team availability, and schedule appointments 24/7.',
      },
      {
        icon: Send,
        color: 'var(--secondary)',
        title: 'Telegram Bot (@BotFather) AI Integration',
        desc: 'Paste your @BotFather token in Settings — our backend automatically registers your Telegram webhook for 24/7 automated booking.',
      },
      {
        icon: Mic,
        color: 'var(--warning)',
        title: 'Voice Note Understanding (Voice AI)',
        desc: 'Clients can send voice messages naturally — the AI transcribes and books the exact requested specialist and time slot.',
      },
      {
        icon: ShieldCheck,
        color: 'var(--primary)',
        title: 'Cash, Payriff & Paymegate Payment Gateways',
        desc: 'Track in-person Cash payments and collect automated online deposits via Payriff and Paymegate (api.paymegate.com) to eliminate no-shows.',
      },
      {
        icon: Calendar,
        color: 'var(--success)',
        title: 'Shift-Aware Scheduling & Emergency Reassignment',
        desc: 'Supports Morning, Evening, and Full-Day shifts, buffer times, overtime rules, and automatic sick-leave staff reassignment.',
      },
      {
        icon: RefreshCw,
        color: 'var(--secondary)',
        title: 'Predictive Repeat-Visit Engine (Cadence Engine)',
        desc: 'Automatically reminds clients when their next checkup, maintenance, consultation, or treatment cycle is due.',
      },
      {
        icon: Zap,
        color: 'var(--warning)',
        title: 'Last-Minute Flash Drops & Smart Waitlist',
        desc: 'Fills cancelled or empty slots automatically by notifying waitlisted clients with time-limited offers.',
      },
      {
        icon: Gift,
        color: 'var(--success)',
        title: 'Digital Gift Vouchers & VIP Loyalty Tiers',
        desc: 'Sell digital gift cards over chat and reward repeat clients with Silver and VIP Gold loyalty tiers.',
      },
      {
        icon: BookOpen,
        color: 'var(--primary)',
        title: 'RAG Knowledge Base ("Learn from Mistakes")',
        desc: 'Teach your AI your exact location, parking info, policies, and pricing corrections powered by PostgreSQL pgvector.',
      },
      {
        icon: Building2,
        color: 'var(--secondary)',
        title: 'Multi-Branch Geo-Location Routing',
        desc: 'When a client shares their location, the AI calculates the nearest branch and offers available times there.',
      },
      {
        icon: Globe,
        color: 'var(--warning)',
        title: 'White-Label Custom CNAME Domains',
        desc: 'Connect your own domain via CNAME (cname.randevu.vip) for a 100% branded booking experience.',
      },
    ],
    pricingTitle: 'Distinct Subscription Plans for Every Business Stage',
    pricingSubtitle:
      'Starter, Pro, and Enterprise each unlock specific channels, AI models, and automation capabilities.',
    tierSubtitles: {
      starter: 'Core WhatsApp AI booking for single-location businesses & solo specialists:',
      pro: 'Everything in Starter + Instagram Direct, Telegram Bot, Voice AI & Online Payments:',
      enterprise: 'Everything in Pro + 20 Branches, White-Label Custom Domain & Enterprise AI:',
    },
    showAllComparison: 'Show Full 29-Feature Comparison Matrix',
    showOnlyIncluded: 'Show Only Included Features per Plan',
    perMonth: '/month',
    planCta: (name) => `Get Started with ${name}`,
    faqTitle: 'Frequently Asked Questions (FAQ)',
    faqs: [
      {
        q: 'Is Randevu.vip only for salons, or can any appointment-based business use it?',
        a: 'Randevu.vip is built for any appointment-driven business: medical & dental clinics, diagnostic labs, beauty & wellness studios, auto service centers, legal & consulting firms, fitness clubs, tutoring centers, and multi-branch enterprises.',
      },
      {
        q: 'How do WhatsApp, Instagram Direct, and Telegram Bot onboarding work?',
        a: 'WhatsApp Business is included in the default package and connects via a 1-scan QR code in Settings. Pro and Enterprise plans also unlock Instagram Direct (Meta Graph API) and Telegram Bot (@BotFather token with automatic webhook registration).',
      },
      {
        q: 'How do Starter, Pro, and Enterprise plans differ?',
        a: 'Starter (29 AZN) includes 1 branch, 1 WhatsApp line, 1,000 AI messages, and Cash ledger. Pro (79 AZN) unlocks 3 branches, 5,000 messages, Instagram Direct, Telegram Bot, Voice Notes, Payriff & Paymegate online deposits, shift management, and loyalty tools. Enterprise (199 AZN) unlocks 20 branches, 50,000 messages, White-Label CNAME domain, emergency staff reassignment, and the Weekly AI Growth Advisor.',
      },
      {
        q: 'Which payment gateways are supported?',
        a: 'Randevu.vip supports in-person Cash payments, Payriff, and Paymegate (api.paymegate.com) for automated online deposits and no-show protection.',
      },
    ],
    footerTagline: 'Omnichannel AI Appointment & Business Management Platform',
    footerLogin: 'Workspace Login (app.randevu.vip)',
    footerRegister: 'Register Business',
  },
};

const LandingPage = () => {
  const [searchParams] = useSearchParams();
  const refCode = searchParams.get('ref') || '';
  const [plans, setPlans] = useState(FALLBACK_PLANS);
  const [showFullMatrix, setShowFullMatrix] = useState(false);
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
      .then((res) => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          setPlans(res.data);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.lang = lang;
      document.title =
        lang === 'en'
          ? 'Randevu.vip — 24/7 AI Appointment & Revenue Platform for WhatsApp, Instagram & Telegram'
          : 'Randevu.vip — WhatsApp, Instagram və Telegram üçün 24/7 AI Randevu və Biznes Platforması';
    }
  }, [lang]);

  const t = TRANSLATIONS[lang] || TRANSLATIONS.az;
  const appOrigin = getAppOrigin();
  const loginUrl = `${appOrigin}/login${refCode ? `?ref=${encodeURIComponent(refCode)}` : ''}`;
  const registerUrl = `${appOrigin}/register${refCode ? `?ref=${encodeURIComponent(refCode)}` : ''}`;

  const handleBrandClick = (e) => {
    e.preventDefault();
    if (typeof window !== 'undefined') {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      if (window.location.pathname !== '/') {
        window.history.pushState({}, '', '/');
      }
    }
  };

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
        <a
          href="/"
          onClick={handleBrandClick}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            textDecoration: 'none',
            cursor: 'pointer',
          }}
          title="Randevu.vip — Ana Səhifə"
        >
          <Sparkles size={28} color="var(--primary)" />
          <span className="text-gradient" style={{ fontSize: '1.6rem', fontWeight: 700 }}>
            Randevu.vip
          </span>
        </a>

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
          <a href="#faq" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontWeight: 500 }}>
            {t.navFaq}
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
          maxWidth: '1120px',
          margin: '0 auto',
          padding: '3.5rem 1.5rem 3rem',
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
            fontSize: '1.12rem',
            lineHeight: 1.65,
            maxWidth: '840px',
            margin: '0 auto 2rem',
          }}
        >
          {t.heroSubtitle}
        </p>

        {/* Multi-Industry Pills */}
        <div style={{ marginBottom: '2.25rem' }}>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '0.75rem', fontWeight: 600 }}>
            {t.industriesLabel}
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '0.5rem', maxWidth: '920px', margin: '0 auto' }}>
            {t.industries.map((ind, i) => (
              <span
                key={i}
                style={{
                  padding: '0.35rem 0.85rem',
                  borderRadius: '999px',
                  fontSize: '0.8rem',
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid var(--border)',
                  color: 'var(--text-primary)',
                }}
              >
                {ind}
              </span>
            ))}
          </div>
        </div>

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
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
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

      {/* Feature Grid (12 Multi-Channel & Revenue Features) */}
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
      <section id="pricing" style={{ maxWidth: '1240px', margin: '0 auto', padding: '3.5rem 1.5rem' }}>
        <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '0.5rem' }}>{t.pricingTitle}</h2>
        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
          {t.pricingSubtitle}
        </p>

        <div style={{ textAlign: 'center', marginBottom: '2.25rem' }}>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setShowFullMatrix((prev) => !prev)}
            style={{ fontSize: '0.85rem' }}
          >
            {showFullMatrix ? t.showOnlyIncluded : t.showAllComparison}
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.5rem', alignItems: 'stretch' }}>
          {plans.map((p) => {
            const pKey = String(p.name || '').trim().toLowerCase();
            const isPro = pKey === 'pro';
            const tierSubtitle =
              t.tierSubtitles[pKey] ||
              (lang === 'en' ? 'Included capabilities in this plan:' : 'Bu paketə daxil olan imkanlar:');
            const featureItems = getPlanFeatureItems(p, lang, !showFullMatrix);

            return (
              <div
                key={p.id}
                className="glass-card"
                style={{
                  padding: '2.25rem',
                  display: 'flex',
                  flexDirection: 'column',
                  border: isPro ? '1px solid var(--primary)' : undefined,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <h3 style={{ fontSize: '1.45rem', margin: 0 }}>{p.name}</h3>
                  {p.allows_free_trial !== false && (p.trial_days ?? 14) > 0 && (
                    <span className="badge badge-info" style={{ fontSize: '0.75rem' }}>
                      {lang === 'en' ? `${p.trial_days ?? 14}-Day Free Trial` : `${p.trial_days ?? 14} Gün Pulsuz Sınaq`}
                    </span>
                  )}
                </div>

                <div style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--primary)', marginBottom: '0.75rem' }}>
                  {p.price} AZN
                  <span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', fontWeight: 400 }}>{t.perMonth}</span>
                </div>

                <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginBottom: '1.25rem', fontWeight: 500 }}>
                  {tierSubtitle}
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', marginBottom: '2rem', flex: 1 }}>
                  {featureItems.map((item) => (
                    <div
                      key={item.key}
                      style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '0.6rem',
                        fontSize: '0.88rem',
                        opacity: item.included ? 1 : 0.42,
                      }}
                    >
                      {item.included ? (
                        <Check size={16} color="var(--success)" style={{ flexShrink: 0, marginTop: '2px' }} />
                      ) : (
                        <X size={16} color="var(--text-secondary)" style={{ flexShrink: 0, marginTop: '2px' }} />
                      )}
                      <span>{item.label}</span>
                    </div>
                  ))}
                </div>

                <a
                  href={`${registerUrl}${registerUrl.includes('?') ? '&' : '?'}plan=${encodeURIComponent(p.name)}`}
                  className="btn btn-primary"
                  style={{ justifyContent: 'center', textDecoration: 'none', width: '100%' }}
                >
                  {t.planCta(p.name)}
                </a>
              </div>
            );
          })}
        </div>
      </section>

      {/* SEO & GEO Structured FAQ Section */}
      <section id="faq" style={{ maxWidth: '1040px', margin: '0 auto', padding: '2.5rem 1.5rem 1rem' }}>
        <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '2rem' }}>{t.faqTitle}</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '1.25rem' }}>
          {(t.faqs || []).map((item, idx) => (
            <div key={idx} className="glass-card" style={{ padding: '1.5rem' }}>
              <h3 style={{ fontSize: '1.05rem', marginBottom: '0.6rem', color: 'var(--primary)' }}>{item.q}</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', lineHeight: 1.6, margin: 0 }}>{item.a}</p>
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
          <a
            href="/"
            onClick={handleBrandClick}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              textDecoration: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
            }}
          >
            <Sparkles size={18} color="var(--primary)" />
            <strong style={{ color: 'var(--text-primary)' }}>Randevu.vip</strong> — {t.footerTagline}
          </a>
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
