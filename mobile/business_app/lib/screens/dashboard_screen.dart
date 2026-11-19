import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'today_schedule_screen.dart';
import 'conversations_screen.dart';
import 'staff_schedule_screen.dart';
import 'services_list_screen.dart';
import 'payments_log_screen.dart';
import 'branch_settings_screen.dart';
import 'notifications_screen.dart';
import 'calendar_screen.dart';
import 'manual_booking_screen.dart';
import 'appointment_detail_screen.dart';
import 'subscription_screen.dart';
import 'cross_branch_dashboard_screen.dart';
import 'branch_manager_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final _api = ApiService();
  int _currentIndex = 0;
  bool _loading = true;
  String _businessName = 'Randevu.vip';
  int _appointmentsThisMonth = 0;
  double _revenueThisMonth = 0.0;
  List<dynamic> _appointments = [];

  @override
  void initState() {
    super.initState();
    _loadDashboard();
  }

  Future<void> _loadDashboard() async {
    setState(() => _loading = true);
    final results = await Future.wait([
      _api.getBusinessProfile(),
      _api.getBusinessAnalytics(),
      _api.getAppointments(),
    ]);
    if (!mounted) return;
    final profile = results[0] as Map<String, dynamic>?;
    final analytics = results[1] as Map<String, dynamic>?;
    final appts = results[2] as List<dynamic>;

    setState(() {
      _businessName = profile?['name']?.toString() ?? 'Randevu.vip';
      _appointmentsThisMonth = (analytics?['appointments_this_month'] as num?)?.toInt() ?? appts.length;
      _revenueThisMonth = (analytics?['revenue_this_month'] as num?)?.toDouble() ?? 0.0;
      _appointments = appts;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final screens = [
      _buildHomeOverview(context),
      const TodayScheduleScreen(),
      const ConversationsScreen(),
      _buildOperationsHub(context),
      const BranchSettingsScreen(),
    ];

    return Scaffold(
      appBar: _currentIndex == 0 || _currentIndex == 3
          ? AppBar(
              title: Text(_currentIndex == 0 ? _businessName : 'Əməliyyat Mərkəzi'),
              actions: [
                IconButton(
                  icon: const Icon(Icons.notifications_outlined),
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const NotificationsScreen()),
                    );
                  },
                ),
              ],
            )
          : null,
      body: IndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      floatingActionButton: _currentIndex == 0 || _currentIndex == 1
          ? FloatingActionButton(
              backgroundColor: const Color(0xFFD4AF37),
              foregroundColor: const Color(0xFF070A0E),
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const ManualBookingScreen()),
                ).then((_) => _loadDashboard());
              },
              child: const Icon(Icons.add),
            )
          : null,
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (idx) => setState(() => _currentIndex = idx),
        type: BottomNavigationBarType.fixed,
        backgroundColor: const Color(0xFF0D121A),
        selectedItemColor: const Color(0xFFD4AF37),
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.dashboard), label: 'Ana səhifə'),
          BottomNavigationBarItem(icon: Icon(Icons.calendar_today), label: 'Cədvəl'),
          BottomNavigationBarItem(icon: Icon(Icons.chat), label: 'AI Çat'),
          BottomNavigationBarItem(icon: Icon(Icons.grid_view), label: 'Mərkəz'),
          BottomNavigationBarItem(icon: Icon(Icons.settings), label: 'Ayarlar'),
        ],
      ),
    );
  }

  Widget _buildHomeOverview(BuildContext context) {
    return RefreshIndicator(
      onRefresh: _loadDashboard,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Biznes Göstəriciləri', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: 1.45,
              children: [
                _buildStatCard('Aylıq Randevular', '$_appointmentsThisMonth', Icons.event_available, const Color(0xFFD4AF37)),
                _buildStatCard('Aylıq Gəlir', '${_revenueThisMonth.toStringAsFixed(0)} AZN', Icons.payments, const Color(0xFF10B981)),
              ],
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Son Randevular', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                TextButton(
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const CalendarScreen()),
                    );
                  },
                  child: const Text('Tam Təqvim', style: TextStyle(color: Color(0xFFD4AF37))),
                ),
              ],
            ),
            const SizedBox(height: 8),
            if (_loading)
              const Center(child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator()))
            else if (_appointments.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(20),
                  child: Center(child: Text('Hələ randevu yoxdur.')),
                ),
              )
            else
              ..._appointments.take(6).map((a) {
                final cust = a['customer_name']?.toString() ?? 'Müştəri';
                final svc = a['service_name']?.toString() ?? 'Xidmət';
                final time = a['start_time']?.toString().substring(0, 16).replaceAll('T', ' ') ?? '';
                final status = a['status']?.toString() ?? 'pending';
                return _buildAppointmentTile(context, a['id']?.toString() ?? '', cust, svc, time, status);
              }),
          ],
        ),
      ),
    );
  }

  Widget _buildOperationsHub(BuildContext context) {
    final items = [
      _HubAction('Abunəlik və Ödəniş', Icons.workspace_premium, const Color(0xFFD4AF37), const SubscriptionScreen()),
      _HubAction('Ödənişlər Jurnalı', Icons.receipt_long, const Color(0xFF10B981), const PaymentsLogScreen()),
      _HubAction('Xidmətlər Kataloqu', Icons.spa, const Color(0xFF0EA5E9), const ServicesListScreen()),
      _HubAction('Mütəxəssislər və Növbə', Icons.badge, Colors.orangeAccent, const StaffScheduleScreen()),
      _HubAction('Filiallar İdarəetməsi', Icons.store, const Color(0xFF10B981), const BranchManagerScreen()),
      _HubAction('Filial Analitikası', Icons.insights, const Color(0xFFD4AF37), const CrossBranchDashboardScreen()),
    ];

    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 14,
        mainAxisSpacing: 14,
        childAspectRatio: 1.15,
      ),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        return InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => item.target)),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF0D121A),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: item.color.withOpacity(0.35)),
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(item.icon, size: 34, color: item.color),
                const SizedBox(height: 12),
                Text(
                  item.title,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF0D121A),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(child: Text(title, style: const TextStyle(color: Colors.grey, fontSize: 12))),
              Icon(icon, color: color, size: 20),
            ],
          ),
          Text(value, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildAppointmentTile(BuildContext context, String id, String name, String service, String time, String status) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: const Color(0xFFD4AF37).withOpacity(0.2),
          child: const Icon(Icons.person, color: Color(0xFFD4AF37)),
        ),
        title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text('$service • $time'),
        trailing: Chip(
          label: Text(status, style: const TextStyle(fontSize: 12)),
          backgroundColor: status == 'confirmed' ? Colors.green.withOpacity(0.2) : Colors.amber.withOpacity(0.2),
        ),
        onTap: () {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (_) => AppointmentDetailScreen(
                customerName: name,
                serviceName: service,
                time: time,
                status: status,
              ),
            ),
          );
        },
      ),
    );
  }
}

class _HubAction {
  final String title;
  final IconData icon;
  final Color color;
  final Widget target;
  const _HubAction(this.title, this.icon, this.color, this.target);
}
