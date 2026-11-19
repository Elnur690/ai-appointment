import 'package:flutter/material.dart';
import '../services/api_service.dart';

class CalendarScreen extends StatefulWidget {
  const CalendarScreen({super.key});

  @override
  State<CalendarScreen> createState() => _CalendarScreenState();
}

class _CalendarScreenState extends State<CalendarScreen> {
  final _api = ApiService();
  bool _loading = true;
  List<dynamic> _appointments = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
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
      appBar: AppBar(title: const Text('Tam Təqvim')),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : RefreshIndicator(
              onRefresh: _load,
              child: _appointments.isEmpty
                  ? ListView(
                      children: const [
                        SizedBox(height: 120),
                        Center(child: Text('Təqvimdə randevu yoxdur.', style: TextStyle(color: Colors.grey))),
                      ],
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _appointments.length,
                      itemBuilder: (context, idx) {
                        final a = _appointments[idx] as Map<String, dynamic>;
                        final dt = a['start_time']?.toString().substring(0, 16).replaceAll('T', ' ') ?? '';
                        return Card(
                          margin: const EdgeInsets.only(bottom: 10),
                          child: ListTile(
                            leading: const Icon(Icons.event, color: Color(0xFFD4AF37)),
                            title: Text('${a['customer_name'] ?? 'Müştəri'} — ${a['service_name'] ?? 'Xidmət'}'),
                            subtitle: Text('$dt • ${a['staff_name'] ?? ''}'),
                            trailing: Text(a['status']?.toString() ?? ''),
                          ),
                        );
                      },
                    ),
            ),
    );
  }
}
