import 'package:flutter/material.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  int _step = 1;
  final _phoneController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Setup Branch — Step $_step of 2')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: _step == 1
            ? Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Icon(Icons.qr_code_2, size: 80, color: Color(0xFF0EA5E9)),
                  const SizedBox(height: 16),
                  const Text('Link WhatsApp Instance', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
                  const SizedBox(height: 8),
                  const Text('Scan this QR code using WhatsApp on your business phone to pair the AI agent.', textAlign: TextAlign.center, style: TextStyle(color: Colors.grey)),
                  const SizedBox(height: 32),
                  Container(
                    height: 200,
                    decoration: BoxDecoration(color: Colors.white10, borderRadius: BorderRadius.circular(16)),
                    child: const Icon(Icons.qr_code, size: 140, color: Colors.white),
                  ),
                  const Spacer(),
                  ElevatedButton(
                    onPressed: () => setState(() => _step = 2),
                    style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0EA5E9), padding: const EdgeInsets.all(16)),
                    child: const Text('Next: Set Working Hours', style: TextStyle(fontSize: 16, color: Colors.white)),
                  )
                ],
              )
            : Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Icon(Icons.access_time, size: 80, color: Color(0xFF0EA5E9)),
                  const SizedBox(height: 16),
                  const Text('Configure Working Hours', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
                  const SizedBox(height: 24),
                  const ListTile(title: Text('Monday - Friday'), trailing: Text('09:00 - 18:00', style: TextStyle(fontWeight: FontWeight.bold))),
                  const ListTile(title: Text('Saturday'), trailing: Text('10:00 - 15:00', style: TextStyle(fontWeight: FontWeight.bold))),
                  const ListTile(title: Text('Sunday'), trailing: Text('Closed', style: TextStyle(color: Colors.grey))),
                  const Spacer(),
                  ElevatedButton(
                    onPressed: () => Navigator.of(context).pop(),
                    style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0EA5E9), padding: const EdgeInsets.all(16)),
                    child: const Text('Complete Onboarding', style: TextStyle(fontSize: 16, color: Colors.white)),
                  )
                ],
              ),
      ),
    );
  }
}
