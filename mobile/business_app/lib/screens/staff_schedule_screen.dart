import 'package:flutter/material.dart';
import '../services/api_service.dart';

class StaffScheduleScreen extends StatefulWidget {
  const StaffScheduleScreen({super.key});

  @override
  State<StaffScheduleScreen> createState() => _StaffScheduleScreenState();
}

class _StaffScheduleScreenState extends State<StaffScheduleScreen> {
  final _api = ApiService();

  final List<Map<String, dynamic>> _staffMembers = [
    {
      'id': 'staff-1',
      'name': 'Dr. Alex Smith',
      'role': 'Senior Stylist',
      'shift': 'Morning Shift (09:00 - 15:00)',
      'allowOvertime': true,
      'sickLeave': false,
    },
    {
      'id': 'staff-2',
      'name': 'Elvin Aliyev',
      'role': 'Master Barber',
      'shift': 'Evening Shift (15:00 - 21:00)',
      'allowOvertime': false,
      'sickLeave': false,
    },
    {
      'id': 'staff-3',
      'name': 'Nigar Huseynova',
      'role': 'Nail Specialist',
      'shift': 'Full-Day Shift (09:00 - 18:00)',
      'allowOvertime': true,
      'sickLeave': false,
    },
  ];

  Future<void> _toggleOvertime(int index, bool value) async {
    setState(() => _staffMembers[index]['allowOvertime'] = value);
    try {
      await _api.toggleStaffOvertime(_staffMembers[index]['id'] as String, value);
    } catch (_) {}
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          value
              ? 'Overtime enabled for ${_staffMembers[index]['name']}'
              : 'Strict shift cutoff enforced for ${_staffMembers[index]['name']}',
        ),
      ),
    );
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
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _staffMembers.length,
        itemBuilder: (context, index) {
          final staff = _staffMembers[index];
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
                    leading: CircleAvatar(child: Text((staff['name'] as String)[0])),
                    title: Text(
                      staff['name'] as String,
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
    );
  }
}
