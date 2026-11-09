import 'package:flutter/material.dart';

class ConversationsScreen extends StatefulWidget {
  const ConversationsScreen({super.key});

  @override
  State<ConversationsScreen> createState() => _ConversationsScreenState();
}

class _ConversationsScreenState extends State<ConversationsScreen> {
  bool _aiActive = true;
  bool _soloOperatorMode = true;
  final TextEditingController _messageController = TextEditingController();
  final List<Map<String, dynamic>> _messages = [
    {'text': 'Hello! I would like to book a haircut for tomorrow.', 'fromAi': false},
    {
      'text': 'Hello! We have available slots at 10:00 AM and 02:00 PM tomorrow. Which time works for you?',
      'fromAi': true,
    },
    {'text': '10:00 AM please. Also can you diagnose a scalp allergy?', 'fromAi': false},
    {
      'text':
          'I have booked your Haircut & Styling for tomorrow at 10:00 AM! Regarding the scalp question, Dr. Alex is currently with a client and will personally reply to you here as soon as he finishes.',
      'fromAi': true,
    },
  ];

  @override
  void dispose() {
    _messageController.dispose();
    super.dispose();
  }

  void _sendMessage() {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;
    setState(() {
      _aiActive = false;
      _messages.add({'text': text, 'fromAi': true});
      _messageController.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('WhatsApp AI Inbox'),
        actions: [
          Switch(
            value: _aiActive,
            activeColor: const Color(0xFF0EA5E9),
            onChanged: (val) {
              setState(() => _aiActive = val);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(val ? 'AI Agent Activated' : 'Human Staff Takeover Active')),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            color: _aiActive ? const Color(0xFF0EA5E9).withOpacity(0.1) : Colors.amber.withOpacity(0.1),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(
                      _aiActive ? Icons.smart_toy : Icons.person,
                      color: _aiActive ? const Color(0xFF0EA5E9) : Colors.amber,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      _aiActive ? 'AI Agent Active' : 'Owner / Staff Takeover',
                      style: TextStyle(
                        color: _aiActive ? const Color(0xFF0EA5E9) : Colors.amber,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                FilterChip(
                  label: Text(
                    _soloOperatorMode ? 'Solo Mode (Defer Reply)' : 'Team Handoff',
                    style: const TextStyle(fontSize: 11),
                  ),
                  selected: _soloOperatorMode,
                  onSelected: (val) => setState(() => _soloOperatorMode = val),
                ),
              ],
            ),
          ),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, idx) {
                final msg = _messages[idx];
                return _buildMessageBubble(msg['text'] as String, msg['fromAi'] as bool);
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    onSubmitted: (_) => _sendMessage(),
                    decoration: InputDecoration(
                      hintText: _aiActive ? 'Send a manual reply (auto-pauses AI)...' : 'Type message to customer...',
                      border: const OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  icon: const Icon(Icons.send, color: Color(0xFF0EA5E9)),
                  onPressed: _sendMessage,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(String text, bool isFromAi) {
    return Align(
      alignment: isFromAi ? Alignment.centerLeft : Alignment.centerRight,
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isFromAi ? const Color(0xFF11141E) : const Color(0xFF0EA5E9),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(text, style: const TextStyle(color: Colors.white)),
      ),
    );
  }
}
