export const PLAN_FEATURE_KEYS = [
  {
    key: 'allows_whatsapp',
    tier: 'starter',
    defaultIncluded: true,
    az: 'WhatsApp Biznes AI Resepşn (1 QR Skanla Qoşulma)',
    en: 'WhatsApp Business AI Receptionist (1-Scan QR Pairing)',
  },
  {
    key: 'allows_rag_knowledge',
    tier: 'starter',
    defaultIncluded: true,
    az: 'PostgreSQL pgvector RAG Bilik Bazası və Avtomatik Xatırlatmalar (24s / 2s)',
    en: 'PostgreSQL pgvector RAG Knowledge Base & Automated Reminders (24h / 2h)',
  },
  {
    key: 'allows_instagram',
    tier: 'pro',
    az: 'Instagram Direct AI Resepşn İnteqrasiyası',
    en: 'Instagram Direct AI Receptionist Integration',
  },
  {
    key: 'allows_telegram',
    tier: 'pro',
    az: 'Telegram Bot (@BotFather) AI Resepşn İnteqrasiyası',
    en: 'Telegram Bot (@BotFather) AI Receptionist Integration',
  },
  {
    key: 'allows_voice_messages',
    tier: 'pro',
    az: 'WhatsApp Səsli Mesajların Tanınması və Avtomatik Randevu',
    en: 'WhatsApp Voice Note Transcription & Automated Booking',
  },
  {
    key: 'allows_online_payments',
    tier: 'pro',
    az: 'Onlayn Ödəniş Şlüzləri (Payriff və Paymegate İnteqrasiyası)',
    en: 'Online Payment Gateways (Payriff & Paymegate Integration)',
  },
  {
    key: 'allows_no_show_deposits',
    tier: 'pro',
    az: 'AI Gəlməmə (No-Show) Qorunması və Avtomatik Beh (Depozit)',
    en: 'AI No-Show Protection & Automated Deposit Links',
  },
  {
    key: 'allows_shift_management',
    tier: 'pro',
    az: 'Növbəli İş Qrafiki (Səhər/Axşam/Tam) və Əlavə Saat (Overtime)',
    en: 'Shift-Aware Staff Scheduling & Overtime Management',
  },
  {
    key: 'allows_cadence_engine',
    tier: 'pro',
    az: 'Proqnozlaşdırıcı Təkrar Müraciət Mühərriki (Cadence Engine)',
    en: 'Predictive Repeat-Visit Rebooking Engine (Cadence Engine)',
  },
  {
    key: 'allows_flash_drops',
    tier: 'pro',
    az: 'Son Dəqiqə Endirimləri (Flash Drops) və Ağıllı Gözləmə Siyahısı',
    en: 'Last-Minute Flash Drops & Smart Waitlist Monetization',
  },
  {
    key: 'allows_gift_vouchers',
    tier: 'pro',
    az: 'Rəqəmsal Hədiyyə Kartları və Kupon Satışı',
    en: 'Digital Gift Vouchers & Promo Cards',
  },
  {
    key: 'allows_loyalty_program',
    tier: 'pro',
    az: 'VIP Müştəri Loyallıq Proqramı (Gümüş və Qızıl Statuslar)',
    en: 'VIP Customer Loyalty Program (Silver & Gold Tiers)',
  },
  {
    key: 'allows_combo_packages',
    tier: 'pro',
    az: 'Kombo Xidmət Paketləri (Multi-Service Packages)',
    en: 'Multi-Service Combo Packages',
  },
  {
    key: 'allows_dynamic_pricing',
    tier: 'pro',
    az: 'Dinamik Qiymətləndirmə (Sakit Saat Endirimləri və Pik Saatlar)',
    en: 'Dynamic Off-Peak & Surge Pricing',
  },
  {
    key: 'allows_winback_campaigns',
    tier: 'pro',
    az: 'Avtomatik İtirilmiş Müştəriləri Qaytarma (Win-Back) Kampaniyası',
    en: 'Automated Customer Win-Back Campaigns',
  },
  {
    key: 'allows_gcal_sync',
    tier: 'pro',
    az: 'Google Təqvim 2-Tərəfli Sinxronizasiya',
    en: 'Google Calendar 2-Way Sync',
  },
  {
    key: 'allows_apple_cal_sync',
    tier: 'pro',
    az: 'Apple iCloud Təqvim Sinxronizasiyası',
    en: 'Apple iCloud Calendar Sync',
  },
  {
    key: 'allows_geo_routing',
    tier: 'pro',
    az: 'Konum (Geo-Location) ilə Ən Yaxın Filiala Avtomatik Yönləndirmə',
    en: 'Geo-Location Nearest Branch Auto-Routing',
  },
  {
    key: 'allows_custom_domain',
    tier: 'enterprise',
    az: 'Şəxsi Domen (White-Label CNAME: cname.randevu.vip)',
    en: 'White-Label Custom CNAME Domain (cname.randevu.vip)',
  },
  {
    key: 'allows_branch_level_ai_tone',
    tier: 'enterprise',
    az: 'Hər Filial Üçün Fərdi AI Ünsiyyət Tonu və Təlimatları',
    en: 'Branch-Level Custom AI Persona & Instructions',
  },
  {
    key: 'allows_emergency_reassignment',
    tier: 'enterprise',
    az: 'Təcili Mütəxəssis Əvəzləməsi (Xəstəlik / Məzuniyyət Transferi)',
    en: 'Emergency Staff Reassignment & Sick-Leave Swaps',
  },
  {
    key: 'allows_growth_advisor',
    tier: 'enterprise',
    az: 'Həftəlik AI Biznes və Gəlir Artımı Məsləhətçisi',
    en: 'Weekly AI Business & Revenue Growth Advisor',
  },
  {
    key: 'allows_group_bookings',
    tier: 'enterprise',
    az: 'Qrup və Korporativ Randevu Qəbulu',
    en: 'Group & Corporate Bookings',
  },
  {
    key: 'allows_product_upsells',
    tier: 'enterprise',
    az: 'AI Əlavə Məhsul və Xidmət Satışı (Smart Upsell)',
    en: 'AI Smart Product & Add-On Upsells',
  },
  {
    key: 'allows_discovery',
    tier: 'enterprise',
    az: 'Ümumi Biznes Kəşfiyyat Kataloqunda (Marketplace) Öncəlik',
    en: 'Priority Public Marketplace & Business Discovery Listing',
  },
];

