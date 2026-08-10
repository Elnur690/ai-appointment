import 'package:flutter/material.dart';

class AppointmentsHistoryScreen extends StatelessWidget {
  const AppointmentsHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Appointments')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildAppointmentCard('Haircut & Styling', 'Beauty Studio Baku', 'Tomorrow, 10:00 AM', 'Confirmed', Colors.green),
          _buildAppointmentCard('Manicure & Polish', 'Beauty Studio Baku', 'Aug 15, 02:00 PM', 'Confirmed', Colors.green),
          _buildAppointmentCard('Beard Trim', 'Beauty Studio Baku', 'Jul 28, 11:30 AM', 'Completed', Colors.blue),
        ],
      ),
    );
  }

  Widget _buildAppointmentCard(String service, String branch, String date, String status, Color statusColor) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        title: Text(service, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text('$branch • $date'),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: statusColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(status, style: TextStyle(color: statusColor, fontWeight: FontWeight.bold, fontSize: 12)),
        ),
      ),
    );
  }
}
