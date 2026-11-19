import 'package:flutter/material.dart';
import '../services/api_service.dart';

class TodayScheduleScreen extends StatefulWidget {
  const TodayScheduleScreen({super.key});

  @override
  State<TodayScheduleScreen> createState() => _TodayScheduleScreenState();
}

class _TodayScheduleScreenState extends State<TodayScheduleScreen> {
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
    final todayPrefix = DateTime.now().toIso8601String().substring(0, 10);
    setState(() {
      _appointments = rows.where((r) => (r['start_time']?.toString() ?? '').startsWith(todayPrefix)).toList();
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Bugünkü Cədvəl')),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : RefreshIndicator(
              onRefresh: _load,
              child: _appointments.isEmpty
                  ? ListView(
                      children: const [
                        SizedBox(height: 120),
                        Center(child: Text('Bu gün üçün randevu yoxdur.', style: TextStyle(color: Colors.grey))),
                      ],
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _appointments.length,
                      itemBuilder: (context, idx) {
                        final a = _appointments[idx] as Map<String, dynamic>;
                        final time = a['start_time']?.toString().substring(11, 16) ?? '';
                        return Card(
                          margin: const EdgeInsets.only(bottom: 10),
                          child: ListTile(
                            leading: Text(time, style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFFD4AF37))),
                            title: Text(a['service_name']?.toString() ?? 'Xidmət'),
                            subtitle: Text('${a['customer_name'] ?? 'Müştəri'} • ${a['staff_name'] ?? ''}'),
                            trailing: Text(a['status']?.toString() ?? ''),
                          ),
                        );
                      },
                    ),
            ),
    );
  }
}
