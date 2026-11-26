import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'discover_screen.dart';
import 'appointments_history_screen.dart';
import 'profile_screen.dart';
import 'booking_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _api = CustomerApiService();
  int _currentIndex = 0;
  bool _loading = true;
  List<dynamic> _appointments = [];
  List<dynamic> _businesses = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final res = await Future.wait([
      _api.getMyAppointments(),
      _api.discoverBusinesses(),
    ]);
    if (!mounted) return;
    setState(() {
      _appointments = res[0];
      _businesses = res[1];
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final screens = [
      _buildHomeTab(context),
      const DiscoverScreen(),
      const AppointmentsHistoryScreen(),
      const CustomerProfileSettingsScreen(),
    ];

    return Scaffold(
      appBar: _currentIndex == 0
          ? AppBar(
              title: const Text('Randevu.vip', style: TextStyle(color: Color(0xFFD4AF37), fontWeight: FontWeight.bold)),
            )
          : null,
      body: IndexedStack(index: _currentIndex, children: screens),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (idx) => setState(() => _currentIndex = idx),
        type: BottomNavigationBarType.fixed,
        backgroundColor: const Color(0xFF0D121A),
        selectedItemColor: const Color(0xFFD4AF37),
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Ana səhifə'),
          BottomNavigationBarItem(icon: Icon(Icons.explore), label: 'Kəşf et'),
          BottomNavigationBarItem(icon: Icon(Icons.calendar_month), label: 'Randevularım'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profil'),
        ],
      ),
    );
  }

  Widget _buildHomeTab(BuildContext context) {
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Qarşıdakı Randevularım', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          if (_loading)
            const Center(child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator()))
          else if (_appointments.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Text('Qarşıdakı randevunuz yoxdur.', style: TextStyle(color: Colors.grey)),
              ),
            )
          else
            ..._appointments.take(3).map((a) {
              final item = a as Map<String, dynamic>;
              return Card(
                margin: const EdgeInsets.only(bottom: 10),
                child: ListTile(
                  leading: const Icon(Icons.event_available, color: Color(0xFFD4AF37)),
                  title: Text(item['service_name']?.toString() ?? 'Xidmət'),
                  subtitle: Text('${item['start_time'] ?? ''} • ${item['status'] ?? ''}'),
                ),
              );
            }),
          const SizedBox(height: 20),
          const Text('Platformadakı Bizneslər', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          if (_businesses.isEmpty && !_loading)
            const Text('Hələ biznes tapılmadı.', style: TextStyle(color: Colors.grey))
          else
            ..._businesses.take(5).map((b) {
              final item = b as Map<String, dynamic>;
              final id = item['id']?.toString() ?? '';
              final name = item['name']?.toString() ?? '';
              return Card(
                margin: const EdgeInsets.only(bottom: 10),
                child: ListTile(
                  leading: const Icon(Icons.store, color: Color(0xFFD4AF37)),
                  title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text('${item['category'] ?? ''} • ${item['address'] ?? ''}'),
                  trailing: ElevatedButton(
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => BookingScreen(businessId: id, businessName: name)),
                      );
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFD4AF37),
                      foregroundColor: const Color(0xFF070A0E),
                    ),
                    child: const Text('Yazıl'),
                  ),
                ),
              );
            }),
        ],
      ),
    );
  }
}
