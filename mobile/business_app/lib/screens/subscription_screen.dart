import 'package:flutter/material.dart';

class SubscriptionScreen extends StatelessWidget {
  const SubscriptionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Subscription & Usage')),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(color: const Color(0xFF11141E), borderRadius: BorderRadius.circular(16)),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Current Plan: Pro Business', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                  SizedBox(height: 8),
                  Text('79 AZN / month • Renews Aug 30, 2026', style: TextStyle(color: Colors.grey)),
                  SizedBox(height: 20),
                  Text('AI Message Usage: 750 / 1000 messages (75%)', style: TextStyle(fontWeight: FontWeight.bold)),
                  SizedBox(height: 8),
                  LinearProgressIndicator(value: 0.75, backgroundColor: Colors.white10, color: Color(0xFF0EA5E9)),
                ],
              ),
            ),
            const Spacer(),
            ElevatedButton(
              onPressed: () {},
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0EA5E9), padding: const EdgeInsets.all(16)),
              child: const Center(child: Text('Upgrade Plan / Buy Overage', style: TextStyle(fontSize: 16, color: Colors.white))),
            ),
          ],
        ),
      ),
    );
  }
}
