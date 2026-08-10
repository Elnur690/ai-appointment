import 'package:flutter/material.dart';

class CustomerHomeScreen extends StatelessWidget {
  const CustomerHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Home'),
        actions: [
          IconButton(icon: const Icon(Icons.notifications_none), onPressed: () {}),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Upcoming Appointment', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Card(
            color: const Color(0xFF0EA5E9).withOpacity(0.1),
            shape: RoundedRectangleBorder(side: const BorderSide(color: Color(0xFF0EA5E9)), borderRadius: BorderRadius.circular(16)),
            child: const Padding(
              padding: EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Haircut & Styling', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      Chip(label: Text('Tomorrow 10:00 AM', style: TextStyle(fontSize: 12))),
                    ],
                  ),
                  SizedBox(height: 8),
                  Text('Beauty Studio Baku • Central Branch', style: TextStyle(color: Colors.grey)),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          const Text('Quick Rebook', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          ListTile(
            leading: const CircleAvatar(child: Icon(Icons.store)),
            title: const Text('Beauty Studio Baku'),
            subtitle: const Text('Last visited Jul 28, 2026'),
            trailing: OutlinedButton(onPressed: () {}, child: const Text('Rebook')),
          ),
        ],
      ),
    );
  }
}
