import 'package:flutter/material.dart';

class StaffScheduleScreen extends StatelessWidget {
  const StaffScheduleScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Staff & Schedule Editor')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildStaffTile('Dr. Alex Smith', 'Senior Stylist', 'Mon - Fri (09:00 - 18:00)'),
          _buildStaffTile('Elvin Aliyev', 'Barber', 'Mon - Sat (10:00 - 19:00)'),
          _buildStaffTile('Nigar Huseynova', 'Manicurist', 'Tue - Sat (09:00 - 17:00)'),
        ],
      ),
    );
  }

  Widget _buildStaffTile(String name, String role, String hours) {
    return Card(
      color: const Color(0xFF11141E),
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(child: Text(name[0])),
        title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text('$role\n$hours'),
        isThreeLine: true,
        trailing: const Icon(Icons.edit, color: Color(0xFF0EA5E9)),
      ),
    );
  }
}
