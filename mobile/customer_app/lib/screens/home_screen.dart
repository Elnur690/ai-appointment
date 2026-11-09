import 'package:flutter/material.dart';
import 'appointment_detail_screen.dart';
import 'appointments_history_screen.dart';
import 'booking_screen.dart';
import 'business_profile_screen.dart';
import 'discover_screen.dart';
import 'profile_screen.dart';

class CustomerHomeScreen extends StatefulWidget {
  const CustomerHomeScreen({super.key});

  @override
  State<CustomerHomeScreen> createState() => _CustomerHomeScreenState();
}

class _CustomerHomeScreenState extends State<CustomerHomeScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final pages = [
      _buildHomeTab(context),
      const DiscoverScreen(),
      const AppointmentsHistoryScreen(),
      const CustomerProfileSettingsScreen(),
    ];

    return Scaffold(
      appBar: _currentIndex == 0
          ? AppBar(
              title: const Text('Randevu.vip'),
              actions: [
                IconButton(
                  icon: const Icon(Icons.card_giftcard, color: Color(0xFF0EA5E9)),
                  tooltip: 'Redeem Gift Voucher',
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const BookingScreen()),
                    );
                  },
                ),
              ],
            )
          : null,
      body: pages[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (idx) => setState(() => _currentIndex = idx),
        type: BottomNavigationBarType.fixed,
        selectedItemColor: const Color(0xFF0EA5E9),
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home_outlined), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.explore_outlined), label: 'Discover'),
          BottomNavigationBarItem(icon: Icon(Icons.calendar_today_outlined), label: 'Appointments'),
          BottomNavigationBarItem(icon: Icon(Icons.person_outline), label: 'Profile'),
        ],
      ),
    );
  }

  Widget _buildHomeTab(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text('Upcoming Appointment', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 12),
        InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: () {
            Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const CustomerAppointmentDetailScreen()),
            );
          },
          child: Card(
            color: const Color(0xFF0EA5E9).withOpacity(0.1),
            shape: RoundedRectangleBorder(
              side: const BorderSide(color: Color(0xFF0EA5E9)),
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Padding(
              padding: EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Haircut & Styling', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      Chip(label: Text('Tomorrow 10:00 AM', style: TextStyle(fontSize: 12))),
                    ],
                  ),
                  SizedBox(height: 8),
                  Text('Beauty Studio Baku • Central Branch', style: TextStyle(color: Colors.grey)),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(height: 24),
        const Text('Predictive Cadence Rebook', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 12),
        Card(
          child: ListTile(
            leading: const CircleAvatar(child: Icon(Icons.store)),
            title: const Text('Beauty Studio Baku'),
            subtitle: const Text('3 weeks since your last visit • Recommended slot ready'),
            trailing: OutlinedButton(
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const BookingScreen()),
                );
              },
              child: const Text('Rebook'),
            ),
            onTap: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const BusinessProfileScreen()),
              );
            },
          ),
        ),
        const SizedBox(height: 24),
        const Text('Last-Minute Flash Drops (-20%)', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 12),
        Card(
          color: Colors.amber.withOpacity(0.12),
          child: ListTile(
            leading: const Icon(Icons.flash_on, color: Colors.amber),
            title: const Text('Beauty Studio Baku — 11:30 AM Today'),
            subtitle: const Text('Instant 20% off cancelled slot (24 AZN instead of 30 AZN)'),
            trailing: ElevatedButton(
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const BookingScreen()),
                );
              },
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0EA5E9)),
              child: const Text('Claim', style: TextStyle(color: Colors.white)),
            ),
          ),
        ),
      ],
    );
  }
}
