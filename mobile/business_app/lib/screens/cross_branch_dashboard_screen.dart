import 'package:flutter/material.dart';

class CrossBranchDashboardScreen extends StatelessWidget {
  const CrossBranchDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Cross-Branch Dashboard')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildStatCard('Total Revenue Today', '1,240 AZN', Icons.account_balance_wallet, Colors.green),
          const SizedBox(height: 12),
          _buildStatCard('Total Appointments Today', '38', Icons.calendar_month, Colors.blue),
          const SizedBox(height: 24),
          const Text('Branch Performance', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          const ListTile(title: Text('Central Branch'), subtitle: Text('24 appointments'), trailing: Text('780 AZN', style: TextStyle(fontWeight: FontWeight.bold))),
          const ListTile(title: Text('Mall Branch'), subtitle: Text('14 appointments'), trailing: Text('460 AZN', style: TextStyle(fontWeight: FontWeight.bold))),
        ],
      ),
    );
  }

  Widget _buildStatCard(String title, String val, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(color: const Color(0xFF11141E), borderRadius: BorderRadius.circular(16)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color),
          const SizedBox(height: 12),
          Text(val, style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold)),
          Text(title, style: const TextStyle(color: Colors.grey)),
        ],
      ),
    );
  }
}
