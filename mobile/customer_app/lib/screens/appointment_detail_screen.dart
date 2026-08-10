import 'package:flutter/material.dart';

class CustomerAppointmentDetailScreen extends StatelessWidget {
  const CustomerAppointmentDetailScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Appointment Details')),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Card(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Haircut & Styling', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                    SizedBox(height: 8),
                    Text('Beauty Studio Baku • Central Branch'),
                    SizedBox(height: 4),
                    Text('Time: Tomorrow at 10:00 AM', style: TextStyle(color: Color(0xFF0EA5E9), fontWeight: FontWeight.bold)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 32),
            OutlinedButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.edit_calendar),
              label: const Text('Reschedule Appointment'),
            ),
            const SizedBox(height: 12),
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
