import 'package:flutter/material.dart';

class CustomerProfileSettingsScreen extends StatefulWidget {
  const CustomerProfileSettingsScreen({super.key});

  @override
  State<CustomerProfileSettingsScreen> createState() => _CustomerProfileSettingsScreenState();
}

class _CustomerProfileSettingsScreenState extends State<CustomerProfileSettingsScreen> {
  String _language = 'Azerbaijani (az)';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Profile & Settings')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const ListTile(
            leading: CircleAvatar(child: Icon(Icons.person)),
            title: Text('Aysel Mammadova', style: TextStyle(fontWeight: FontWeight.bold)),
            subtitle: Text('+994 50 123 45 67'),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.language),
            title: const Text('Language Preference'),
            trailing: DropdownButton<String>(
              value: _language,
              items: ['Azerbaijani (az)', 'English (en)', 'Russian (ru)'].map((l) => DropdownMenuItem(value: l, child: Text(l))).toList(),
              onChanged: (v) => setState(() => _language = v!),
            ),
          ),
          const Divider(),
          const ListTile(
            leading: Icon(Icons.notifications),
            title: Text('WhatsApp & Push Reminders'),
            trailing: Icon(Icons.check_circle, color: Colors.green),
          ),
        ],
      ),
    );
  }
}
