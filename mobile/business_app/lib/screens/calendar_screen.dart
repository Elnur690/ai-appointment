import 'package:flutter/material.dart';

class CalendarScreen extends StatelessWidget {
  const CalendarScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Appointments Calendar')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF11141E),
                borderRadius: BorderRadius.circular(16),
              ),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('August 2026', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  Row(
                    children: [
                      Icon(Icons.chevron_left),
                      SizedBox(width: 8),
                      Icon(Icons.chevron_right),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            _buildTimeSlot('09:00 AM', 'Available'),
            _buildTimeSlot('10:00 AM', 'Aysel Mammadova - Haircut'),
            _buildTimeSlot('11:00 AM', 'Available'),
            _buildTimeSlot('02:00 PM', 'Nigar Huseynova - Manicure'),
          ],
        ),
      ),
    );
  }

  Widget _buildTimeSlot(String time, String title) {
    final isBooked = !title.contains('Available');
    return Card(
      color: isBooked ? const Color(0xFF11141E) : Colors.transparent,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: isBooked ? const Color(0xFF0EA5E9) : Colors.white12),
        borderRadius: BorderRadius.circular(12),
      ),
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Text(time, style: const TextStyle(fontWeight: FontWeight.bold)),
        title: Text(title, style: TextStyle(color: isBooked ? Colors.white : Colors.grey)),
        trailing: isBooked ? const Icon(Icons.check_circle, color: Color(0xFF0EA5E9)) : const Icon(Icons.add_circle_outline),
      ),
    );
  }
}
