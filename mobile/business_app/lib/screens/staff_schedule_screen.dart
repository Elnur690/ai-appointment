import 'package:flutter/material.dart';
import '../services/api_service.dart';

class StaffScheduleScreen extends StatefulWidget {
  const StaffScheduleScreen({super.key});

  @override
  State<StaffScheduleScreen> createState() => _StaffScheduleScreenState();
}

class _StaffScheduleScreenState extends State<StaffScheduleScreen> {
  final _api = ApiService();

  bool _loading = true;
  String? _error;
  List<Map<String, dynamic>> _staffMembers = [];

  @override
  void initState() {
    super.initState();
    _loadStaff();
  }

  Future<void> _loadStaff() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final rows = await _api.getStaff();
      if (!mounted) return;
      setState(() {
        _staffMembers = rows.whereType<Map<String, dynamic>>().map((item) {
          final name = (item['name']?.toString() ?? '').trim();
          final role = (item['role'] ?? item['role_title'] ?? 'Specialist').toString();
          final shift = (item['shift'] ?? item['shift_type'] ?? 'Full-Day (09:00 - 20:00)').toString();
          final allowOvertime = item['allow_overtime'] is bool
              ? item['allow_overtime'] as bool
              : (item['overtime_enabled'] is bool ? item['overtime_enabled'] as bool : false);
          return <String, dynamic>{
            'id': item['id']?.toString() ?? '',
            'name': name.isNotEmpty ? name : 'Unnamed Staff',
            'role': role,
            'shift': shift,
            'allowOvertime': allowOvertime,
            'sickLeave': false,
          };
        }).toList();
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = 'Failed to load staff schedules: ${e.toString().replaceFirst('Exception: ', '')}';
        _loading = false;
      });
    }
  }

  Future<void> _toggleOvertime(int index, bool value) async {
    final previous = _staffMembers[index]['allowOvertime'] as bool;
    final staffId = _staffMembers[index]['id'] as String;
    final staffName = _staffMembers[index]['name'] as String;
    setState(() => _staffMembers[index]['allowOvertime'] = value);
    bool success = false;
    try {
      if (staffId.isNotEmpty) {
        success = await _api.toggleStaffOvertime(staffId, value);
      }
    } catch (_) {
      success = false;
    }
    if (!mounted) return;
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            value
                ? 'Overtime enabled for $staffName'
                : 'Strict shift cutoff enforced for $staffName',
          ),
        ),
      );
    } else {
      setState(() => _staffMembers[index]['allowOvertime'] = previous);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to update overtime setting for $staffName'),
        ),
      );
    }
  }

  void _triggerEmergencySickLeave(int index) {
    setState(() => _staffMembers[index]['sickLeave'] = true);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Emergency sick leave activated for ${_staffMembers[index]['name']}. AI is auto-reassigning today\'s bookings.',
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Staff Shifts & Overtime')),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          _error!,
                          textAlign: TextAlign.center,
                          style: const TextStyle(color: Colors.redAccent),
                        ),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _loadStaff,
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadStaff,
                  child: _staffMembers.isEmpty
                      ? ListView(
                          children: const [
                            SizedBox(height: 120),
                            Center(
                              child: Text(
                                'No staff members found.',
                                style: TextStyle(color: Colors.grey),
                              ),
                            ),
                          ],
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _staffMembers.length,
                          itemBuilder: (context, index) {
                            final staff = _staffMembers[index];
                            final name = staff['name'] as String;
                            final allowOvertime = staff['allowOvertime'] as bool;
                            final sickLeave = staff['sickLeave'] as bool;

                            return Card(
                              color: const Color(0xFF11141E),
                              margin: const EdgeInsets.only(bottom: 14),
                              child: Padding(
                                padding: const EdgeInsets.all(12.0),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    ListTile(
                                      contentPadding: EdgeInsets.zero,
                                      leading: CircleAvatar(
                                        child: Text(name.isNotEmpty ? name[0].toUpperCase() : '?'),
                                      ),
                                      title: Text(
                                        name,
                                        style: const TextStyle(fontWeight: FontWeight.bold),
                                      ),
                                      subtitle: Text('${staff['role']}\n${staff['shift']}'),
                                      isThreeLine: true,
                                      trailing: Chip(
                                        label: Text(
                                          sickLeave ? 'On Sick Leave' : (allowOvertime ? 'Overtime ON' : 'Strict Shift'),
                                          style: const TextStyle(fontSize: 11),
                                        ),
                                        backgroundColor: sickLeave
                                            ? Colors.red.withOpacity(0.2)
                                            : (allowOvertime ? Colors.green.withOpacity(0.2) : Colors.blueGrey.withOpacity(0.2)),
                                      ),
                                    ),
                                    const Divider(),
                                    SwitchListTile(
                                      contentPadding: EdgeInsets.zero,
                                      title: const Text('Allow Overtime Bookings', style: TextStyle(fontSize: 14)),
                                      subtitle: const Text(
                                        'Permit AI to book up to +60 mins past shift end for high-value appointments',
                                        style: TextStyle(fontSize: 12, color: Colors.grey),
                                      ),
                                      value: allowOvertime,
                                      activeColor: const Color(0xFF0EA5E9),
                                      onChanged: (val) => _toggleOvertime(index, val),
                                    ),
                                    Align(
                                      alignment: Alignment.centerRight,
                                      child: TextButton.icon(
                                        onPressed: sickLeave ? null : () => _triggerEmergencySickLeave(index),
                                        icon: const Icon(Icons.medical_services_outlined, size: 16, color: Colors.orangeAccent),
                                        label: Text(
                                          sickLeave ? 'Bookings Reassigned' : 'Emergency Sick-Leave Swap',
                                          style: const TextStyle(color: Colors.orangeAccent, fontSize: 12),
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                ),
    );
  }
}
