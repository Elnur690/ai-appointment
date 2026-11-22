import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BrandLogo } from '../components/common/BrandLogo';
import { ArrowLeft, Shield, FileText, RotateCcw, Cookie, CheckCircle2, Mail } from 'lucide-react';

const POLICIES = {
  terms: {
    icon: FileText,
    titleEn: 'Terms of Service',
    titleAz: 'İstifadə Şərtləri',
    updated: '2026-11-22',
    sectionsEn: [
      {
        heading: '1. Overview & Acceptance',
        body: 'Randevu.vip ("Platform", "we", "us") provides a cloud-based AI appointment scheduling, WhatsApp/Instagram/Telegram automation, CRM, and business management Software-as-a-Service (SaaS) platform for salons, clinics, barbershops, spas, and service businesses. By creating an account, starting a trial, or purchasing a subscription, you agree to these Terms of Service.',
      },
      {
        heading: '2. Eligibility & Account Security',
        body: 'You must be at least 18 years old and authorized to act on behalf of the business you register. You must register with a valid business or standard email address (disposable/temporary email addresses are not permitted). You are responsible for safeguarding your login credentials and connected messaging channels.',
      },
      {
        heading: '3. Subscriptions, Billing & Auto-Renewal',
        body: 'Randevu.vip is offered on a recurring monthly subscription basis with transparent plan tiers published on our pricing page. Payments for Randevu.vip SaaS plans and add-ons are securely processed via our payment processor (Suby.fi) supporting credit/debit cards, Apple Pay/Google Pay, and supported digital payment methods. Subscriptions renew automatically each billing cycle unless canceled prior to the renewal date from your Business Dashboard → Payments & Billing.',
      },
      {
        heading: '4. Direct Customer Deposits ("Beh")',
        body: 'Businesses using Randevu.vip may optionally connect their own local merchant accounts (such as Payriff or EPoint) to collect booking deposits directly from their end customers. Randevu.vip does not hold, custody, or settle end-customer deposit funds; each business is solely responsible for its own merchant account, local tax obligations, and customer deposit refunds.',
      },
      {
        heading: '5. Service Availability & Acceptable Use',
        body: 'We strive for 99.9% uptime. You agree not to use Randevu.vip for spam, unsolicited bulk messaging, illegal services, fraudulent transactions, or any activity violating WhatsApp/Meta policies or applicable laws. We reserve the right to suspend accounts that violate this policy.',
      },
      {
        heading: '6. Intellectual Property & Data Ownership',
        body: 'All platform software, branding, and AI orchestration remain the intellectual property of Randevu.vip. You retain full ownership of your business data, customer records, appointment history, and knowledge base content.',
      },
      {
        heading: '7. Limitation of Liability & Governing Law',
        body: 'To the maximum extent permitted by law, Randevu.vip shall not be liable for indirect, incidental, or consequential damages, and our total aggregate liability shall not exceed the subscription fees paid by you in the preceding 3 months. These Terms are governed by the laws of the Republic of Azerbaijan.',
      },
    ],
    sectionsAz: [
      {
        heading: '1. Ümumi Müddəalar və Razılaşma',
        body: 'Randevu.vip ("Platforma", "biz") salonlar, klinikalar, bərbərxanalar, spa mərkəzləri və xidmət biznesləri üçün bulud əsaslı AI randevu idarəetməsi, WhatsApp/Instagram/Telegram avtomatlaşdırılması və CRM SaaS platforması təqdim edir. Hesab yaratmaqla və ya abunəlik almaqla bu İstifadə Şərtlərini qəbul etmiş olursunuz.',
      },
      {
        heading: '2. Hesab Təhlükəsizliyi və Qeydiyyat',
        body: 'Qeydiyyatdan keçən şəxs ən azı 18 yaşında olmalı və təmsil etdiyi biznes adından çıxış etmək səlahiyyətinə malik olmalıdır. Qeydiyyat yalnız etibarlı domen və ya tanınmış e-poçt ünvanları ilə mümkündür (müvəqqəti/birdəfəlik e-poçtlar qadağandır).',
      },
      {
        heading: '3. Abunəliklər, Ödəniş və Avtomatik Yenilənmə',
        body: 'Randevu.vip aylıq təkrarlanan SaaS abunəlik paketləri əsasında təqdim olunur. SaaS paket ödənişləri Suby.fi ödəniş infrastrukturu vasitəsilə təhlükəsiz şəkildə emal edilir. Abunəliklər Biznes Paneli → Ödənişlər bölməsindən ləğv edilmədiyi təqdirdə hər dövr avtomatik yenilənir.',
      },
      {
        heading: '4. Birbaşa Müştəri Beh (Depozit) Ödənişləri',
        body: 'Bizneslər öz müştərilərindən beh qəbul etmək üçün öz Payriff və ya EPoint hesablarını birbaşa paneldən qoşa bilərlər. Bu ödənişlər vasitəçisiz birbaşa biznesin hesabına köçürülür və müştəri behlərinə görə məsuliyyət müvafiq biznesə aiddir.',
      },
      {
        heading: '5. Məqbul İstifadə və Məsuliyyət',
        body: 'Platformadan spam, qanunsuz fəaliyyət və ya WhatsApp/Meta qaydalarını pozan məqsədlər üçün istifadə qadağandır. Biznes məlumatları və müştəri bazası tamamilə sizin mülkiyyətinizdə qalır.',
      },
    ],
  },
  privacy: {
    icon: Shield,
    titleEn: 'Privacy Policy',
    titleAz: 'Məxfilik Siyasəti',
    updated: '2026-11-22',
    sectionsEn: [
      {
        heading: '1. Information We Collect',
        body: 'We collect information you provide directly when registering and using Randevu.vip: business name, owner name, email address, phone number, service catalog, staff schedules, appointment records, and customer messages processed through your connected WhatsApp, Instagram, or Telegram channels.',
      },
      {
        heading: '2. Payment Data & PCI-DSS Security',
        body: 'Randevu.vip never stores raw credit or debit card numbers on our servers. All SaaS subscription payments are processed on PCI-DSS compliant hosted checkout pages operated by Suby.fi. Business-owned local gateway keys (Payriff / EPoint) entered in your dashboard are encrypted at rest using authenticated symmetric encryption (Fernet/AES) and masked in all API responses.',
      },
      {
        heading: '3. How We Use Information',
        body: 'We use your data strictly to deliver the Randevu.vip service: automating appointment booking, sending appointment reminders, syncing Google/Apple calendars, billing your subscription, preventing fraud/disposable-email abuse, and providing customer support. We never sell your personal or customer data to third parties.',
      },
      {
        heading: '4. Third-Party Sub-Processors',
        body: 'To operate the service, we rely on vetted infrastructure and API partners including cloud hosting providers, AI language model providers (for generating booking responses), Suby.fi (subscription billing), and Resend/SMTP (transactional emails).',
      },
      {
        heading: '5. Data Retention & Your Rights',
        body: 'You may access, export, update, or request permanent deletion of your account and associated business data at any time from your dashboard or by emailing support@randevu.vip. Upon account cancellation, active data is retained for up to 30 days for recovery or billing audit purposes unless immediate deletion is requested.',
      },
    ],
    sectionsAz: [
      {
        heading: '1. Topladığımız Məlumatlar',
        body: 'Qeydiyyat və istifadə zamanı təqdim etdiyiniz məlumatlar (biznes adı, e-poçt, telefon, xidmət siyahısı, işçi cədvəlləri, randevu tarixçəsi və qoşulmuş WhatsApp/Instagram/Telegram mesajları) yalnız xidmətin göstərilməsi üçün emal olunur.',
      },
      {
        heading: '2. Ödəniş Təhlükəsizliyi',
        body: 'Randevu.vip kart məlumatlarını öz serverlərində saxlamır. Bütün abunəlik ödənişləri PCI-DSS standartlı Suby.fi səhifəsində emal edilir. Bizneslərin daxil etdiyi Payriff/EPoint açarları bazada şifrələnmiş (Fernet) şəkildə saxlanılır.',
      },
      {
        heading: '3. Məlumatların İstifadəsi və Mühafizəsi',
        body: 'Məlumatlarınız heç vaxt üçüncü tərəflərə satılmır. İstənilən vaxt məlumatlarınızın silinməsini və ya ixracını support@randevu.vip ünvanına yazaraq tələb edə bilərsiniz.',
      },
    ],
  },
  refund: {
    icon: RotateCcw,
    titleEn: 'Refund & Cancellation Policy',
    titleAz: 'Geri Ödəniş və Ləğv Siyasəti',
    updated: '2026-11-22',
    sectionsEn: [
      {
        heading: '1. Free Trial Before Billing',
        body: 'Eligible new accounts receive a free trial period (up to 14 days depending on the selected plan) so you can evaluate Randevu.vip before being charged. You may cancel during the trial at no cost.',
      },
      {
        heading: '2. Subscription Cancellation',
        body: 'You can cancel your monthly SaaS subscription at any time directly from your Business Dashboard → Payments & Billing or Settings → Cancel Account. Cancellation stops all future recurring charges immediately. You retain access until the end of your current paid billing period unless you request immediate account closure.',
      },
      {
        heading: '3. Refund Eligibility & Processing',
        body: 'If you are unsatisfied with Randevu.vip or were billed in error, you may request a full refund within 14 calendar days of your most recent subscription charge directly from Business Dashboard → Payments → Request Refund, or by emailing support@randevu.vip with your account email and payment reference. Qualifying requests within our automated refund window (48 hours) are approved automatically; all other requests are reviewed within 2 business days.',
      },
      {
        heading: '4. Refund Method & Timeline',
        body: 'Approved refunds are issued back to the original payment method (credit/debit card or original payment rail via Suby.fi). Card refunds typically appear on your statement within 5–10 business days depending on your issuing bank.',
      },
      {
        heading: '5. End-Customer Booking Deposits ("Beh")',
        body: 'Booking deposits paid by salon/clinic end-customers go directly to the respective business’s own Payriff or EPoint merchant account. Refund requests for service appointments or booking deposits must be directed to the specific business where the appointment was booked.',
      },
    ],
    sectionsAz: [
      {
        heading: '1. Ödənişsiz Sınaq Müddəti',
        body: 'Yeni biznes hesabları seçilmiş paketə uyğun olaraq ödənişsiz sınaq müddəti əldə edirlər. Sınaq müddətində abunəliyi heç bir ödəniş etmədən ləğv edə bilərsiniz.',
      },
      {
        heading: '2. Abunəliyin Ləğv Edilməsi',
        body: 'Aylıq SaaS abunəliyinizi istənilən vaxt Biznes Paneli → Ödənişlər və ya Tənzimləmələr bölməsindən dərhal ləğv edə bilərsiniz. Ləğv edildikdə növbəti dövrlər üçün avtomatik çıxılma dayandırılır.',
      },
      {
        heading: '3. Geri Ödəniş Şərtləri və Müddəti',
        body: 'Son abunəlik ödənişinizdən sonra 14 təqvim günü ərzində Biznes Panelindən və ya support@randevu.vip ünvanından geri ödəniş tələb edə bilərsiniz. 48 saat ərzindəki uyğun tələblər avtomatik təsdiqlənir, digər müraciətlərə 2 iş günü ərzində baxılır. Təsdiqlənmiş məbləğ 5–10 iş günü ərzində ilkin ödəniş üsuluna qaytarılır.',
      },
      {
        heading: '4. Müştəri Beh (Depozit) Ödənişləri',
        body: 'Randevu zamanı müştərilərin ödədiyi beh birbaşa müvafiq biznesin öz Payriff/EPoint hesabına köçürüldüyü üçün, xidmət behlərinin qaytarılması birbaşa həmin biznes tərəfindən həyata keçirilir.',
      },
    ],
  },
  cookies: {
    icon: Cookie,
    titleEn: 'Cookie Policy',
    titleAz: 'Kuki (Cookie) Siyasəti',
    updated: '2026-11-22',
    sectionsEn: [
      {
        heading: '1. What Cookies We Use',
        body: 'Randevu.vip uses strictly necessary browser storage and cookies to keep you signed in securely (JWT session tokens), remember your interface language preference (Azerbaijani / English), and protect against unauthorized access.',
      },
      {
        heading: '2. Third-Party Payment & Integration Cookies',
        body: 'When you proceed to checkout on Suby.fi, Payriff, or EPoint, those payment processors may set their own security and fraud-prevention cookies subject to their respective privacy policies. Randevu.vip does not use invasive third-party advertising trackers.',
      },
      {
        heading: '3. Managing Cookies',
        body: 'You can clear or block cookies in your browser settings at any time; however, disabling essential authentication storage will prevent you from staying logged into the Business Dashboard.',
      },
    ],
    sectionsAz: [
      {
        heading: '1. İstifadə Etdiyimiz Kukilər',
        body: 'Randevu.vip yalnız sistemə təhlükəsiz giriş (sessiya tokeni) və dil seçiminizin (AZ / EN) yadda saxlanılması üçün zəruri brauzer kukilərindən istifadə edir.',
      },
      {
        heading: '2. Üçüncü Tərəf Ödəniş Kukiləri',
        body: 'Suby.fi, Payriff və ya EPoint ödəniş səhifələrinə keçid etdikdə həmin ödəniş provayderlərinin təhlükəsizlik kukiləri tətbiq oluna bilər. Platformamız reklam izləmə kukilərindən istifadə etmir.',
      },
    ],
  },
  acceptableUse: {
    icon: CheckCircle2,
    titleEn: 'Acceptable Use Policy',
    titleAz: 'Məqbul İstifadə Siyasəti',
    updated: '2026-11-22',
    sectionsEn: [
      {
        heading: '1. Permitted Business Use',
        body: 'Randevu.vip is designed exclusively for legitimate appointment-based service businesses (salons, barbershops, medical/dental/aesthetic clinics, spas, fitness studios, consultants, and repair centers) to manage bookings, customer communication, and scheduling.',
      },
      {
        heading: '2. Prohibited Activities',
        body: 'You may not use Randevu.vip to send unsolicited spam, conduct phishing or fraud, promote illegal goods or restricted financial schemes, impersonate third parties, or bypass Meta/WhatsApp anti-spam safeguards. Violations result in immediate account termination without refund.',
      },
    ],
    sectionsAz: [
      {
        heading: '1. İcazə Verilən İstifadə',
        body: 'Randevu.vip yalnız qanuni xidmət bizneslərinin (salonlar, klinikalar, bərbərxanalar, spa, məsləhət xidmətləri və s.) randevu və müştəri əlaqələrinin idarə edilməsi üçün nəzərdə tutulub.',
      },
      {
        heading: '2. Qadağan Olunmuş Fəaliyyətlər',
        body: 'Spam göndərişi, dələduzluq, qanunsuz xidmətlərin təşviqi və ya WhatsApp/Meta qaydalarının pozulması qəti qadağandır və hesabın dərhal bloklanmasına səbəb olur.',
      },
    ],
  },
};

