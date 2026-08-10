import 'package:flutter/material.dart';

class PaymentsLogScreen extends StatelessWidget {
  const PaymentsLogScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Payments Log'),
        actions: [
          IconButton(icon: const Icon(Icons.add_card), onPressed: () {}),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildPaymentTile('Aysel Mammadova', '30 AZN', 'Cash Payment', '10:15 AM', Colors.green),
          _buildPaymentTile('Elvin Aliyev', '15 AZN', 'Payriff Gateway', '11:45 AM', Colors.blue),
          _buildPaymentTile('Nigar Huseynova', '25 AZN', 'EPoint Gateway', '02:10 PM', Colors.blue),
        ],
      ),
    );
  }

  Widget _buildPaymentTile(String name, String amount, String method, String time, Color color) {
    return Card(
      color: const Color(0xFF11141E),
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: Icon(Icons.receipt_long, color: color),
        title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text('$method • $time'),
        trailing: Text(amount, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.green)),
      ),
    );
  }
}