export const getPlanFeatureItems = (plan, lang = 'az', onlyIncluded = true) => {
  const isAz = lang !== 'en';
  const pName = String(plan.name || '').trim().toLowerCase();
  const isPro = pName === 'pro';
  const isEnterprise = pName === 'enterprise';

  const quota = Number(
    plan.message_limit || plan.ai_message_quota || (isEnterprise ? 50000 : isPro ? 5000 : 1000)
  );
  const branches = Number(plan.max_branches || (isEnterprise ? 20 : isPro ? 3 : 1));
  const waNumbers = Number(plan.max_whatsapp_numbers || (isEnterprise ? 20 : isPro ? 3 : 1));
  const assignedModel =
    plan.features?.assigned_model ||
    (isEnterprise ? 'gpt-4o' : isPro ? 'claude-3-7-sonnet' : 'gemini-3.5-flash');

  const limits = [
    {
      key: 'quota',
      included: true,
      label:
        quota >= 100000
          ? isAz
            ? 'Limitsiz AI mesaj / ay'
            : 'Unlimited AI messages / month'
          : isAz
          ? `Ayda ${quota.toLocaleString()} AI mesaj limiti`
          : `${quota.toLocaleString()} AI messages / month`,
    },
    {
      key: 'branches',
      included: true,
      label: isAz ? `${branches} filiala qədər idarəetmə` : `Up to ${branches} branch(es) management`,
    },
    {
      key: 'wa_numbers',
      included: true,
      label: isAz
        ? `${waNumbers} WhatsApp Biznes xətti`
        : `Up to ${waNumbers} WhatsApp Business line(s)`,
    },
    {
      key: 'cash_payment',
      included: true,
      label: isAz
        ? 'Nağd Ödəniş və Gəlir Uçotu Jurnalı (Standart)'
        : 'Cash Payment & Revenue Ledger (Included)',
    },
    {
      key: 'ai_model',
      included: true,
      label: isAz ? `AI Model Mühərriki: ${assignedModel}` : `AI Model Engine: ${assignedModel}`,
    },
  ];

  // Check if DB row had all false flags from an older schema seed
  const hasExplicitDbFlags =
    Boolean(plan.allows_voice_messages) ||
    Boolean(plan.allows_online_payments) ||
    Boolean(plan.allows_custom_domain) ||
    Boolean(plan.allows_instagram) ||
    Boolean(plan.allows_telegram);

  const entitlements = PLAN_FEATURE_KEYS.map((item) => {
    let val = false;
    if (item.defaultIncluded) {
      val = true;
    } else if (hasExplicitDbFlags) {
      val =
        item.key === 'allows_instagram'
          ? Boolean(plan.allows_instagram || plan.allows_omnichannel_messaging)
          : item.key === 'allows_telegram'
          ? Boolean(plan.allows_telegram || plan.allows_omnichannel_messaging)
          : Boolean(plan[item.key]);
    } else {
      // Fallback to tier defaults if DB row wasn't migrated yet
      if (isEnterprise) {
        val = true;
      } else if (isPro) {
        val = item.tier === 'starter' || item.tier === 'pro';
      } else {
        val = item.tier === 'starter';
      }
    }

    return {
      key: item.key,
      included: val,
      tier: item.tier,
      label: isAz ? item.az : item.en,
    };
  });

  const combined = [...limits, ...entitlements];
  return onlyIncluded ? combined.filter((i) => i.included) : combined;
};

