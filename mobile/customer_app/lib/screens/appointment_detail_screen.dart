import 'package:flutter/material.dart';

class AppointmentDetailScreen extends StatelessWidget {
  final String serviceName;
  final String staffName;
  final String time;
  final String status;

  const AppointmentDetailScreen({
    super.key,
    required this.serviceName,
    required this.staffName,
    required this.time,
    required this.status,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Randevu Detalları')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(serviceName, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFFD4AF37))),
                const SizedBox(height: 10),
                Text('Mütəxəssis: $staffName'),
                const SizedBox(height: 8),
                Text('Vaxt: $time'),
                const SizedBox(height: 8),
                Text('Status: $status'),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
