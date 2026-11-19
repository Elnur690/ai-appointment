import 'package:flutter/material.dart';

class CustomerProfileScreen extends StatelessWidget {
  final String customerName;
  final String phone;
  final List<dynamic> history;

  const CustomerProfileScreen({
    super.key,
    required this.customerName,
    required this.phone,
    this.history = const [],
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(customerName)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          ListTile(
            leading: const CircleAvatar(
              backgroundColor: Color(0xFFD4AF37),
              child: Icon(Icons.person, color: Color(0xFF070A0E)),
            ),
            title: Text(customerName, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            subtitle: Text(phone),
          ),
          const Divider(),
          const SizedBox(height: 8),
          const Text('Ziyarət Tarixçəsi', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 8),
          if (history.isEmpty)
            const Text('Ziyarət tarixçəsi yoxdur.', style: TextStyle(color: Colors.grey))
          else
            ...history.map((h) {
              final item = h as Map<String, dynamic>;
              return ListTile(
                title: Text(item['service_name']?.toString() ?? 'Xidmət'),
                subtitle: Text(item['start_time']?.toString() ?? ''),
                trailing: Text(item['status']?.toString() ?? ''),
              );
            }),
        ],
      ),
    );
  }
}
