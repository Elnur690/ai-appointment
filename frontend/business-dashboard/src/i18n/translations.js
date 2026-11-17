export const PLAN_FEATURE_KEYS = [
  {
    key: 'allows_whatsapp',
    defaultIncluded: true,
    az: 'WhatsApp Biznes AI Resepşn (Standart Paket)',
    en: 'WhatsApp Business AI Receptionist (Default Included)',
  },
  {
    key: 'allows_instagram',
    az: 'Instagram Direct AI Resepşn İnteqrasiyası',
    en: 'Instagram Direct AI Receptionist Integration',
  },
  {
    key: 'allows_telegram',
    az: 'Telegram Bot AI Resepşn İnteqrasiyası',
    en: 'Telegram Bot AI Receptionist Integration',
  },
  {
    key: 'allows_voice_messages',
    az: 'WhatsApp Səsli Mesajların Tanınması və Randevu Yazılması',
    en: 'WhatsApp Voice Note Transcription & Booking',
  },
  {
    key: 'allows_online_payments',
    az: 'Onlayn Ödəniş Şlüzləri (Payriff və Paymegate)',
    en: 'Online Payment Gateways (Payriff & Paymegate)',
  },
  {
    key: 'allows_no_show_deposits',
    az: 'AI Gəlməmə (No-Show) Qorunması və Dinamik Beh (Depozit)',
    en: 'AI No-Show Protection & Dynamic Deposits',
  },
  {
    key: 'allows_shift_management',
    az: 'Növbəli İş Qrafiki (Səhər/Axşam/Tam) və Əlavə İş Saatı (Overtime)',
    en: 'Shift-Aware Staff Scheduling & Overtime Management',
  },
  {
    key: 'allows_cadence_engine',
    az: 'Proqnozlaşdırıcı Təkrar Randevu Mühərriki (Cadence Engine)',
    en: 'Predictive Cadence Rebooking Engine',
  },
  {
    key: 'allows_flash_drops',
    az: 'Son Dəqiqə Endirimləri (Flash Drops) və Gözləmə Siyahısı',
    en: 'Last-Minute Flash Drops & Smart Waitlist',
  },
  {
    key: 'allows_gift_vouchers',
    az: 'Rəqəmsal Hədiyyə Kartları və Kupon Satışı',
    en: 'Digital Gift Vouchers & Gifting',
  },
  {
    key: 'allows_loyalty_program',
    az: 'VIP Müştəri Loyallıq Proqramı (Gümüş və Qızıl Statuslar)',
    en: 'VIP Customer Loyalty Program (Silver & Gold Tiers)',
  },
  {
    key: 'allows_combo_packages',
    az: 'Kombo Xidmət Paketləri (Multi-Service Packages)',
    en: 'Multi-Service Combo Packages',
  },
  {
    key: 'allows_group_bookings',
    az: 'Qrup və Ailəvi Randevu Qəbulu',
    en: 'Group & Family Bookings',
  },
  {
    key: 'allows_product_upsells',
    az: 'AI Məhsul və Kosmetika Əlavə Satışı (Upsell)',
    en: 'AI Retail Product Upsells',
  },
  {
    key: 'allows_dynamic_pricing',
    az: 'Dinamik Qiymətləndirmə (Sakit Saat Endirimləri və Pik Saatlar)',
    en: 'Dynamic Off-Peak & Surge Pricing',
  },
  {
    key: 'allows_winback_campaigns',
    az: 'Avtomatik İtirilmiş Müştəriləri Qaytarma (Win-Back) Kampaniyası',
    en: 'Automated Customer Win-Back Campaigns',
  },
  {
    key: 'allows_gcal_sync',
    az: 'Google Təqvim 2-Tərəfli Sinxronizasiya',
    en: 'Google Calendar 2-Way Sync',
  },
  {
    key: 'allows_apple_cal_sync',
    az: 'Apple iCloud Təqvim Sinxronizasiyası',
    en: 'Apple iCloud Calendar Sync',
  },
  {
    key: 'allows_geo_routing',
    az: 'WhatsApp Konum (Geo-Location) ilə Ən Yaxın Filiala Yönləndirmə',
    en: 'WhatsApp Geo-Location Nearest Branch Auto-Routing',
  },
  {
    key: 'allows_emergency_reassignment',
    az: 'Təcili Usta Əvəzləməsi (Xəstəlik / Məzuniyyət Transferi)',
    en: 'Emergency Staff Reassignment & Sick-Leave Swaps',
  },
  {
    key: 'allows_growth_advisor',
    az: 'Həftəlik AI Biznes və Gəlir Məsləhətçisi',
    en: 'Weekly AI Business & Revenue Growth Advisor',
  },
  {
    key: 'allows_branch_level_ai_tone',
    az: 'Hər Filial Üçün Fərdi AI Ünsiyyət Тonu',
    en: 'Branch-Level Custom AI Persona & Tone',
  },
  {
    key: 'allows_discovery',
    az: 'Müştəri Kəşfiyyat Kataloqunda (Marketplace) Görünmə',
    en: 'Public Marketplace & Business Discovery Listing',
  },
  {
    key: 'allows_custom_domain',
    az: 'Şəxsi Domen (White-Label CNAME: cname.randevu.vip)',
    en: 'White-Label Custom CNAME Domain (cname.randevu.vip)',
  },
];

