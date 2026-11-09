import 'package:flutter/material.dart';

class SubscriptionScreen extends StatelessWidget {
  const SubscriptionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final features = [
      'AI Engine: GPT-4o (Assigned by Randevu.vip Plan)',
      'Predictive Cadence Rebooking Engine',
      'WhatsApp Digital Gift Vouchers & Gifting',
      'Last-Minute Flash Drop Dead-Slot Monetizer',
      'Multi-Branch Location Pin & Geo-Routing',
      'Shift Overtime & Emergency Sick-Leave Swap',
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('Subscription & Entitlements')),
      body: ListView(
        padding: const EdgeInsets.all(20.0),
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color(0xFF11141E),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFF0EA5E9).withOpacity(0.4)),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Current Plan: Pro Business',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 8),
                Text('79 AZN / month • Active on randevu.vip', style: TextStyle(color: Colors.grey)),
                SizedBox(height: 20),
                Text('AI Message Usage: 750 / 1,000 messages (75%)', style: TextStyle(fontWeight: FontWeight.bold)),
                SizedBox(height: 8),
                LinearProgressIndicator(
                  value: 0.75,
                  backgroundColor: Colors.white10,
                  color: Color(0xFF0EA5E9),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'Unlocked Plan Entitlements',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          ...features.map(
            (f) => ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.check_circle, color: Colors.green, size: 20),
              title: Text(f, style: const TextStyle(fontSize: 14)),
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Redirecting to Payriff / EPoint Plan Upgrade checkout...')),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0EA5E9),
              padding: const EdgeInsets.all(16),
            ),
            child: const Center(
              child: Text('Upgrade Plan / Buy Message Overage', style: TextStyle(fontSize: 16, color: Colors.white)),
            ),
          ),
        ],
      ),
    );
  }
}
