import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'appointment_detail_screen.dart';

class AppointmentsHistoryScreen extends StatefulWidget {
  const AppointmentsHistoryScreen({super.key});

  @override
  State<AppointmentsHistoryScreen> createState() => _AppointmentsHistoryScreenState();
}

class _AppointmentsHistoryScreenState extends State<AppointmentsHistoryScreen> {
  final _api = CustomerApiService();
  bool _loading = true;
  List<dynamic> _appointments = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final rows = await _api.getMyAppointments();
    if (!mounted) return;
    setState(() {
      _appointments = rows;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Randevularım')),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : RefreshIndicator(
              onRefresh: _load,
              child: _appointments.isEmpty
                  ? ListView(
                      children: const [
                        SizedBox(height: 120),
                        Center(child: Text('Hələ randevu tarixçəniz yoxdur.', style: TextStyle(color: Colors.grey))),
                      ],
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _appointments.length,
                      itemBuilder: (context, idx) {
                        final a = _appointments[idx] as Map<String, dynamic>;
                        final svc = a['service_name']?.toString() ?? 'Xidmət';
                        final staff = a['staff_name']?.toString() ?? '';
                        final time = a['start_time']?.toString() ?? '';
                        final status = a['status']?.toString() ?? '';
                        return Card(
                          margin: const EdgeInsets.only(bottom: 12),
                          child: ListTile(
                            leading: const Icon(Icons.calendar_today, color: Color(0xFFD4AF37)),
                            title: Text(svc, style: const TextStyle(fontWeight: FontWeight.bold)),
                            subtitle: Text('$staff • $time'),
                            trailing: Text(status),
                            onTap: () {
                              Navigator.of(context).push(
                                MaterialPageRoute(
                                  builder: (_) => AppointmentDetailScreen(
                                    serviceName: svc,
                                    staffName: staff,
                                    time: time,
                                    status: status,
                                  ),
                                ),
                              );
                            },
                          ),
                        );
                      },
                    ),
            ),
    );
  }
}
