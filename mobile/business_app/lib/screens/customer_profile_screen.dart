import 'package:flutter/material.dart';

class CustomerProfileScreen extends StatelessWidget {
  final String name;
  final String phone;

  const CustomerProfileScreen({
    super.key,
    this.name = 'Aysel Mammadova',
    this.phone = '+994 50 123 45 67',
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(name)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            color: const Color(0xFF11141E),
            child: ListTile(
              leading: CircleAvatar(child: Text(name[0])),
              title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text(phone),
            ),
          ),
          const SizedBox(height: 16),
          const Text('Past Appointments History', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          const ListTile(title: Text('Haircut & Styling'), subtitle: Text('Aug 10, 2026'), trailing: Text('Completed', style: TextStyle(color: Colors.green))),
          const ListTile(title: Text('Manicure & Polish'), subtitle: Text('Jul 14, 2026'), trailing: Text('Completed', style: TextStyle(color: Colors.green))),
        ],
      ),
    );
  }
}
