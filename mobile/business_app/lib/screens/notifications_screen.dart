import 'package:flutter/material.dart';

class NotificationsScreen extends StatelessWidget {
  const NotificationsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Push Notifications')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildNotificationTile('New Booking', 'Aysel Mammadova booked Haircut for tomorrow at 10:00 AM', '5 min ago', Icons.calendar_today, Colors.blue),
          _buildNotificationTile('Human Takeover Request', 'Customer requested human staff support in WhatsApp chat', '15 min ago', Icons.support_agent, Colors.amber),
          _buildNotificationTile('Cancellation', 'Booking #1042 was cancelled by customer', '1 hour ago', Icons.cancel, Colors.red),
          _buildNotificationTile('Low Quota Warning', 'Your business has used 85% of monthly AI message quota', '2 hours ago', Icons.warning_amber, Colors.orange),
        ],
      ),
    );
  }

  Widget _buildNotificationTile(String title, String body, String time, IconData icon, Color color) {
    return Card(
      color: const Color(0xFF11141E),
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: Icon(icon, color: color),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text('$body\n$time'),
        isThreeLine: true,
      ),
    );
  }
}
