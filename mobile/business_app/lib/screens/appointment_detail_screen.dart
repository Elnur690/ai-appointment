import 'package:flutter/material.dart';

class AppointmentDetailScreen extends StatelessWidget {
  final String customerName;
  final String serviceName;
  final String time;
  final String status;

  const AppointmentDetailScreen({
    super.key,
    this.customerName = 'Aysel Mammadova',
    this.serviceName = 'Haircut & Styling',
    this.time = 'Tomorrow at 10:00 AM',
    this.status = 'Confirmed',
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Appointment Details')),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Card(
              color: const Color(0xFF11141E),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    ListTile(
                      leading: CircleAvatar(child: Text(customerName[0])),
                      title: Text(customerName, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                      subtitle: const Text('+994 50 123 45 67'),
                    ),
                    const Divider(),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Service:'),
                        Text(serviceName, style: const TextStyle(fontWeight: FontWeight.bold)),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Scheduled Time:'),
                        Text(time, style: const TextStyle(fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            const Text('Update Appointment Status', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            ElevatedButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.check_circle, color: Colors.white),
              label: const Text('Mark as Completed', style: TextStyle(color: Colors.white)),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.green, padding: const EdgeInsets.all(16)),
            ),
            const SizedBox(height: 8),
            OutlinedButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.person_off, color: Colors.orange),
              label: const Text('Mark as No-Show', style: TextStyle(color: Colors.orange)),
            ),
            const SizedBox(height: 8),
            OutlinedButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.cancel, color: Colors.red),
              label: const Text('Cancel Appointment', style: TextStyle(color: Colors.red)),
            ),
          ],
        ),
      ),
    );
  }
}