export const UI_TEXT = {
  az: {
    sidebar: {
      dashboard: 'İdarə Paneli',
      calendar: 'Təqvim',
      appointments: 'Randevular',
      staff: 'Komanda və Növbələr',
      services: 'Xidmətlər',
      customers: 'Müştərilər',
      conversations: 'Mesajlar (AI Chat)',
      knowledge: 'Bilik Bazası (RAG)',
      payments: 'Ödənişlər',
      settings: 'Tənzimləmələr',
      logout: 'Çıxış',
      workspace: 'Biznes Paneli',
    },
    auth: {
      signInTab: 'Daxil Ol',
      registerTab: 'Qeydiyyat / Pulsuz Sınaq',
      registerBusinessBtn: 'Biznes Qeydiyyatı',
      heroBadge: 'İstənilən Xidmət və Randevu Biznesi üçün 24/7 AI Автоmatlaşdırma Platforması',
      heroTitle: 'WhatsApp, Instagram və Telegram-da Bütün Randevuları Avtomatlaşdırın',
      heroDesc:
        'Randevu.vip tibb mərkəzləri, klinikalar, gözəllik və sağlamlıq mərkəzləri, tədris, konsaltinq, avtoservis və bütün randevu əsaslı bizneslər üçün WhatsApp, Instagram Direct və Telegram mesajlarını 24/7 ağıllı rezervasiya sisteminə çevirir.',
      card1Title: 'WhatsApp, IG və Telegram AI',
      card1Desc: 'Mətn və səsli mesajlara 4 dildə ani cavab və istənilən an canlı operatora keçid.',
      card2Title: 'Sıfır Üst-Üstə Düşmə',
      card2Desc: 'Canlı əməkdaş cədvəli, fasilələr və 24s / 2s avtomatik xatırlatmalar.',
      card3Title: 'Nağd, Payriff və Paymegate',
      card3Desc: 'Gəlməmə (No-Show) qorunması üçün avtomatlaşdırılmış onlayn beh və ödəniş uçotu.',
      card4Title: 'Şəxsi Domen (White-Label)',
      card4Desc: 'Öz domeninizi CNAME ilə cname.randevu.vip ünvanına yönləndirin.',
      welcomeBack: 'Xoş Gəlmisiniz',
      signInSubtitle: 'Randevuları, komandanızı və AI köməkçinizi idarə etmək üçün daxil olun.',
      emailLabel: 'E-poçt Ünvanı',
      passwordLabel: 'Şifrə',
      signingIn: 'Daxil olunur...',
      signInSubmit: 'İdarəetmə Panelinə Daxil Ol',
      createAccountTitle: 'Biznes Hesabınızı Yaradın',
      createAccountSubtitle: '60 saniyə ərzində çoxkanallı AI randevu panelinizi işə salın.',
      businessNameLabel: 'Biznes / Şirkət / Müəssisə Adı',
      businessNamePlaceholder: 'məs: MedLine Klinika, ProAuto Servis, Bakı Hüquq Mərkəzi',
      ownerNameLabel: 'Məsul Şəxsin Adı və Soyadı',
      ownerNamePlaceholder: 'məs: Nərgiz Nuriyeva',
      ownerEmailLabel: 'Biznes E-poçt Ünvanı',
      phoneLabel: 'WhatsApp / Əlaqə Nömrəsi',
      passwordHint: 'Ən azı 6 simvol',
      referralLabel: 'Partnyor / Reseller Kodu (İstəyə bağlı)',
      referralPlaceholder: 'Varsa partnyor kodu',
      creatingWorkspace: 'Hesab yaradılır...',
      createAccountSubmit: 'Biznes Hesabını Yarat',
      plansTitle: 'Fərqli Biznes Həcmləri Üçün Şəffaf Abunəlik Paketləri',
      plansSubtitle: 'Kiçik komandalardan çoxfiliallı şəbəkələrə qədər hər paket özünəməxsus imkanlar təqdim edir.',
      perMonth: '/ay',
      selectPlanCta: (name) => `${name} ilə Qeydiyyatdan Keç`,
      includedLabel: 'Daxildir',
      notIncludedLabel: 'Bu paketdə yoxdur',
    },
  },
  en: {
    sidebar: {
      dashboard: 'Dashboard',
      calendar: 'Calendar',
      appointments: 'Appointments',
      staff: 'Team & Shifts',
      services: 'Services',
      customers: 'Customers',
      conversations: 'Conversations',
      knowledge: 'Knowledge Base',
      payments: 'Payments',
      settings: 'Settings',
      logout: 'Logout',
      workspace: 'Business Workspace',
    },
    auth: {
      signInTab: 'Sign In',
      registerTab: 'Start Free Trial / Register',
      registerBusinessBtn: 'Register Business',
      heroBadge: '24/7 AI Booking & Revenue Platform for Any Appointment-Based Business',
      heroTitle: 'Automate Every Booking on WhatsApp, Instagram & Telegram',
      heroDesc:
        'Randevu.vip turns WhatsApp, Instagram Direct, and Telegram into a 24/7 intelligent booking engine for clinics, medical centers, wellness & beauty, auto services, consulting firms, education centers, and multi-branch enterprises.',
      card1Title: 'WhatsApp, IG & Telegram AI',
      card1Desc: 'Instant text & voice note replies in 4 languages with 1-click human takeover.',
      card2Title: 'Zero Double-Bookings',
      card2Desc: 'Real-time team availability, buffer times, and automated 24h/2h reminders.',
      card3Title: 'Cash, Payriff & Paymegate',
      card3Desc: 'Automated online deposit links for no-show protection and full revenue tracking.',
      card4Title: 'White-Label Domain',
      card4Desc: 'Connect your own domain via CNAME to cname.randevu.vip.',
      welcomeBack: 'Welcome Back',
      signInSubtitle: 'Sign in to manage your appointments, team schedules, and AI receptionist.',
      emailLabel: 'Email Address',
      passwordLabel: 'Password',
      signingIn: 'Signing in...',
      signInSubmit: 'Sign In to Workspace',
      createAccountTitle: 'Create Your Business Account',
      createAccountSubtitle: 'Launch your omnichannel AI booking workspace in under 60 seconds.',
      businessNameLabel: 'Business / Company / Organization Name',
      businessNamePlaceholder: 'e.g. MedLine Clinic, ProAuto Service, Apex Consulting',
      ownerNameLabel: 'Owner / Manager Full Name',
      ownerNamePlaceholder: 'e.g. Nargiz Nuriyeva',
      ownerEmailLabel: 'Business Email Address',
      phoneLabel: 'WhatsApp / Contact Number',
      passwordHint: 'At least 6 characters',
      referralLabel: 'Partner / Reseller Code (Optional)',
      referralPlaceholder: 'Optional referral code',
      creatingWorkspace: 'Creating Workspace...',
      createAccountSubmit: 'Create Business Account',
      plansTitle: 'Tailored Subscription Plans for Every Business Size',
      plansSubtitle: 'From solo specialists to multi-branch enterprises — each tier unlocks distinct omnichannel and revenue capabilities.',
      perMonth: '/month',
      selectPlanCta: (name) => `Get Started with ${name}`,
      includedLabel: 'Included',
      notIncludedLabel: 'Not in this tier',
    },
  },
};
