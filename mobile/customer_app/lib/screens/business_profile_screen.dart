import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'booking_screen.dart';

class BusinessProfileScreen extends StatefulWidget {
  final String businessId;
  final String businessName;

  const BusinessProfileScreen({
    super.key,
    required this.businessId,
    required this.businessName,
  });

  @override
  State<BusinessProfileScreen> createState() => _BusinessProfileScreenState();
}

class _BusinessProfileScreenState extends State<BusinessProfileScreen> {
  final _api = CustomerApiService();
  bool _loading = true;
  Map<String, dynamic>? _biz;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final data = await _api.resolveBusiness(widget.businessId);
    if (!mounted) return;
    setState(() {
      _biz = data;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final services = (_biz?['services'] as List?) ?? [];
    return Scaffold(
      appBar: AppBar(title: Text(widget.businessName)),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Text(
                  _biz?['name']?.toString() ?? widget.businessName,
                  style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFFD4AF37)),
                ),
                const SizedBox(height: 6),
                Text(_biz?['category']?.toString() ?? '', style: const TextStyle(color: Colors.grey)),
                const SizedBox(height: 20),
                const Text('Xidmətlər', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 10),
                if (services.isEmpty)
                  const Text('Xidmət tapılmadı.', style: TextStyle(color: Colors.grey))
                else
                  ...services.map((s) {
                    final item = s as Map<String, dynamic>;
                    return Card(
                      margin: const EdgeInsets.only(bottom: 10),
                      child: ListTile(
                        title: Text(item['name']?.toString() ?? ''),
                        subtitle: Text('${item['duration_minutes'] ?? 30} dəq'),
                        trailing: Text(
                          '${item['price'] ?? 0} ${item['currency'] ?? 'AZN'}',
                          style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF10B981)),
                        ),
                      ),
                    );
                  }),
                const SizedBox(height: 20),
                ElevatedButton(
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => BookingScreen(
                          businessId: widget.businessId,
                          businessName: widget.businessName,
                        ),
                      ),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFD4AF37),
                    foregroundColor: const Color(0xFF070A0E),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                  child: const Text('Onlayn Randevu Al', style: TextStyle(fontWeight: FontWeight.bold)),
                ),
              ],
            ),
    );
  }
}
