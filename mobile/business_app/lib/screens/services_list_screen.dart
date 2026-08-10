import 'package:flutter/material.dart';

class ServicesListScreen extends StatelessWidget {
  const ServicesListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Services Catalog'),
        actions: [
          IconButton(icon: const Icon(Icons.add), onPressed: () {}),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildServiceTile('Haircut & Styling', '30 AZN', '45 min (15 min buffer)'),
          _buildServiceTile('Beard Trim', '15 AZN', '30 min (5 min buffer)'),
          _buildServiceTile('Manicure & Polish', '25 AZN', '45 min (10 min buffer)'),
        ],
      ),
    );
  }

  Widget _buildServiceTile(String name, String price, String duration) {
    return Card(
      color: const Color(0xFF11141E),
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(duration),
        trailing: Text(price, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0EA5E9))),
      ),
    );
  }
}
