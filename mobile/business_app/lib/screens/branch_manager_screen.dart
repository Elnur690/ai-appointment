import 'package:flutter/material.dart';

class BranchManagerScreen extends StatelessWidget {
  const BranchManagerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Branch List / Switcher'),
        actions: [
          IconButton(icon: const Icon(Icons.add_location_alt), onPressed: () {}),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildBranchCard('Central Branch', 'Nizami St 42', 'Connected', Colors.green),
          _buildBranchCard('Mall Branch', '28 Mall 3rd Floor', 'Connected', Colors.green),
          _buildBranchCard('Baku White City', 'White City Blvd 12', 'Offline', Colors.red),
        ],
      ),
    );
  }

  Widget _buildBranchCard(String name, String address, String status, Color color) {
    return Card(
      color: const Color(0xFF11141E),
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: const Icon(Icons.store, color: Color(0xFF0EA5E9)),
        title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(address),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
          child: Text(status, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold)),
        ),
      ),
    );
  }
}