export const getPlanFeatureItems = (plan, lang = 'az') => {
  const isAz = lang !== 'en';
  const quota = Number(plan.message_limit || plan.ai_message_quota || 1000);
  const branches = Number(plan.max_branches || 1);
  const waNumbers = Number(plan.max_whatsapp_numbers || 1);
  const assignedModel = plan.features?.assigned_model || 'gemini-3.5-flash';

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
      label: isAz ? `${branches} filiala qədər dəstək` : `Up to ${branches} branch(es)`,
    },
    {
      key: 'wa_numbers',
      included: true,
      label: isAz
        ? `${waNumbers} WhatsApp nömrəsi qoşulması`
        : `Up to ${waNumbers} WhatsApp number(s)`,
    },
    {
      key: 'cash_payment',
      included: true,
      label: isAz
        ? 'Nağd Ödəniş və Gəlir Qeydiyyatı (Standart)'
        : 'Cash Payment & Revenue Ledger (Included)',
    },
    {
      key: 'ai_model',
      included: true,
      label: isAz ? `AI Mühərriki: ${assignedModel}` : `AI Engine: ${assignedModel}`,
    },
  ];

  const entitlements = PLAN_FEATURE_KEYS.map((item) => {
    const val =
      item.key === 'allows_whatsapp'
        ? plan.allows_whatsapp !== false
        : item.key === 'allows_instagram'
        ? Boolean(plan.allows_instagram || plan.allows_omnichannel_messaging)
        : item.key === 'allows_telegram'
        ? Boolean(plan.allows_telegram || plan.allows_omnichannel_messaging)
        : Boolean(plan[item.key] ?? item.defaultIncluded);

    return {
      key: item.key,
      included: val,
      label: isAz ? item.az : item.en,
    };
  });

  return [...limits, ...entitlements];
};

