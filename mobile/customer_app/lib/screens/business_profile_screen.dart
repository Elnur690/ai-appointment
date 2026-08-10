import 'package:flutter/material.dart';
import 'booking_screen.dart';

class BusinessProfileScreen extends StatelessWidget {
  final String businessName;

  const BusinessProfileScreen({
    super.key,
    this.businessName = 'Beauty Studio Baku',
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(businessName)),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              height: 180,
              color: const Color(0xFF0EA5E9).withOpacity(0.2),
              child: const Center(child: Icon(Icons.store, size: 80, color: Color(0xFF0EA5E9))),
            ),
            Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(businessName, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  const Text('Hair & Beauty • Central Baku', style: TextStyle(color: Colors.grey)),
                  const SizedBox(height: 16),
                  const Text('About', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  const Text('Premium salon offering professional haircutting, styling, coloring, manicure, and beard treatments.'),
                  const SizedBox(height: 24),
                  const Text('Branches', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  const ListTile(leading: Icon(Icons.location_on), title: Text('Central Branch'), subtitle: Text('Nizami St 42')),
                  const ListTile(leading: Icon(Icons.location_on), title: Text('Mall Branch'), subtitle: Text('28 Mall 3rd Floor')),
                  const SizedBox(height: 32),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.of(context).push(MaterialPageRoute(builder: (_) => const BookingScreen()));
                      },
                      style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0EA5E9), padding: const EdgeInsets.all(16)),
                      child: const Text('Book Appointment Now', style: TextStyle(fontSize: 16, color: Colors.white)),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
