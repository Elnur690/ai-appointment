import 'package:flutter/material.dart';

class ConversationsScreen extends StatefulWidget {
  const ConversationsScreen({super.key});

  @override
  State<ConversationsScreen> createState() => _ConversationsScreenState();
}

class _ConversationsScreenState extends State<ConversationsScreen> {
  bool _aiActive = true;

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
              children: [
                Icon(_aiActive ? Icons.smart_toy : Icons.person, color: _aiActive ? const Color(0xFF0EA5E9) : Colors.amber),
                const SizedBox(width: 12),
                Text(
                  _aiActive ? 'AI Agent handling messages' : 'Human Staff Takeover Mode',
                  style: TextStyle(color: _aiActive ? const Color(0xFF0EA5E9) : Colors.amber, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _buildMessageBubble('Hello! I would like to book a haircut for tomorrow.', false),
                _buildMessageBubble('Hello! We have available slots at 10:00 AM and 02:00 PM tomorrow. Which time works for you?', true),
                _buildMessageBubble('10:00 AM please.', false),
                _buildMessageBubble('Great! I have booked your Haircut & Styling for tomorrow at 10:00 AM with Dr. Alex. See you then!', true),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    decoration: InputDecoration(
                      hintText: _aiActive ? 'Take over to type message...' : 'Type message to customer...',
                      border: const OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  icon: const Icon(Icons.send, color: Color(0xFF0EA5E9)),
                  onPressed: () {},
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
