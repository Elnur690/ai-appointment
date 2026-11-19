import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/api_service.dart';

class BookingScreen extends StatefulWidget {
  final String businessId;
  final String businessName;

  const BookingScreen({
    super.key,
    required this.businessId,
    required this.businessName,
  });

  @override
  State<BookingScreen> createState() => _BookingScreenState();
}

class _BookingScreenState extends State<BookingScreen> {
  final _api = CustomerApiService();
  final _nameCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  bool _loading = true;
  bool _submitting = false;
  List<dynamic> _services = [];
  List<dynamic> _staff = [];
  String? _serviceId;
  String? _staffId;
  DateTime _selectedDate = DateTime.now().add(const Duration(days: 1));
  TimeOfDay _selectedTime = const TimeOfDay(hour: 11, minute: 0);
  Map<String, dynamic>? _bookingResult;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _phoneCtrl.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    final data = await _api.resolveBusiness(widget.businessId);
    if (!mounted) return;
    final svcs = (data?['services'] as List?) ?? [];
    final stf = (data?['staff'] as List?) ?? [];
    setState(() {
      _services = svcs;
      _staff = stf;
      _serviceId = svcs.isNotEmpty ? svcs.first['id']?.toString() : null;
      _staffId = stf.isNotEmpty ? stf.first['id']?.toString() : null;
      _loading = false;
    });
  }

  Future<void> _submit() async {
    if (_serviceId == null || _staffId == null || _nameCtrl.text.trim().isEmpty || _phoneCtrl.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Zəhmət olmasa bütün xanaları doldurun.')),
      );
      return;
    }
    setState(() => _submitting = true);
    try {
      final hh = _selectedTime.hour.toString().padLeft(2, '0');
      final mm = _selectedTime.minute.toString().padLeft(2, '0');
      final res = await _api.createPublicBooking(widget.businessId, {
        'service_id': _serviceId,
        'staff_id': _staffId,
        'date': _selectedDate.toIso8601String().substring(0, 10),
        'time': '$hh:$mm',
        'customer_name': _nameCtrl.text.trim(),
        'customer_phone': _phoneCtrl.text.trim(),
      });
      if (!mounted) return;
      if (res['error'] != null) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(res['error'].toString())));
      } else {
        setState(() => _bookingResult = res['appointment'] as Map<String, dynamic>?);
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Xəta: $e')));
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Randevu — ${widget.businessName}')),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : _bookingResult != null
              ? Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.check_circle, size: 64, color: Color(0xFF10B981)),
                      const SizedBox(height: 16),
                      Text(
                        _bookingResult!['deposit_required'] == true
                            ? 'Randevu Yaradıldı — Beh Gözlənilir'
                            : 'Randevunuz Təsdiqləndi!',
                        style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 10),
                      Text(
                        '${_bookingResult!['service']} • ${_bookingResult!['staff']} • ${_bookingResult!['date']} ${_bookingResult!['time']}',
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: Colors.grey),
                      ),
                      if (_bookingResult!['deposit_required'] == true) ...[
                        const SizedBox(height: 16),
                        Text(
                          'Beh məbləği: ${_bookingResult!['deposit_amount']} AZN',
                          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFFD4AF37)),
                        ),
                        if (_bookingResult!['checkout_url'] != null) ...[
                          const SizedBox(height: 12),
                          ElevatedButton.icon(
                            onPressed: () async {
                              await Clipboard.setData(ClipboardData(text: _bookingResult!['checkout_url'].toString()));
                              if (!mounted) return;
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Beh ödəniş linki kopyalandı!')),
                              );
                            },
                            icon: const Icon(Icons.credit_card),
                            label: const Text('Beh Ödəniş Linkini Kopyala'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFFD4AF37),
                              foregroundColor: const Color(0xFF070A0E),
                            ),
                          ),
                        ],
                      ],
                    ],
                  ),
                )
              : ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    DropdownButtonFormField<String>(
                      value: _serviceId,
                      decoration: const InputDecoration(labelText: 'Xidmət', border: OutlineInputBorder()),
                      items: _services
                          .map((s) => DropdownMenuItem<String>(
                                value: s['id'].toString(),
                                child: Text('${s['name']} — ${s['price']} ${s['currency'] ?? 'AZN'}'),
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
                                child: Text('${st['name']} (${st['role']})'),
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
                          lastDate: DateTime.now().add(const Duration(days: 90)),
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
                      controller: _nameCtrl,
                      decoration: const InputDecoration(labelText: 'Adınız və Soyadınız', border: OutlineInputBorder()),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _phoneCtrl,
                      keyboardType: TextInputType.phone,
                      decoration: const InputDecoration(labelText: 'Telefon (+994...)', border: OutlineInputBorder()),
                    ),
                    const SizedBox(height: 20),
                    ElevatedButton(
                      onPressed: _submitting ? null : _submit,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFD4AF37),
                        foregroundColor: const Color(0xFF070A0E),
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: Text(
                        _submitting ? 'Göndərilir...' : 'Randevunu Təsdiqlə',
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
    );
  }
}
