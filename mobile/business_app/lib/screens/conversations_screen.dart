import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ConversationsScreen extends StatefulWidget {
  const ConversationsScreen({super.key});

  @override
  State<ConversationsScreen> createState() => _ConversationsScreenState();
}

class _ConversationsScreenState extends State<ConversationsScreen> {
  final _api = ApiService();
  bool _loading = true;
  List<dynamic> _conversations = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final rows = await _api.getConversations();
    if (!mounted) return;
    setState(() {
      _conversations = rows;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Müştəri Yazışmaları (AI)')),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : RefreshIndicator(
              onRefresh: _load,
              child: _conversations.isEmpty
                  ? ListView(
                      children: const [
                        SizedBox(height: 120),
                        Center(child: Text('Hələ aktiv yazışma yoxdur.', style: TextStyle(color: Colors.grey))),
                      ],
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _conversations.length,
                      itemBuilder: (context, idx) {
                        final c = _conversations[idx] as Map<String, dynamic>;
                        final id = c['id']?.toString() ?? '';
                        final phone = c['customer_phone']?.toString() ?? c['customer_name']?.toString() ?? 'Müştəri';
                        final channel = c['channel']?.toString() ?? 'whatsapp';
                        final status = c['status']?.toString() ?? 'ai_active';

                        return Card(
                          margin: const EdgeInsets.only(bottom: 12),
                          child: ListTile(
                            leading: CircleAvatar(
                              backgroundColor: const Color(0xFFD4AF37).withOpacity(0.18),
                              child: const Icon(Icons.chat_bubble_outline, color: Color(0xFFD4AF37)),
                            ),
                            title: Text(phone, style: const TextStyle(fontWeight: FontWeight.bold)),
                            subtitle: Text('Kanal: $channel • Status: $status'),
                            trailing: TextButton(
                              onPressed: () async {
                                final ok = await _api.takeoverConversation(id);
                                if (!mounted) return;
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text(ok ? 'Canlı operator rejiminə keçildi.' : 'Əməliyyat alınmadı.')),
                                );
                                _load();
                              },
                              child: const Text('Takeover', style: TextStyle(color: Color(0xFFD4AF37))),
                            ),
                          ),
                        );
                      },
                    ),
            ),
    );
  }
}
