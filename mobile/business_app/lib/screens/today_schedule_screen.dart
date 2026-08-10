import 'package:flutter/material.dart';

class TodayScheduleScreen extends StatefulWidget {
  const TodayScheduleScreen({super.key});

  @override
  State<TodayScheduleScreen> createState() => _TodayScheduleScreenState();
}

class _TodayScheduleScreenState extends State<TodayScheduleScreen> {
  String _selectedStaff = 'All Staff';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Today's Schedule"),
        actions: [
          DropdownButton<String>(
            value: _selectedStaff,
            underline: const SizedBox(),
            dropdownColor: const Color(0xFF11141E),
            items: ['All Staff', 'Dr. Alex', 'Elvin A.'].map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
            onChanged: (v) => setState(() => _selectedStaff = v!),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildAgendaItem('09:00 AM', 'Opening Prep', 'Branch Staff', 'Completed', Colors.grey),
          _buildAgendaItem('10:00 AM', 'Haircut & Styling', 'Aysel Mammadova • Dr. Alex', 'Confirmed', Colors.green),
          _buildAgendaItem('11:30 AM', 'Beard Trim', 'Elvin Aliyev • Dr. Alex', 'Confirmed', Colors.green),
          _buildAgendaItem('02:00 PM', 'Manicure', 'Nigar Huseynova • Elvin A.', 'Pending', Colors.orange),
        ],
      ),
    );
  }

  Widget _buildAgendaItem(String time, String title, String subtitle, String status, Color statusColor) {
    return Card(
      color: const Color(0xFF11141E),
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: Text(time, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(subtitle),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(color: statusColor.withOpacity(0.2), borderRadius: BorderRadius.circular(8)),
          child: Text(status, style: TextStyle(color: statusColor, fontSize: 12, fontWeight: FontWeight.bold)),
        ),
      ),
    );
  }
}
