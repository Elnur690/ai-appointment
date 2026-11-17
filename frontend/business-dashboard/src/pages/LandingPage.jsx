import React, { useEffect, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/client';
import { getPlanFeatureItems } from '../i18n/translations';
import { BrandLogo } from '../components/common/BrandLogo';
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
  Handshake,
  Lock,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
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
    navRoi: 'Gəlir Kalkulyatoru',
    navPricing: 'Paketlər',
    navReseller: 'Satış Partnyoru Ol',
    navFaq: 'FAQ',
    navSignIn: 'Daxil Ol',
    navStartTrial: '14 Gün Pulsuz Başla',
    heroBadge: 'Bütün Xidmət və Randevu Biznesləri Üçün Çoxkanallı Süni İntellekt Platforması',
    heroTitlePrefix: 'Gecikən Cavablara Görə Müştəri İtirməyi Dayandırın — ',
    heroTitleHighlight: 'WhatsApp, Instagram və Telegram-ı 24/7 AI Resepşnə',
    heroTitleSuffix: ' Çevirin',
    heroSubtitle:
      'Araşdırmalar göstərir ki, müştərilərin 62%-i 5 dəqiqə ərzində cavab almadıqda rəqib şirkətə müraciət edir. Randevu.vip tibb mərkəzləri, stomatologiya, gözəllik və SPA, avtoservislər, hüquq və tədris mərkəzləri üçün mətn və səsli mesajları 3 saniyədə cavablandırır, təqvimə yazır və onlayn beh (depozit) qəbul edir.',
    riskReversal: '✓ Kredit kartı tələb olunmur   •   ✓ 60 saniyədə QR ilə qoşulur   •   ✓ İstənilən vaxt ləğv edilə bilər',
    industriesLabel: 'İstənilən sahəyə uyğunlaşan universal çoxfiliallı arxitektura:',
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
    heroPrimaryCta: '14 Günlük Pulsuz Sınağı İndi Başlat',
    heroSecondaryCta: 'Satış Partnyoru Ol (20%+ Komissiya)',
    painTitle: 'Niyə Ənənəvi Qeydiyyat Biznesinizə Hər Ay Minlərlə Manat İtki Yaşadır?',
    painOldTitle: '❌ Ənənəvi İdarəetmə (Randevu.vip Olmadan)',
    painOldList: [
      'Axşam saatlarında və həftəsonu yazılan WhatsApp / Instagram / Telegram mesajları cavabsız qalır.',
      'Müştərilər randevuya gəlmir (No-Show) və boş qalan saatlara görə birbaşa gəlir itirilir.',
      'Administrator eyni anda həm zənglərə, həm də 3 fərqli mesajlaşma kanalına çatdıra bilmir.',
      'Səsli mesajları dinləmək və növbə cədvəlini əllə yoxlamaq vaxt aparır və səhvlərə yol açır.',
    ],
    painNewTitle: '✓ Randevu.vip AI Автоmatlaşdırması İlə',
    painNewList: [
      'Gecə saat 03:00-da belə WhatsApp, Instagram Direct və Telegram mesajlarına 3 saniyədə 4 dildə cavab verilir.',
      'Payriff və Paymegate ilə avtomatik onlayn beh (depozit) alınaraq gəlməmə (No-Show) halları sıfıra endirilir.',
      'AI səsli mesajları anlayır, mütəxəssisin növbəsini yoxlayır və 24s / 2s öncədən avtomatik xatırlatma göndərir.',
      'Ləğv edilən saatlar "Flash Drop" vasitəsilə gözləmə siyahısındakı müştərilərlə dərhal doldurulur.',
    ],
    roiTitle: 'İtirdiyiniz Gəliri Hesablayın (Canlı ROI Kalkulyatoru)',
    roiSubtitle: 'Gündə cəmi bir neçə cavabsız mesajın və ya gəlməyən müştərinin biznesinizə neçəyə başa gəldiyini görün:',
    roiMissedLabel: 'Gündəlik itirilən / gec cavablanan müraciət və ya gəlməyən müştəri sayı:',
    roiPriceLabel: 'Orta xidmət / qəbul qiyməti (AZN):',
    roiMonthlyRecovered: 'Randevu.vip ilə Qorunan Aylıq Əlavə Gəlir:',
    roiYearlyRecovered: 'İllik Əlavə Gəlir Artımı:',
    roiNote: 'Gündə cəmi 1 qorunan randevu bütün aylıq abunəlik xərcinizi 10 dəfədən çox qarşılayır.',
    howTitle: '3 Sadə Addımda İşə Başlayın',
    howSubtitlePrefix: 'Bütün kanallar və ödənişlər ',
    howSubtitleHighlight: 'app.randevu.vip',
    howSubtitleSuffix: ' üzərindəki təhlükəsiz biznes panelinizdən idarə olunur.',
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
    mostPopularBadge: '★ ƏN ÇOX SEÇİLƏN PAKET',
    dailyCostAnchor: (price) => `Gündə cəmi ${(Number(price) / 30).toFixed(2)} AZN — 1 randevu bütün ayı ödəyir`,
    tierSubtitles: {
      starter: 'Tək filiallı bizneslər və fərdi mütəxəssislər üçün əsas WhatsApp AI paketi:',
      pro: 'Starter-dəki hər şey + Instagram, Telegram, Səsli AI və Onlayn Ödənişlər:',
      enterprise: 'Pro-dakı hər şey + 20 Filial, Şəxsi Domen (CNAME) və Korporativ AI:',
    },
    showAllComparison: 'Bütün 29 Xüsusiyyətin Müqayisəsini Göstər',
    showOnlyIncluded: 'Yalnız Paketə Daxil Olanları Göstər',
    perMonth: '/ay',
    planCta: (name) => `${name} Paketi ilə Pulsuz Başla`,
    securityTitle: 'Bank Səviyyəli Təhlükəsizlik və Məlumat Məxfiliyi',
    securityItems: [
      {
        title: 'İzolyasiya Olunmuş Tenant Bazası',
        desc: 'Hər bir biznesin müştəri bazası, API açarları və yazışmaları PostgreSQL-də tam izolyasiya olunur.',
      },
      {
        title: 'TLS 1.3 və HSTS Şifrələmə',
        desc: 'Bütün trafik və webhook bağlantıları 256-bit TLS şifrələmə və ciddi HSTS başlıqları ilə qorunur.',
      },
      {
        title: 'Rəsmi Ödəniş Təhlükəsizliyi',
        desc: 'Kart məlumatları heç vaxt bizdə saxlanılmır — ödənişlər birbaşa Payriff və Paymegate tərəfindən emal edilir.',
      },
      {
        title: 'AI Guardrail Qorunması',
        desc: 'Mövzudan kənar və ya həssas suallar aşkarlandıqda AI avtomatik dayanır və canlı operatoru xəbərdar edir.',
      },
    ],
    resellerBadge: 'RƏSMİ SATIŞ PARTNYORU VƏ AGENTLİK PROQRAMI',
    resellerTitle: 'Randevu.vip Satış Partnyoru Olun — Hər Qoşduğunuz Biznesdən Hər Ay 20%+ Davamlı Gəlir Qazanın',
    resellerSubtitle:
      'Rəqəmsal marketinq agentlikləri, SMM mütəxəssisləri, İT konsultantlar və satış peşəkarları üçün passiv gəlir imkanı. Öz unikal referal linkinizi və ya şəxsi brend (White-Label) domeninizi alın, müştərilərinizi qoşun və onlar abunə qaldığı müddətcə hər ay komissiya əldə edin.',
    resellerPerks: [
      'Hər aktiv biznes abunəliyindən hər ay 20%+ təkrarlanan (recurring) komissiya',
      'Avtomatik izləmə linki (randevu.vip/?ref=SIZINKOD) və şəxsi White-Label CNAME dəstəyi',
      'Klinika, salon, avtoservis və tədris mərkəzlərinə asan satış üçün hazır təqdimat',
    ],
    resellerCta: 'Satış Partnyoru Olmaq Üçün Müraciət Et',
    modalTitle: 'Satış Partnyoru (Reseller) Müraciət Forması',
    modalSubtitle: 'Məlumatlarınızı daxil edin — dərhal şəxsi partnyor kodunuz və referal linkiniz yaradılacaq.',
    modalNameLabel: 'Ad və Soyad',
    modalCompanyLabel: 'Agentlik / Şirkət Adı (İstəyə bağlı)',
    modalEmailLabel: 'E-poçt Ünvanı',
    modalPhoneLabel: 'WhatsApp / Əlaqə Nömrəsi',
    modalCodeLabel: 'İstədiyiniz Partnyor Kodu (məs: BAKU-DIGITAL)',
    modalSubmit: 'Müraciəti Təsdiqlə və Linki Al',
    modalCancel: 'Bağla',
    modalSuccessTitle: 'Təbriklər! Partnyor Hesabınız Aktivdir',
    modalSuccessDesc: 'Bu linki müştərilərinizə göndərin — qeydiyyatdan keçən hər biznes avtomatik sizin balansınıza yazılır:',
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
        q: 'Satış Partnyoru (Reseller) proqramı necə işləyir?',
        a: 'Partnyor kimi qeydiyyatdan keçdikdə sizə unikal referal linki (məs: randevu.vip/?ref=AGENTLIK) verilir. Sizin linkinizlə qeydiyyatdan keçən hər biznesin aylıq abunəlik ödənişindən hər ay 20%+ komissiya qazanırsınız.',
      },
    ],
    footerTagline: 'Çoxkanallı AI Randevu və Biznes İdarəetmə Platforması',
    footerLogin: 'İdarəetmə Paneli (app.randevu.vip)',
    footerRegister: 'Biznes Qeydiyyatı',
  },
  en: {
    navFeatures: 'Features',
    navRoi: 'ROI Calculator',
    navPricing: 'Plans',
    navReseller: 'Become a Seller',
    navFaq: 'FAQ',
    navSignIn: 'Sign In',
    navStartTrial: 'Start 14-Day Free Trial',
    heroBadge: 'Universal Omnichannel AI Booking & Revenue Platform for Service Businesses',
    heroTitlePrefix: 'Stop Losing Clients to Slow Replies — Turn ',
    heroTitleHighlight: 'WhatsApp, Instagram & Telegram Into a 24/7 AI Receptionist',
    heroTitleSuffix: '',
    heroSubtitle:
      'Studies show 62% of prospects book with a competitor if they wait more than 5 minutes for a reply. Built for medical & dental clinics, beauty & wellness, auto services, legal & consulting firms, education centers, and multi-branch enterprises — Randevu.vip replies to text & voice notes in 3 seconds, books into your live calendar, and collects online deposits.',
    riskReversal: '✓ No credit card required   •   ✓ Pair via QR in 60 seconds   •   ✓ Cancel anytime',
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
    heroPrimaryCta: 'Start Your 14-Day Free Trial Now',
    heroSecondaryCta: 'Become a Seller (20%+ Recurring Commission)',
    painTitle: 'Why Manual Booking Costs Your Business Thousands Every Month',
    painOldTitle: '❌ Without Randevu.vip (Manual Reception)',
    painOldList: [
      'After-hours and weekend WhatsApp, Instagram & Telegram inquiries go unanswered.',
      'Clients fail to show up (No-Shows), leaving expensive gaps in your specialists’ calendars.',
      'Receptionists get overwhelmed juggling phone calls and 3 separate messaging apps.',
      'Listening to voice notes and manually cross-checking shifts leads to double-bookings.',
    ],
    painNewTitle: '✓ With Randevu.vip 24/7 AI Automation',
    painNewList: [
      'Instant 3-second replies at 3:00 AM across WhatsApp, Instagram Direct & Telegram in 4 languages.',
      'Automated Payriff & Paymegate deposit links eliminate no-shows before they happen.',
      'Voice AI transcribes audio messages, checks shift availability, and sends 24h & 2h reminders.',
      'Cancelled slots are automatically monetized via Last-Minute Flash Drops to your waitlist.',
    ],
    roiTitle: 'Calculate Your Recovered Revenue (Live ROI Calculator)',
    roiSubtitle: 'See how much monthly revenue you recover by capturing missed messages and preventing no-shows:',
    roiMissedLabel: 'Missed inquiries or no-shows recovered per day:',
    roiPriceLabel: 'Average appointment / service value (AZN):',
    roiMonthlyRecovered: 'Additional Monthly Revenue Recovered:',
    roiYearlyRecovered: 'Additional Annual Revenue Recovered:',
    roiNote: 'Recovering just 1 booking per month more than pays for your entire subscription.',
    howTitle: 'Go Live in 3 Simple Steps',
    howSubtitlePrefix: 'All channels and payment gateways are managed from your secure workspace at ',
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
    mostPopularBadge: '★ MOST POPULAR CHOICE',
    dailyCostAnchor: (price) => `Just ${(Number(price) / 30).toFixed(2)} AZN/day — 1 saved booking pays for the month`,
    tierSubtitles: {
      starter: 'Core WhatsApp AI booking for single-location businesses & solo specialists:',
      pro: 'Everything in Starter + Instagram Direct, Telegram Bot, Voice AI & Online Payments:',
      enterprise: 'Everything in Pro + 20 Branches, White-Label Custom Domain & Enterprise AI:',
    },
    showAllComparison: 'Show Full 29-Feature Comparison Matrix',
    showOnlyIncluded: 'Show Only Included Features per Plan',
    perMonth: '/month',
    planCta: (name) => `Start Free Trial with ${name}`,
    securityTitle: 'Enterprise-Grade Security & Data Privacy',
    securityItems: [
      {
        title: 'Tenant-Isolated Database',
        desc: 'Every business’s customer records, API keys, and conversations are strictly isolated in PostgreSQL.',
      },
      {
        title: 'TLS 1.3 & HSTS Encryption',
        desc: 'All traffic and webhook payloads are protected by 256-bit TLS encryption and strict security headers.',
      },
      {
        title: 'Certified Payment Gateways',
        desc: 'Card details never touch our servers — online checkouts run directly through Payriff and Paymegate.',
      },
      {
        title: 'AI Guardrail Protection',
        desc: 'Out-of-scope or sensitive queries automatically pause the AI and notify a human operator immediately.',
      },
    ],
    resellerBadge: 'OFFICIAL SELLER & AGENCY PARTNER PROGRAM',
    resellerTitle: 'Become a Randevu.vip Seller — Earn 20%+ Recurring Monthly Commission on Every Business You Refer',
    resellerSubtitle:
      'Built for digital agencies, SMM specialists, IT consultants, and sales professionals. Get your instant referral link and optional White-Label CNAME portal, onboard businesses across any industry, and earn monthly recurring payouts for the lifetime of each subscription.',
    resellerPerks: [
      '20%+ lifetime recurring monthly commission on every active business subscription',
      'Instant referral tracking link (randevu.vip/?ref=YOURCODE) & White-Label CNAME support',
      'High-demand AI solution easy to sell to clinics, salons, auto centers, and enterprises',
    ],
    resellerCta: 'Apply to Become an Official Seller',
    modalTitle: 'Apply to Become a Seller / Agency Partner',
    modalSubtitle: 'Complete the form below to generate your active partner account and referral link immediately.',
    modalNameLabel: 'Full Name',
    modalCompanyLabel: 'Agency / Company Name (Optional)',
    modalEmailLabel: 'Email Address',
    modalPhoneLabel: 'WhatsApp / Phone Number',
    modalCodeLabel: 'Preferred Referral Code (e.g. BAKU-AGENCY)',
    modalSubmit: 'Submit Application & Get Referral Link',
    modalCancel: 'Close',
    modalSuccessTitle: 'Welcome Aboard! Your Seller Account is Active',
    modalSuccessDesc: 'Share your unique referral link with businesses — every signup is automatically attributed to you:',
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
        q: 'How does the Seller / Reseller Partner program work?',
        a: 'When you apply via the Seller form on this page, you receive a unique referral link (e.g. randevu.vip/?ref=YOURCODE). Every business that registers through your link is permanently attributed to you, earning you 20%+ recurring monthly commission.',
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
  const [missedPerDay, setMissedPerDay] = useState(2);
  const [avgBookingPrice, setAvgBookingPrice] = useState(45);

  // Seller / Reseller Application Modal state
  const sellerDialogRef = useRef(null);
  const [sellerForm, setSellerForm] = useState({
    name: '',
    company_name: '',
    email: '',
    phone: '',
    preferred_referral_code: '',
    website_honeypot: '',
  });
  const [sellerSubmitting, setSellerSubmitting] = useState(false);
  const [sellerResult, setSellerResult] = useState(null);
  const [sellerError, setSellerError] = useState('');

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

  // Light-dismiss fallback for browsers without native dialog.closedBy support
  useEffect(() => {
    const dialog = sellerDialogRef.current;
    if (!dialog || typeof HTMLDialogElement === 'undefined') return;
    if ('closedBy' in HTMLDialogElement.prototype) return;

    const isOutside = (e) => {
      const r = dialog.getBoundingClientRect();
      return e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom;
    };
    let pressedOutside = false;
    const onDown = (e) => {
      pressedOutside = isOutside(e);
    };
    const onUp = (e) => {
      if (pressedOutside && isOutside(e)) dialog.close();
    };
    dialog.addEventListener('pointerdown', onDown);
    dialog.addEventListener('pointerup', onUp);
    return () => {
      dialog.removeEventListener('pointerdown', onDown);
      dialog.removeEventListener('pointerup', onUp);
    };
  }, []);

  const openSellerModal = () => {
    setSellerError('');
    if (sellerDialogRef.current && typeof sellerDialogRef.current.showModal === 'function') {
      sellerDialogRef.current.showModal();
    }
  };

  const closeSellerModal = () => {
    if (sellerDialogRef.current && typeof sellerDialogRef.current.close === 'function') {
      sellerDialogRef.current.close();
    }
  };

  const handleSellerSubmit = async (e) => {
    e.preventDefault();
    setSellerError('');
    setSellerSubmitting(true);
    try {
      const res = await api.post('/resellers/apply', sellerForm);
      setSellerResult(res.data);
    } catch (err) {
      setSellerError(
        err.response?.data?.detail ||
          (lang === 'en' ? 'Could not submit application. Please check your inputs.' : 'Müraciət göndərilə bilmədi. Məlumatları yoxlayın.')
      );
    } finally {
      setSellerSubmitting(false);
    }
  };

  const t = TRANSLATIONS[lang] || TRANSLATIONS.az;
  const appOrigin = getAppOrigin();
  const loginUrl = `${appOrigin}/login${refCode ? `?ref=${encodeURIComponent(refCode)}` : ''}`;
  const registerUrl = `${appOrigin}/register${refCode ? `?ref=${encodeURIComponent(refCode)}` : ''}`;

  const monthlyRecovered = missedPerDay * avgBookingPrice * 30;
  const yearlyRecovered = monthlyRecovered * 12;

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
          maxWidth: '1280px',
          margin: '0 auto',
          padding: '1.25rem 1.5rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          position: 'sticky',
          top: 0,
          zIndex: 50,
          background: 'rgba(6, 8, 15, 0.85)',
          backdropFilter: 'blur(16px)',
          borderBottom: '1px solid rgba(148, 163, 184, 0.12)',
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
          <BrandLogo size={40} fontSize="1.65rem" />
        </a>

        <nav style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', flexWrap: 'wrap' }}>
          <a href="#features" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontWeight: 500, fontSize: '0.92rem' }}>
            {t.navFeatures}
          </a>
          <a href="#roi" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontWeight: 500, fontSize: '0.92rem' }}>
            {t.navRoi}
          </a>
          <a href="#pricing" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontWeight: 500, fontSize: '0.92rem' }}>
            {t.navPricing}
          </a>
          <button
            type="button"
            onClick={openSellerModal}
            className="btn btn-gold"
            style={{ padding: '0.45rem 0.95rem', fontSize: '0.84rem' }}
          >
            <Handshake size={15} />
            {t.navReseller}
          </button>

          {/* Language Switcher (AZ default | EN) */}
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              background: 'rgba(255, 255, 255, 0.05)',
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
                padding: '0.32rem 0.68rem',
                borderRadius: '999px',
                fontSize: '0.78rem',
                fontWeight: 700,
                background: lang === 'az' ? 'var(--primary)' : 'transparent',
                color: lang === 'az' ? '#06080f' : 'var(--text-secondary)',
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
                padding: '0.32rem 0.68rem',
                borderRadius: '999px',
                fontSize: '0.78rem',
                fontWeight: 700,
                background: lang === 'en' ? 'var(--primary)' : 'transparent',
                color: lang === 'en' ? '#06080f' : 'var(--text-secondary)',
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
          maxWidth: '1140px',
          margin: '0 auto',
          padding: '4rem 1.5rem 3rem',
          textAlign: 'center',
        }}
      >
        <span className="badge badge-gold" style={{ marginBottom: '1.25rem', display: 'inline-flex', fontSize: '0.84rem' }}>
          <Sparkles size={14} /> {t.heroBadge}
        </span>
        <h1 style={{ fontSize: 'clamp(2.2rem, 4.8vw, 3.6rem)', lineHeight: 1.14, marginBottom: '1.5rem', fontWeight: 800 }}>
          {t.heroTitlePrefix}
          <span className="text-gradient">{t.heroTitleHighlight}</span>
          {t.heroTitleSuffix}
        </h1>
        <p
          style={{
            color: 'var(--text-secondary)',
            fontSize: '1.12rem',
            lineHeight: 1.65,
            maxWidth: '880px',
            margin: '0 auto 2rem',
          }}
        >
          {t.heroSubtitle}
        </p>

        {/* Multi-Industry Pills */}
        <div style={{ marginBottom: '2.25rem' }}>
          <div style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginBottom: '0.75rem', fontWeight: 600 }}>
            {t.industriesLabel}
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '0.5rem', maxWidth: '940px', margin: '0 auto' }}>
            {t.industries.map((ind, i) => (
              <span
                key={i}
                style={{
                  padding: '0.38rem 0.9rem',
                  borderRadius: '999px',
                  fontSize: '0.8rem',
                  background: 'rgba(56, 189, 248, 0.08)',
                  border: '1px solid rgba(56, 189, 248, 0.25)',
                  color: 'var(--text-primary)',
                }}
              >
                {ind}
              </span>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
          <a
            href={registerUrl}
            className="btn btn-primary"
            style={{ padding: '0.95rem 2rem', fontSize: '1.02rem', textDecoration: 'none' }}
          >
            {t.heroPrimaryCta} <ArrowRight size={18} />
          </a>
          <button
            type="button"
            onClick={openSellerModal}
            className="btn btn-gold"
            style={{ padding: '0.95rem 1.75rem', fontSize: '1rem' }}
          >
            <Handshake size={18} />
            {t.heroSecondaryCta}
          </button>
        </div>

        <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 500 }}>{t.riskReversal}</div>
      </section>

      {/* Loss Aversion: Old Way vs New Way Comparison */}
      <section style={{ maxWidth: '1200px', margin: '0 auto', padding: '2.5rem 1.5rem' }}>
        <h2 style={{ textAlign: 'center', fontSize: '1.85rem', marginBottom: '2rem' }}>{t.painTitle}</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.5rem' }}>
          <div
            className="glass-card"
            style={{
              padding: '2rem',
              border: '1px solid rgba(239, 68, 68, 0.35)',
              background: 'rgba(239, 68, 68, 0.04)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem', color: '#fca5a5' }}>
              <AlertTriangle size={22} />
              <h3 style={{ fontSize: '1.2rem', margin: 0 }}>{t.painOldTitle}</h3>
            </div>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {t.painOldList.map((item, idx) => (
                <li key={idx} style={{ display: 'flex', gap: '0.6rem', color: 'var(--text-secondary)', fontSize: '0.92rem' }}>
                  <X size={18} color="var(--danger)" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div
            className="glass-card"
            style={{
              padding: '2rem',
              border: '1px solid rgba(16, 185, 129, 0.45)',
              background: 'rgba(16, 185, 129, 0.05)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem', color: '#6ee7b7' }}>
              <CheckCircle2 size={22} />
              <h3 style={{ fontSize: '1.2rem', margin: 0 }}>{t.painNewTitle}</h3>
            </div>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {t.painNewList.map((item, idx) => (
                <li key={idx} style={{ display: 'flex', gap: '0.6rem', color: 'var(--text-primary)', fontSize: '0.92rem' }}>
                  <Check size={18} color="var(--success)" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* Interactive ROI & Lost Revenue Calculator */}
      <section id="roi" style={{ maxWidth: '1100px', margin: '0 auto', padding: '3rem 1.5rem' }}>
        <div
          className="glass-card"
          style={{
            padding: '2.5rem',
            border: '1px solid rgba(245, 158, 11, 0.4)',
            background: 'linear-gradient(135deg, rgba(13, 18, 26, 0.94), rgba(18, 24, 34, 0.88))',
          }}
        >
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <span className="badge badge-gold" style={{ marginBottom: '0.75rem' }}>
              <TrendingUp size={14} /> ROI CALCULATOR
            </span>
            <h2 style={{ fontSize: '1.9rem', marginBottom: '0.5rem' }}>{t.roiTitle}</h2>
            <p style={{ color: 'var(--text-secondary)' }}>{t.roiSubtitle}</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', alignItems: 'center' }}>
            <div>
              <div className="form-group">
                <label htmlFor="roi-missed-range" className="form-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>{t.roiMissedLabel}</span>
                  <strong style={{ color: 'var(--primary)', fontSize: '1.1rem' }}>{missedPerDay}</strong>
                </label>
                <input
                  id="roi-missed-range"
                  type="range"
                  min="1"
                  max="15"
                  value={missedPerDay}
                  onChange={(e) => setMissedPerDay(Number(e.target.value))}
                  style={{ width: '100%', accentColor: 'var(--primary)' }}
                />
              </div>

              <div className="form-group" style={{ marginBottom: 0 }}>
                <label htmlFor="roi-price-range" className="form-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>{t.roiPriceLabel}</span>
                  <strong style={{ color: 'var(--gold)', fontSize: '1.1rem' }}>{avgBookingPrice} AZN</strong>
                </label>
                <input
                  id="roi-price-range"
                  type="range"
                  min="15"
                  max="250"
                  step="5"
                  value={avgBookingPrice}
                  onChange={(e) => setAvgBookingPrice(Number(e.target.value))}
                  style={{ width: '100%', accentColor: 'var(--gold)' }}
                />
              </div>
            </div>

            <div
              style={{
                padding: '1.75rem',
                borderRadius: '16px',
                background: 'rgba(6, 8, 15, 0.75)',
                border: '1px solid rgba(16, 185, 129, 0.4)',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                {t.roiMonthlyRecovered}
              </div>
              <div style={{ fontSize: '2.6rem', fontWeight: 800, color: 'var(--success)', marginBottom: '0.75rem' }}>
                +{monthlyRecovered.toLocaleString()} AZN
                <span style={{ fontSize: '1rem', fontWeight: 500 }}>{t.perMonth}</span>
              </div>
              <div style={{ fontSize: '0.9rem', color: '#fde68a', fontWeight: 600, marginBottom: '0.75rem' }}>
                {t.roiYearlyRecovered} +{yearlyRecovered.toLocaleString()} AZN
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{t.roiNote}</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" style={{ maxWidth: '1200px', margin: '0 auto', padding: '2.5rem 1.5rem' }}>
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

      {/* Live Subscription Plans with Price Anchoring */}
      <section id="pricing" style={{ maxWidth: '1240px', margin: '0 auto', padding: '3.5rem 1.5rem' }}>
        <h2 style={{ textAlign: 'center', fontSize: '2.1rem', marginBottom: '0.5rem' }}>{t.pricingTitle}</h2>
        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
          {t.pricingSubtitle}
        </p>

        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setShowFullMatrix((prev) => !prev)}
            style={{ fontSize: '0.85rem' }}
          >
            {showFullMatrix ? t.showOnlyIncluded : t.showAllComparison}
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.75rem', alignItems: 'stretch' }}>
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
                  position: 'relative',
                  border: isPro ? '2px solid var(--gold)' : undefined,
                  boxShadow: isPro ? '0 20px 50px -10px rgba(245, 158, 11, 0.25)' : undefined,
                }}
              >
                {isPro && (
                  <div
                    className="badge badge-gold"
                    style={{
                      position: 'absolute',
                      top: '-14px',
                      left: '50%',
                      transform: 'translateX(-50%)',
                      fontWeight: 800,
                      fontSize: '0.75rem',
                      padding: '0.3rem 1rem',
                    }}
                  >
                    {t.mostPopularBadge}
                  </div>
                )}

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <h3 style={{ fontSize: '1.5rem', margin: 0 }}>{p.name}</h3>
                  {p.allows_free_trial !== false && (p.trial_days ?? 14) > 0 && (
                    <span className="badge badge-info" style={{ fontSize: '0.75rem' }}>
                      {lang === 'en' ? `${p.trial_days ?? 14}-Day Free Trial` : `${p.trial_days ?? 14} Gün Pulsuz Sınaq`}
                    </span>
                  )}
                </div>

                <div style={{ fontSize: '2.4rem', fontWeight: 800, color: isPro ? 'var(--gold)' : 'var(--primary)', marginBottom: '0.25rem' }}>
                  {p.price} AZN
                  <span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', fontWeight: 400 }}>{t.perMonth}</span>
                </div>

                <div style={{ fontSize: '0.8rem', color: 'var(--emerald)', fontWeight: 600, marginBottom: '1rem' }}>
                  {t.dailyCostAnchor(p.price)}
                </div>

                <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginBottom: '1.25rem', fontWeight: 600 }}>
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
                  className={isPro ? 'btn btn-gold' : 'btn btn-primary'}
                  style={{ justifyContent: 'center', textDecoration: 'none', width: '100%' }}
                >
                  {t.planCta(p.name)} <ArrowRight size={16} />
                </a>
              </div>
            );
          })}
        </div>
      </section>

      {/* Become a Seller / Agency Partner Section */}
      <section id="reseller" style={{ maxWidth: '1200px', margin: '0 auto', padding: '3rem 1.5rem' }}>
        <div
          className="glass-card"
          style={{
            padding: '3rem 2.5rem',
            border: '1px solid rgba(251, 191, 36, 0.45)',
            background: 'linear-gradient(135deg, rgba(24, 20, 12, 0.9), rgba(15, 20, 34, 0.92))',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '2.5rem',
            alignItems: 'center',
          }}
        >
          <div>
            <span className="badge badge-gold" style={{ marginBottom: '1rem' }}>
              <Handshake size={14} /> {t.resellerBadge}
            </span>
            <h2 style={{ fontSize: '2rem', marginBottom: '1rem', lineHeight: 1.25 }}>{t.resellerTitle}</h2>
            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.65, marginBottom: '1.5rem' }}>
              {t.resellerSubtitle}
            </p>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '2rem' }}>
              {t.resellerPerks.map((perk, i) => (
                <li key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', fontSize: '0.95rem' }}>
                  <CheckCircle2 size={18} color="var(--gold)" style={{ flexShrink: 0 }} />
                  <span>{perk}</span>
                </li>
              ))}
            </ul>
            <button
              type="button"
              onClick={openSellerModal}
              className="btn btn-gold"
              style={{ padding: '0.95rem 2rem', fontSize: '1rem' }}
            >
              <Handshake size={18} />
              {t.resellerCta}
            </button>
          </div>

          <div
            className="glass-card"
            style={{
              padding: '2rem',
              border: '1px solid rgba(251, 191, 36, 0.3)',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              {lang === 'en' ? 'Example Partner Monthly Recurring Income' : 'Nümunə Partnyor Aylıq Passiv Gəliri'}
            </div>
            <div className="text-gradient-gold" style={{ fontSize: '3rem', fontWeight: 800, marginBottom: '0.5rem' }}>
              20%+
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
              {lang === 'en'
                ? 'Refer 25 Pro businesses → Earn ~395 AZN every single month automatically.'
                : '25 Pro biznes qoşun → Hər ay avtomatik ~395 AZN davamlı komissiya qazanın.'}
            </p>
            <button
              type="button"
              onClick={openSellerModal}
              className="btn btn-secondary"
              style={{ width: '100%' }}
            >
              {t.resellerCta} <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </section>

      {/* Enterprise Security & Data Privacy Section */}
      <section style={{ maxWidth: '1200px', margin: '0 auto', padding: '2.5rem 1.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <span className="badge badge-success" style={{ marginBottom: '0.6rem' }}>
            <Lock size={13} /> SECURITY & COMPLIANCE
          </span>
          <h2 style={{ fontSize: '1.9rem' }}>{t.securityTitle}</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
          {t.securityItems.map((sec, idx) => (
            <div key={idx} className="glass-card" style={{ padding: '1.5rem' }}>
              <ShieldCheck size={22} color="var(--success)" style={{ marginBottom: '0.75rem' }} />
              <h3 style={{ fontSize: '1.05rem', marginBottom: '0.4rem' }}>{sec.title}</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.55 }}>{sec.desc}</p>
            </div>
          ))}
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

      {/* Native <dialog> Modal for Seller / Reseller Application */}
      <dialog
        ref={sellerDialogRef}
        aria-labelledby="seller-modal-title"
        {...{ closedby: 'any' }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 id="seller-modal-title" style={{ fontSize: '1.35rem', margin: 0 }}>
            {t.modalTitle}
          </h2>
          <button
            type="button"
            onClick={closeSellerModal}
            className="btn btn-secondary"
            style={{ padding: '0.35rem 0.65rem', minHeight: 'auto' }}
            aria-label={t.modalCancel}
          >
            <X size={18} />
          </button>
        </div>

        {sellerResult ? (
          <div style={{ padding: '1rem 0' }} role="status" aria-live="polite">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', color: 'var(--success)', fontWeight: 700, marginBottom: '0.75rem' }}>
              <CheckCircle2 size={22} />
              <span>{t.modalSuccessTitle}</span>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
              {t.modalSuccessDesc}
            </p>
            <div
              style={{
                padding: '0.85rem 1rem',
                borderRadius: '10px',
                background: 'rgba(16, 185, 129, 0.12)',
                border: '1px solid var(--success)',
                fontFamily: 'monospace',
                wordBreak: 'break-all',
                marginBottom: '1.25rem',
                color: '#fff',
              }}
            >
              {sellerResult.referral_url}
            </div>
            <button type="button" className="btn btn-primary" style={{ width: '100%' }} onClick={closeSellerModal}>
              {t.modalCancel}
            </button>
          </div>
        ) : (
          <form onSubmit={handleSellerSubmit} aria-labelledby="seller-modal-title">
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
              {t.modalSubtitle}
            </p>

            {/* Honeypot anti-spam field hidden from assistive tech */}
            <div className="visually-hidden" aria-hidden="true">
              <label htmlFor="seller-website-hp">Website</label>
              <input
                id="seller-website-hp"
                name="website_honeypot"
                type="text"
                tabIndex={-1}
                autoComplete="off"
                value={sellerForm.website_honeypot}
                onChange={(e) => setSellerForm({ ...sellerForm, website_honeypot: e.target.value })}
              />
            </div>

            {sellerError && (
              <div
                role="alert"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  background: 'rgba(239, 68, 68, 0.15)',
                  border: '1px solid var(--danger)',
                  color: '#fca5a5',
                  marginBottom: '1rem',
                  fontSize: '0.88rem',
                }}
              >
                <AlertTriangle size={16} />
                <span>{sellerError}</span>
              </div>
            )}

            <div className="form-group">
              <label htmlFor="seller-name" className="form-label">
                {t.modalNameLabel} <span aria-hidden="true">*</span>
              </label>
              <input
                id="seller-name"
                name="name"
                type="text"
                required
                autoFocus
                autoComplete="name"
                className="form-control"
                value={sellerForm.name}
                onChange={(e) => setSellerForm({ ...sellerForm, name: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label htmlFor="seller-company" className="form-label">
                {t.modalCompanyLabel}
              </label>
              <input
                id="seller-company"
                name="company_name"
                type="text"
                autoComplete="organization"
                className="form-control"
                value={sellerForm.company_name}
                onChange={(e) => setSellerForm({ ...sellerForm, company_name: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label htmlFor="seller-email" className="form-label">
                {t.modalEmailLabel} <span aria-hidden="true">*</span>
              </label>
              <input
                id="seller-email"
                name="email"
                type="email"
                required
                autoComplete="email"
                autoCorrect="off"
                autoCapitalize="none"
                spellCheck={false}
                className="form-control"
                value={sellerForm.email}
                onChange={(e) => setSellerForm({ ...sellerForm, email: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label htmlFor="seller-phone" className="form-label">
                {t.modalPhoneLabel} <span aria-hidden="true">*</span>
              </label>
              <input
                id="seller-phone"
                name="phone"
                type="tel"
                required
                autoComplete="tel"
                className="form-control"
                placeholder="+994 50 000 00 00"
                value={sellerForm.phone}
                onChange={(e) => setSellerForm({ ...sellerForm, phone: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label htmlFor="seller-code" className="form-label">
                {t.modalCodeLabel}
              </label>
              <input
                id="seller-code"
                name="preferred_referral_code"
                type="text"
                autoCorrect="off"
                autoCapitalize="characters"
                spellCheck={false}
                className="form-control"
                placeholder="PARTNER-BAKU"
                value={sellerForm.preferred_referral_code}
                onChange={(e) => setSellerForm({ ...sellerForm, preferred_referral_code: e.target.value })}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
              <button type="button" className="btn btn-secondary" onClick={closeSellerModal}>
                {t.modalCancel}
              </button>
              <button type="submit" disabled={sellerSubmitting} className="btn btn-gold">
                {t.modalSubmit}
              </button>
            </div>
          </form>
        )}
      </dialog>

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
              gap: '0.6rem',
              textDecoration: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
            }}
          >
            <BrandLogo size={28} fontSize="1.1rem" /> — {t.footerTagline}
          </a>
          <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
            <button
              type="button"
              onClick={openSellerModal}
              style={{ background: 'none', border: 'none', color: 'var(--gold)', cursor: 'pointer', fontWeight: 600 }}
            >
              {t.navReseller}
            </button>
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