const ROUTE_TO_KEY = {
  '/terms': 'terms',
  '/privacy': 'privacy',
  '/refund-policy': 'refund',
  '/returns': 'refund',
  '/cookies': 'cookies',
  '/acceptable-use': 'acceptableUse',
};

const LegalPolicyPage = ({ defaultPolicy = 'terms' }) => {
  const location = useLocation();
  const activeKey = ROUTE_TO_KEY[location.pathname] || defaultPolicy;
  const [lang, setLang] = useState('en');
  const isAz = lang === 'az';
  const policy = POLICIES[activeKey] || POLICIES.terms;
  const Icon = policy.icon;
  const sections = isAz ? policy.sectionsAz : policy.sectionsEn;

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
      {/* Header */}
      <header
        style={{
          borderBottom: '1px solid var(--border)',
          padding: '1rem 1.5rem',
          background: 'var(--header-bg, rgba(15, 23, 42, 0.88))',
          backdropFilter: 'blur(12px)',
          position: 'sticky',
          top: 0,
          zIndex: 20,
        }}
      >
        <div
          style={{
            maxWidth: '960px',
            margin: '0 auto',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', textDecoration: 'none', color: 'inherit' }}>
            <BrandLogo size={30} fontSize="1.15rem" />
          </Link>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ display: 'flex', border: '1px solid var(--border)', borderRadius: '8px', overflow: 'hidden' }}>
              <button
                type="button"
                onClick={() => setLang('en')}
                style={{
                  padding: '0.35rem 0.65rem',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  background: !isAz ? 'var(--primary)' : 'transparent',
                  color: !isAz ? '#fff' : 'var(--text-secondary)',
                }}
              >
                EN
              </button>
              <button
                type="button"
                onClick={() => setLang('az')}
                style={{
                  padding: '0.35rem 0.65rem',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  background: isAz ? 'var(--primary)' : 'transparent',
                  color: isAz ? '#fff' : 'var(--text-secondary)',
                }}
              >
                AZ
              </button>
            </div>
            <Link to="/" className="btn btn-secondary" style={{ textDecoration: 'none', padding: '0.45rem 0.9rem', fontSize: '0.85rem' }}>
              <ArrowLeft size={15} /> {isAz ? 'Ana Səhifə' : 'Back to Home'}
            </Link>
          </div>
        </div>
      </header>

      <main style={{ maxWidth: '960px', margin: '0 auto', padding: '2.5rem 1.5rem 4rem' }}>
        {/* Policy Navigation Pills */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem', marginBottom: '2rem' }}>
          {[
            { to: '/terms', key: 'terms', en: 'Terms of Service', az: 'İstifadə Şərtləri' },
            { to: '/privacy', key: 'privacy', en: 'Privacy Policy', az: 'Məxfilik Siyasəti' },
            { to: '/refund-policy', key: 'refund', en: 'Refund & Cancellation Policy', az: 'Geri Ödəniş Siyasəti' },
            { to: '/cookies', key: 'cookies', en: 'Cookie Policy', az: 'Kuki Siyasəti' },
            { to: '/acceptable-use', key: 'acceptableUse', en: 'Acceptable Use', az: 'Məqbul İstifadə' },
          ].map((item) => (
            <Link
              key={item.key}
              to={item.to}
              style={{
                padding: '0.45rem 0.9rem',
                borderRadius: '999px',
                fontSize: '0.84rem',
                textDecoration: 'none',
                fontWeight: activeKey === item.key ? 700 : 500,
                border: `1px solid ${activeKey === item.key ? 'var(--primary)' : 'var(--border)'}`,
                background: activeKey === item.key ? 'rgba(99, 102, 241, 0.16)' : 'transparent',
                color: activeKey === item.key ? 'var(--text-primary)' : 'var(--text-secondary)',
              }}
            >
              {isAz ? item.az : item.en}
            </Link>
          ))}
        </div>

        {/* Content Card */}
        <article className="glass-card" style={{ padding: '2.25rem', lineHeight: 1.7 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <Icon size={26} color="var(--primary)" />
            <h1 style={{ fontSize: '1.85rem', fontWeight: 800, margin: 0 }}>
              {isAz ? policy.titleAz : policy.titleEn}
            </h1>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '2rem' }}>
            {isAz ? `Son yenilənmə tarixi: ${policy.updated}` : `Last updated: ${policy.updated}`} · Randevu.vip
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {sections.map((sec, i) => (
              <section key={i}>
                <h2 style={{ fontSize: '1.12rem', fontWeight: 700, marginBottom: '0.45rem', color: 'var(--text-primary)' }}>
                  {sec.heading}
                </h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.96rem', margin: 0 }}>
                  {sec.body}
                </p>
              </section>
            ))}
          </div>

          {/* Merchant / Compliance Contact Block */}
          <div
            style={{
              marginTop: '2.5rem',
              padding: '1.25rem',
              borderRadius: '12px',
              background: 'rgba(99, 102, 241, 0.08)',
              border: '1px solid rgba(99, 102, 241, 0.25)',
              fontSize: '0.9rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, marginBottom: '0.4rem' }}>
              <Mail size={16} color="var(--primary)" />
              {isAz ? 'Əlaqə və Hüquqi Məlumatlar' : 'Contact & Merchant Information'}
            </div>
            <div style={{ color: 'var(--text-secondary)' }}>
              <strong>Randevu.vip</strong> — AI Appointment & Business Automation SaaS
              <br />
              {isAz ? 'Dəstək və Geri Ödəniş E-poçtu:' : 'Support & Billing Email:'}{' '}
              <a href="mailto:support@randevu.vip" style={{ color: 'var(--primary)' }}>
                support@randevu.vip
              </a>
              <br />
              {isAz ? 'Ünvan: Bakı, Azərbaycan · Veb-sayt: https://randevu.vip' : 'Location: Baku, Azerbaijan · Website: https://randevu.vip'}
            </div>
          </div>
        </article>
      </main>
    </div>
  );
};

export default LegalPolicyPage;
