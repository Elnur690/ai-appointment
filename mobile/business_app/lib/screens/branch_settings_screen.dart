import 'package:flutter/material.dart';

class BranchSettingsScreen extends StatelessWidget {
  const BranchSettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Branch Settings')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const ListTile(
            leading: Icon(Icons.store, color: Color(0xFF0EA5E9)),
            title: Text('Central Branch'),
            subtitle: Text('Nizami St 42, Baku'),
          ),
          const Divider(),
          const ListTile(
            leading: Icon(Icons.chat, color: Colors.green),
            title: Text('WhatsApp Instance'),
            subtitle: Text('Connected (+994 50 123 45 67)'),
          ),
          const Divider(),
          const ListTile(
            leading: Icon(Icons.smart_toy, color: Colors.purple),
            title: Text('AI Agent Tone'),
            subtitle: Text('Language: AZ • Tone: Professional'),
            trailing: Icon(Icons.arrow_forward_ios, size: 16),
          ),
        ],
      ),
    );
  }
}
