import 'package:flutter/material.dart';

class BookingScreen extends StatefulWidget {
  const BookingScreen({super.key});

  @override
  State<BookingScreen> createState() => _BookingScreenState();
}

class _BookingScreenState extends State<BookingScreen> {
  String? _selectedService = 'Haircut & Styling';
  String? _selectedTime = '10:00 AM';
  final TextEditingController _voucherController = TextEditingController();
  bool _voucherApplied = false;

  @override
  void dispose() {
    _voucherController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Book Appointment'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Select Service', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            _buildServiceCard('Haircut & Styling', '30 AZN', '45 min'),
            _buildServiceCard('Beard Trim & Shape', '15 AZN', '30 min'),
            _buildServiceCard('Full Treatment', '60 AZN', '90 min'),
            const SizedBox(height: 24),
            const Text('Select Available Time', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: ['09:00 AM', '10:00 AM', '11:30 AM (Flash -20%)', '02:00 PM', '03:30 PM'].map((time) {
                final isSelected = _selectedTime == time;
                return ChoiceChip(
                  label: Text(time),
                  selected: isSelected,
                  onSelected: (selected) => setState(() => _selectedTime = time),
                );
              }).toList(),
            ),
            const SizedBox(height: 24),
            const Text('Digital Gift Voucher', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _voucherController,
                    decoration: const InputDecoration(
                      hintText: 'Enter code (e.g. GIFT-A1B2C3D4)',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                OutlinedButton(
                  onPressed: () {
                    final code = _voucherController.text.trim().toUpperCase();
                    if (code.startsWith('GIFT-')) {
                      setState(() => _voucherApplied = true);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Gift Voucher $code applied!')),
                      );
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Please enter a valid GIFT-XXXXXXX code.')),
                      );
                    }
                  },
                  child: Text(_voucherApplied ? 'Applied ✓' : 'Apply'),
                ),
              ],
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Appointment Booked Successfully!')),
                  );
                  if (Navigator.of(context).canPop()) {
                    Navigator.of(context).pop();
                  }
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0EA5E9),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: const Text('Confirm Booking', style: TextStyle(fontSize: 16, color: Colors.white)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildServiceCard(String name, String price, String duration) {
    final isSelected = _selectedService == name;
    return Card(
      color: isSelected ? const Color(0xFF0EA5E9).withOpacity(0.12) : null,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: isSelected ? const Color(0xFF0EA5E9) : Colors.grey.shade300),
        borderRadius: BorderRadius.circular(12),
      ),
      child: ListTile(
        title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(duration),
        trailing: Text(
          price,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0EA5E9)),
        ),
        onTap: () => setState(() => _selectedService = name),
      ),
    );
  }
}
