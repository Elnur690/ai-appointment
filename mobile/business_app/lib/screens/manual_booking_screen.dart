import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ManualBookingScreen extends StatefulWidget {
  const ManualBookingScreen({super.key});

  @override
  State<ManualBookingScreen> createState() => _ManualBookingScreenState();
}

class _ManualBookingScreenState extends State<ManualBookingScreen> {
  final _api = ApiService();
  final _notesCtrl = TextEditingController();
  bool _loading = true;
  bool _submitting = false;
  List<dynamic> _services = [];
  List<dynamic> _staff = [];
  List<dynamic> _customers = [];
  String? _serviceId;
  String? _staffId;
  String? _customerId;
  DateTime _selectedDate = DateTime.now().add(const Duration(days: 1));
  TimeOfDay _selectedTime = const TimeOfDay(hour: 11, minute: 0);

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _notesCtrl.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    final res = await Future.wait([_api.getServices(), _api.getStaff(), _api.getCustomers()]);
    if (!mounted) return;
    setState(() {
      _services = res[0];
      _staff = res[1];
      _customers = res[2];
      _serviceId = _services.isNotEmpty ? _services.first['id']?.toString() : null;
      _staffId = _staff.isNotEmpty ? _staff.first['id']?.toString() : null;
      _customerId = _customers.isNotEmpty ? _customers.first['id']?.toString() : null;
      _loading = false;
    });
  }

  Future<void> _submit() async {
    if (_serviceId == null || _staffId == null || _customerId == null) return;
    setState(() => _submitting = true);
    final dt = DateTime(
      _selectedDate.year,
      _selectedDate.month,
      _selectedDate.day,
      _selectedTime.hour,
      _selectedTime.minute,
    );
    final ok = await _api.createAppointment({
      'service_id': _serviceId,
      'staff_id': _staffId,
      'customer_id': _customerId,
      'start_time': dt.toUtc().toIso8601String(),
      'notes': _notesCtrl.text.trim(),
    });
    if (!mounted) return;
    setState(() => _submitting = false);
    if (ok) {
      Navigator.of(context).pop(true);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Randevu yaradıla bilmədi.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Yeni Randevu Yarat')),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                DropdownButtonFormField<String>(
                  value: _customerId,
                  decoration: const InputDecoration(labelText: 'Müştəri', border: OutlineInputBorder()),
                  items: _customers
                      .map((c) => DropdownMenuItem<String>(
                            value: c['id'].toString(),
                            child: Text(c['name']?.toString() ?? c['phone_number']?.toString() ?? ''),
                          ))
                      .toList(),
                  onChanged: (v) => setState(() => _customerId = v),
                ),
                const SizedBox(height: 14),
                DropdownButtonFormField<String>(
                  value: _serviceId,
                  decoration: const InputDecoration(labelText: 'Xidmət', border: OutlineInputBorder()),
                  items: _services
                      .map((s) => DropdownMenuItem<String>(
                            value: s['id'].toString(),
                            child: Text('${s['name']} (${s['price']} ${s['currency'] ?? 'AZN'})'),
                          ))
                      .toList(),
                  onChanged: (v) => setState(() => _serviceId = v),
                ),
                const SizedBox(height: 14),
                DropdownButtonFormField<String>(
                  value: _staffId,
                  decoration: const InputDecoration(labelText: 'Mütəxəssis', border: OutlineInputBorder()),
                  items: _staff
                      .map((st) => DropdownMenuItem<String>(
                            value: st['id'].toString(),
                            child: Text(st['name']?.toString() ?? ''),
                          ))
                      .toList(),
                  onChanged: (v) => setState(() => _staffId = v),
                ),
                const SizedBox(height: 14),
                ListTile(
                  title: Text('Tarix: ${_selectedDate.toIso8601String().substring(0, 10)}'),
                  trailing: const Icon(Icons.calendar_today, color: Color(0xFFD4AF37)),
                  onTap: () async {
                    final picked = await showDatePicker(
                      context: context,
                      initialDate: _selectedDate,
                      firstDate: DateTime.now(),
                      lastDate: DateTime.now().add(const Duration(days: 180)),
                    );
                    if (picked != null) setState(() => _selectedDate = picked);
                  },
                ),
                ListTile(
                  title: Text('Saat: ${_selectedTime.format(context)}'),
                  trailing: const Icon(Icons.access_time, color: Color(0xFFD4AF37)),
                  onTap: () async {
                    final picked = await showTimePicker(context: context, initialTime: _selectedTime);
                    if (picked != null) setState(() => _selectedTime = picked);
                  },
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _notesCtrl,
                  decoration: const InputDecoration(labelText: 'Qeyd (İstəyə bağlı)', border: OutlineInputBorder()),
                ),
                const SizedBox(height: 20),
                ElevatedButton(
                  onPressed: _submitting ? null : _submit,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFD4AF37),
                    foregroundColor: const Color(0xFF070A0E),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                  child: Text(_submitting ? 'Yaradılır...' : 'Randevunu Yadda Saxla', style: const TextStyle(fontWeight: FontWeight.bold)),
                ),
              ],
            ),
    );
  }
}
