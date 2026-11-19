import 'package:flutter/material.dart';
import '../services/api_service.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  final _api = ApiService();
  bool _loading = true;
  List<dynamic> _appointments = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final rows = await _api.getAppointments();
    if (!mounted) return;
    setState(() {
      _appointments = rows;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Bildirişlər')),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : _appointments.isEmpty
              ? const Center(child: Text('Yeni bildiriş yoxdur.', style: TextStyle(color: Colors.grey)))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _appointments.length,
                  itemBuilder: (context, idx) {
                    final a = _appointments[idx] as Map<String, dynamic>;
                    return Card(
                      margin: const EdgeInsets.only(bottom: 10),
                      child: ListTile(
                        leading: const Icon(Icons.notifications_active, color: Color(0xFFD4AF37)),
                        title: Text('${a['customer_name'] ?? 'Müştəri'} — ${a['service_name'] ?? 'Xidmət'}'),
                        subtitle: Text('Status: ${a['status'] ?? ''} • ${a['start_time'] ?? ''}'),
                      ),
                    );
                  },
                ),
    );
  }
}
