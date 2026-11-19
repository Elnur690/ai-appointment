import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/api_service.dart';

class BranchSettingsScreen extends StatefulWidget {
  const BranchSettingsScreen({super.key});

  @override
  State<BranchSettingsScreen> createState() => _BranchSettingsScreenState();
}

class _BranchSettingsScreenState extends State<BranchSettingsScreen> {
  final _api = ApiService();
  bool _loading = true;
  bool _saving = false;
  String _businessId = '';
  String _businessName = '';
  String _planName = 'Starter';
  bool _adminAllowsDeposits = false;
  bool _allowsCalendarSync = false;

  String _aiLang = 'az';
  String _depositRuleMode = 'high_risk_only';
  String _depositCalcType = 'percentage';
  final _minPriceCtrl = TextEditingController(text: '50');
  final _pctCtrl = TextEditingController(text: '20');
  final _fixedCtrl = TextEditingController(text: '10');
  bool _skipRegular = true;
  final _regularMinVisitsCtrl = TextEditingController(text: '2');

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _minPriceCtrl.dispose();
    _pctCtrl.dispose();
    _fixedCtrl.dispose();
    _regularMinVisitsCtrl.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final profile = await _api.getBusinessProfile();
    if (!mounted) return;
    if (profile != null) {
      final ent = (profile['entitlements'] as Map?) ?? {};
      final s = (profile['settings'] as Map?) ?? {};
      setState(() {
        _businessId = profile['id']?.toString() ?? '';
        _businessName = profile['name']?.toString() ?? '';
        _planName = profile['plan_name']?.toString() ?? 'Starter';
        _adminAllowsDeposits = ent['allows_no_show_deposits'] == true;
        _allowsCalendarSync = ent['allows_gcal_sync'] == true || ent['allows_apple_cal_sync'] == true;
        _aiLang = s['language']?.toString() ?? 'az';
        _depositRuleMode = s['deposit_rule_mode']?.toString() ?? 'high_risk_only';
        _depositCalcType = s['deposit_calc_type']?.toString() ?? 'percentage';
        _minPriceCtrl.text = (s['deposit_min_service_price'] ?? 50).toString();
        _pctCtrl.text = (s['deposit_percentage'] ?? 20).toString();
        _fixedCtrl.text = (s['deposit_fixed_amount'] ?? 10).toString();
        _skipRegular = s['deposit_skip_regular_customers'] != false;
        _regularMinVisitsCtrl.text = (s['deposit_regular_min_visits'] ?? 2).toString();
        _loading = false;
      });
    } else {
      setState(() => _loading = false);
    }
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    final ok = await _api.updateBusinessProfile({
      'name': _businessName,
      'settings': {
        'language': _aiLang,
        'deposit_rule_mode': _depositRuleMode,
        'deposit_calc_type': _depositCalcType,
        'deposit_min_service_price': double.tryParse(_minPriceCtrl.text) ?? 50,
        'deposit_percentage': double.tryParse(_pctCtrl.text) ?? 20,
        'deposit_fixed_amount': double.tryParse(_fixedCtrl.text) ?? 10,
        'deposit_skip_regular_customers': _skipRegular,
        'deposit_regular_min_visits': int.tryParse(_regularMinVisitsCtrl.text) ?? 2,
      },
    });
    if (!mounted) return;
    setState(() => _saving = false);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(ok ? 'Tənzimləmələr yadda saxlanıldı.' : 'Yadda saxlama zamanı xəta.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final icsUrl = 'https://api.randevu.vip/api/v1/appointments/ical-feed?business_id=$_businessId';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Biznes və Beh Tənzimləmələri'),
        actions: [
          IconButton(
            icon: const Icon(Icons.save, color: Color(0xFFD4AF37)),
            onPressed: _saving ? null : _save,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                ListTile(
                  leading: const Icon(Icons.store, color: Color(0xFFD4AF37)),
                  title: Text(_businessName.isEmpty ? 'Biznes Profili' : _businessName),
                  subtitle: Text('Aktiv Paket: $_planName'),
                ),
                const Divider(),
                const SizedBox(height: 8),
                const Text('AI Ünsiyyət Dili', style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                DropdownButtonFormField<String>(
                  value: _aiLang,
                  decoration: InputDecoration(border: OutlineInputBorder(borderRadius: BorderRadius.circular(10))),
                  items: const [
                    DropdownMenuItem(value: 'az', child: Text('Azərbaycan dili')),
                    DropdownMenuItem(value: 'en', child: Text('English')),
                    DropdownMenuItem(value: 'ru', child: Text('Русский')),
                    DropdownMenuItem(value: 'tr', child: Text('Türkçe')),
                  ],
                  onChanged: (v) => setState(() => _aiLang = v ?? 'az'),
                ),
                const SizedBox(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Beh (Ön Ödəniş) Qaydaları', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                    Chip(
                      label: Text(_adminAllowsDeposits ? 'Admin Aktiv' : 'Admin Deaktiv'),
                      backgroundColor: _adminAllowsDeposits ? Colors.green.withOpacity(0.2) : Colors.orange.withOpacity(0.2),
                    ),
                  ],
                ),
                if (!_adminAllowsDeposits)
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 8.0),
                    child: Text(
                      'Beh funksiyası hazırda Platforma Admini tərəfindən deaktiv edilib.',
                      style: TextStyle(color: Colors.grey),
                    ),
                  )
                else ...[
                  const SizedBox(height: 8),
                  DropdownButtonFormField<String>(
                    value: _depositRuleMode,
                    decoration: InputDecoration(
                      labelText: 'Kimlərdən Beh Alınsın?',
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    items: const [
                      DropdownMenuItem(value: 'high_risk_only', child: Text('Yalnız gəlməyən (No-Show) müştərilər')),
                      DropdownMenuItem(value: 'above_amount', child: Text('Müəyyən məbləğdən yuxarı xidmətlər')),
                      DropdownMenuItem(value: 'all', child: Text('Bütün randevular')),
                    ],
                    onChanged: (v) => setState(() => _depositRuleMode = v ?? 'high_risk_only'),
                  ),
                  if (_depositRuleMode == 'above_amount') ...[
                    const SizedBox(height: 12),
                    TextField(
                      controller: _minPriceCtrl,
                      keyboardType: TextInputType.number,
                      decoration: InputDecoration(
                        labelText: 'Minimum Xidmət Qiyməti (AZN)',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                  ],
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _depositCalcType,
                    decoration: InputDecoration(
                      labelText: 'Beh Hesablanması',
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    items: const [
                      DropdownMenuItem(value: 'percentage', child: Text('Xidmət qiymətinin %')),
                      DropdownMenuItem(value: 'fixed', child: Text('Sabit məbləğ (AZN)')),
                    ],
                    onChanged: (v) => setState(() => _depositCalcType = v ?? 'percentage'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _depositCalcType == 'fixed' ? _fixedCtrl : _pctCtrl,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: _depositCalcType == 'fixed' ? 'Sabit Beh (AZN)' : 'Beh Faizi (%)',
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
                  const SizedBox(height: 8),
                  SwitchListTile(
                    contentPadding: EdgeInsets.zero,
                    title: const Text('Daimi müştəriləri behdən azad et'),
                    value: _skipRegular,
                    activeColor: const Color(0xFF10B981),
                    onChanged: (v) => setState(() => _skipRegular = v),
                  ),
                  if (_skipRegular)
                    TextField(
                      controller: _regularMinVisitsCtrl,
                      keyboardType: TextInputType.number,
                      decoration: InputDecoration(
                        labelText: 'Minimum tamamlanmış ziyarət sayı',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                ],
                const SizedBox(height: 20),
                const Divider(),
                const Text('Google & Apple Təqvim (.ics)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                const SizedBox(height: 8),
                if (!_allowsCalendarSync)
                  const Text('Təqvim sinxronizasiyası cari paketinizdə aktiv deyil.', style: TextStyle(color: Colors.grey))
                else
                  OutlinedButton.icon(
                    onPressed: () async {
                      await Clipboard.setData(ClipboardData(text: icsUrl));
                      if (!mounted) return;
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Təqvim (.ics) linki kopyalandı!')),
                      );
                    },
                    icon: const Icon(Icons.copy),
                    label: const Text('Təqvim Feed Linkini (.ics) Kopyala'),
                  ),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: _saving ? null : _save,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFD4AF37),
                    foregroundColor: const Color(0xFF070A0E),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                  child: Text(_saving ? 'Yadda saxlanılır...' : 'Yadda Saxla', style: const TextStyle(fontWeight: FontWeight.bold)),
                ),
              ],
            ),
    );
  }
}
