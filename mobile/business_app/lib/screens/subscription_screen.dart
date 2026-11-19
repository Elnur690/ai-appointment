import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/api_service.dart';

class SubscriptionScreen extends StatefulWidget {
  const SubscriptionScreen({super.key});

  @override
  State<SubscriptionScreen> createState() => _SubscriptionScreenState();
}

class _SubscriptionScreenState extends State<SubscriptionScreen> {
  final _api = ApiService();
  bool _loading = true;
  bool _checkingOut = false;
  Map<String, dynamic>? _subData;
  String? _selectedPlanId;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final data = await _api.getSubscription();
    if (!mounted) return;
    setState(() {
      _subData = data;
      _selectedPlanId = data?['current_plan_id']?.toString() ??
          (data?['plans'] is List && (data!['plans'] as List).isNotEmpty
              ? (data['plans'] as List).first['id']?.toString()
              : null);
      _loading = false;
    });
  }

  Future<void> _startCheckout() async {
    if (_selectedPlanId == null) return;
    setState(() => _checkingOut = true);
    try {
      final res = await _api.createSubscriptionCheckout(_selectedPlanId!);
      final url = res['checkout_url']?.toString();
      if (!mounted) return;
      if (url != null && url.isNotEmpty) {
        await Clipboard.setData(ClipboardData(text: url));
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Ödəniş linki kopyalandı! Brauzerdə açaraq ödənişi tamamlayın.')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ödəniş sorğusu yaradıldı (${res['plan_name']} - ${res['amount']} AZN).')),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Xəta: $e')),
      );
    } finally {
      if (mounted) setState(() => _checkingOut = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final plans = (_subData?['plans'] as List?) ?? [];
    final planName = _subData?['current_plan_name']?.toString() ?? '—';
    final planPrice = _subData?['current_plan_price']?.toString() ?? '0';
    final status = _subData?['subscription_status']?.toString() ?? 'trial';

    return Scaffold(
      appBar: AppBar(title: const Text('Abunəlik və Paketlər')),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : RefreshIndicator(
              onRefresh: _load,
              child: ListView(
                padding: const EdgeInsets.all(20.0),
                children: [
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: const Color(0xFF0D121A),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: const Color(0xFFD4AF37).withOpacity(0.45)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Cari Paket: $planName',
                          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFFD4AF37)),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '$planPrice AZN / ay • Status: $status',
                          style: const TextStyle(color: Colors.grey),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                  if (plans.isNotEmpty) ...[
                    const Text(
                      'Paketi Seçin və Ödəniş Edin',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      value: _selectedPlanId,
                      decoration: InputDecoration(
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      items: plans
                          .map((p) => DropdownMenuItem<String>(
                                value: p['id'].toString(),
                                child: Text('${p['name']} — ${p['price']} AZN/ay'),
                              ))
                          .toList(),
                      onChanged: (val) => setState(() => _selectedPlanId = val),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: _checkingOut ? null : _startCheckout,
                      icon: const Icon(Icons.credit_card),
                      label: Text(_checkingOut ? 'Hazırlanır...' : 'Abunəliyi Ödə / Yenilə'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFD4AF37),
                        foregroundColor: const Color(0xFF070A0E),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                    ),
                  ],
                ],
              ),
            ),
    );
  }
}
