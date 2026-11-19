import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ServicesListScreen extends StatefulWidget {
  const ServicesListScreen({super.key});

  @override
  State<ServicesListScreen> createState() => _ServicesListScreenState();
}

class _ServicesListScreenState extends State<ServicesListScreen> {
  final _api = ApiService();
  bool _loading = true;
  List<dynamic> _services = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final rows = await _api.getServices();
    if (!mounted) return;
    setState(() {
      _services = rows;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Xidmətlər Kataloqu')),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : RefreshIndicator(
              onRefresh: _load,
              child: _services.isEmpty
                  ? ListView(
                      children: const [
                        SizedBox(height: 120),
                        Center(child: Text('Hələ xidmət əlavə edilməyib.', style: TextStyle(color: Colors.grey))),
                      ],
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _services.length,
                      itemBuilder: (context, idx) {
                        final s = _services[idx] as Map<String, dynamic>;
                        return Card(
                          margin: const EdgeInsets.only(bottom: 12),
                          child: ListTile(
                            leading: const Icon(Icons.spa, color: Color(0xFFD4AF37)),
                            title: Text(s['name']?.toString() ?? '', style: const TextStyle(fontWeight: FontWeight.bold)),
                            subtitle: Text('${s['duration_minutes'] ?? 30} dəq'),
                            trailing: Text(
                              '${s['price'] ?? 0} ${s['currency'] ?? 'AZN'}',
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF10B981)),
                            ),
                          ),
                        );
                      },
                    ),
            ),
    );
  }
}
