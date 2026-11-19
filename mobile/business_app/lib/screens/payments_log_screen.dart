import 'package:flutter/material.dart';
import '../services/api_service.dart';

class PaymentsLogScreen extends StatefulWidget {
  const PaymentsLogScreen({super.key});

  @override
  State<PaymentsLogScreen> createState() => _PaymentsLogScreenState();
}

class _PaymentsLogScreenState extends State<PaymentsLogScreen> {
  final _api = ApiService();
  bool _loading = true;
  List<dynamic> _payments = [];
  double _totalRevenue = 0.0;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final res = await Future.wait([_api.getPayments(), _api.getPaymentsSummary()]);
    if (!mounted) return;
    final list = res[0] as List<dynamic>;
    final summary = res[1] as Map<String, dynamic>;
    setState(() {
      _payments = list;
      _totalRevenue = (summary['total_revenue'] as num?)?.toDouble() ?? 0.0;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Ödənişlər və Beh Jurnalı')),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : RefreshIndicator(
              onRefresh: _load,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  Container(
                    padding: const EdgeInsets.all(16),
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: const Color(0xFF0D121A),
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: const Color(0xFF10B981).withOpacity(0.4)),
                    ),
                    child: Text(
                      'Ümumi Gəlir: ${_totalRevenue.toStringAsFixed(2)} AZN',
                      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF10B981)),
                    ),
                  ),
                  if (_payments.isEmpty)
                    const Center(
                      child: Padding(
                        padding: EdgeInsets.all(32),
                        child: Text('Hələ ödəniş qeydə alınmayıb.', style: TextStyle(color: Colors.grey)),
                      ),
                    )
                  else
                    ..._payments.map((p) {
                      final m = p as Map<String, dynamic>;
                      final method = (m['method']?.toString() ?? 'cash').toLowerCase();
                      final label = method == 'cash' ? 'Nağd Ödəniş' : 'Onlayn Kart / Beh';
                      return Card(
                        margin: const EdgeInsets.only(bottom: 10),
                        child: ListTile(
                          leading: Icon(
                            method == 'cash' ? Icons.payments : Icons.credit_card,
                            color: const Color(0xFFD4AF37),
                          ),
                          title: Text(m['customer']?.toString() ?? label, style: const TextStyle(fontWeight: FontWeight.bold)),
                          subtitle: Text('$label • ${m['status'] ?? ''}'),
                          trailing: Text(
                            m['amount']?.toString() ?? '0 AZN',
                            style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF10B981)),
                          ),
                        ),
                      );
                    }),
                ],
              ),
            ),
    );
  }
}