export const UI_TEXT = {
  az: {
    sidebar: {
      dashboard: 'İdarə Paneli',
      calendar: 'Təqvim',
      appointments: 'Randevular',
      staff: 'Ustalar və Növbələr',
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
      registerTab: 'Qeydiyyat / Pulsuz Başla',
      registerBusinessBtn: 'Biznes Qeydiyyatı',
      heroBadge: 'Salonlar, Klinikalar və Studiyalar üçün 24/7 AI Resepşn',
      heroTitle: 'WhatsApp, Instagram və Telegram-da Bütün Randevuları Avtomatlaşdırın',
      heroDesc:
        'Randevu.vip sizin WhatsApp, Instagram Direct və Telegram mesajlarınızı Azərbaycan, Rus, Türk və İngilis dillərində ağıllı randevu sisteminə çevirir — növbəli usta qrafiki, Nağd / Payriff / Paymegate ödənişləri və şəxsi domen dəstəyi ilə.',
      card1Title: 'WhatsApp, IG və TG AI',
      card1Desc: 'Mətn və səsli mesajlara ani cavab və istənilən an canlı operatora keçid.',
      card2Title: 'Sıfır Üst-Üstə Düşmə',
      card2Desc: 'Canlı usta cədvəli, fasilələr və 24s / 2s avtomatik xatırlatmalar.',
      card3Title: 'Gəlməmə (No-Show) Qorunması',
      card3Desc: 'Nağd, Payriff və Paymegate ilə avtomatlaşdırılmış onlayn beh (depozit).',
      card4Title: 'Şəxsi Domen (White-Label)',
      card4Desc: 'Öz domeninizi CNAME ilə cname.randevu.vip ünvanına yönləndirin.',
      welcomeBack: 'Xoş Gəlmisiniz',
      signInSubtitle: 'Randevuları, ustaları və AI köməkçinizi idarə etmək üçün daxil olun.',
      emailLabel: 'E-poçt Ünvanı',
      passwordLabel: 'Şifrə',
      signingIn: 'Daxil olunur...',
      signInSubmit: 'İdarəetmə Panelinə Daxil Ol',
      createAccountTitle: 'Biznes Hesabınızı Yaradın',
      createAccountSubtitle: '60 saniyə ərzində AI randevu panelinizi işə salın.',
      businessNameLabel: 'Biznes / Salon / Klinika Adı',
      businessNamePlaceholder: 'məs: Bella Aesthetics Bakı',
      ownerNameLabel: 'Sahibkarın Adı və Soyadı',
      ownerNamePlaceholder: 'məs: Nərgiz Nuriyeva',
      ownerEmailLabel: 'Sahibkarın E-poçt Ünvanı',
      phoneLabel: 'WhatsApp / Telefon Nömrəsi',
      passwordHint: 'Ən azı 6 simvol',
      referralLabel: 'Partnyor / Reseller Kodu (İstəyə bağlı)',
      referralPlaceholder: 'Varsa partnyor kodu',
      creatingWorkspace: 'Hesab yaradılır...',
      createAccountSubmit: 'Biznes Hesabını Yarat',
      plansTitle: 'Bütün Xüsusiyyətləri Əhatə Edən Şəffaf Paketlər',
      plansSubtitle: 'Hər bir yeni biznes Starter paketi ilə başlayır və istənilən vaxt yüksəldə bilər.',
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
      staff: 'Staff & Shifts',
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
      heroBadge: '24/7 AI Receptionist for Salons, Clinics & Studios',
      heroTitle: 'Automate Every Booking on WhatsApp, Instagram & Telegram',
      heroDesc:
        'Randevu.vip turns your WhatsApp, Instagram DMs, and Telegram bots into an intelligent booking engine in Azerbaijani, Russian, Turkish, and English — with shift-aware scheduling, Cash / Payriff / Paymegate payments, and white-label custom domains.',
      card1Title: 'WhatsApp, IG & TG AI',
      card1Desc: 'Instant text & voice note replies with human takeover anytime.',
      card2Title: 'Zero Double-Bookings',
      card2Desc: 'Real-time staff availability, buffers, and 24h/2h reminders.',
      card3Title: 'No-Show Protection',
      card3Desc: 'Cash, Payriff & Paymegate automated deposit links for bookings.',
      card4Title: 'White-Label Domain',
      card4Desc: 'Connect your own domain via CNAME to cname.randevu.vip.',
      welcomeBack: 'Welcome Back',
      signInSubtitle: 'Sign in to manage your appointments, staff, and AI assistant.',
      emailLabel: 'Email Address',
      passwordLabel: 'Password',
      signingIn: 'Signing in...',
      signInSubmit: 'Sign In to Workspace',
      createAccountTitle: 'Create Your Business Account',
      createAccountSubtitle: 'Launch your AI booking workspace in under 60 seconds.',
      businessNameLabel: 'Business / Salon / Clinic Name',
      businessNamePlaceholder: 'e.g. Bella Aesthetics Baku',
      ownerNameLabel: 'Owner Full Name',
      ownerNamePlaceholder: 'e.g. Nargiz Nuriyeva',
      ownerEmailLabel: 'Owner Email Address',
      phoneLabel: 'WhatsApp / Phone Number',
      passwordHint: 'At least 6 characters',
      referralLabel: 'Partner / Reseller Code (Optional)',
      referralPlaceholder: 'Optional referral code',
      creatingWorkspace: 'Creating Workspace...',
      createAccountSubmit: 'Create Business Account',
      plansTitle: 'Transparent Subscription Plans (All Platform Features)',
      plansSubtitle: 'Every new business starts on the Starter tier and can upgrade anytime.',
      perMonth: '/month',
      selectPlanCta: (name) => `Get Started with ${name}`,
      includedLabel: 'Included',
      notIncludedLabel: 'Not in this tier',
    },
  },
};
