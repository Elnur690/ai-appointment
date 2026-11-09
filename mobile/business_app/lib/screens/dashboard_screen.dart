import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'appointment_detail_screen.dart';
import 'branch_manager_screen.dart';
import 'branch_settings_screen.dart';
import 'calendar_screen.dart';
import 'conversations_screen.dart';
import 'cross_branch_dashboard_screen.dart';
import 'customer_profile_screen.dart';
import 'login_screen.dart';
import 'manual_booking_screen.dart';
import 'notifications_screen.dart';
import 'onboarding_screen.dart';
import 'payments_log_screen.dart';
import 'services_list_screen.dart';
import 'staff_schedule_screen.dart';
import 'subscription_screen.dart';
import 'today_schedule_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final pages = [
      _buildOverviewTab(context),
      const CalendarScreen(),
      const ConversationsScreen(),
      _buildOperationsHubTab(context),
    ];

    return Scaffold(
      appBar: _currentIndex == 0 || _currentIndex == 3
          ? AppBar(
              title: Text(_currentIndex == 0 ? 'Beauty Studio Baku' : 'Operations & Growth Hub'),
              actions: [
                IconButton(
                  tooltip: 'Notifications',
                  icon: const Icon(Icons.notifications_outlined),
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const NotificationsScreen()),
                    );
                  },
                ),
                IconButton(
                  tooltip: 'Add Walk-In Booking',
                  icon: const Icon(Icons.add_circle_outline, color: Color(0xFF0EA5E9)),
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const ManualBookingScreen()),
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
        backgroundColor: const Color(0xFF11141E),
        selectedItemColor: const Color(0xFF0EA5E9),
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.dashboard_outlined), label: 'Dashboard'),
          BottomNavigationBarItem(icon: Icon(Icons.calendar_month_outlined), label: 'Calendar'),
          BottomNavigationBarItem(icon: Icon(Icons.chat_bubble_outline), label: 'WhatsApp AI'),
          BottomNavigationBarItem(icon: Icon(Icons.grid_view_rounded), label: 'Operations'),
        ],
      ),
    );
  }

  Widget _buildOverviewTab(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Today Overview',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              TextButton.icon(
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const TodayScheduleScreen()),
                  );
                },
                icon: const Icon(Icons.schedule, size: 16),
                label: const Text("Today's Agenda"),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _buildStatCard('Appointments', '12', Icons.calendar_today, Colors.blue),
              const SizedBox(width: 12),
              _buildStatCard('Revenue', '340 AZN', Icons.attach_money, Colors.green),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _buildStatCard('Cadence Rebooked', '5', Icons.autorenew, Colors.purpleAccent),
              const SizedBox(width: 12),
              _buildStatCard('Flash Drops Filled', '3 slots', Icons.flash_on, Colors.amber),
            ],
          ),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Upcoming Appointments',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              TextButton(
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const ManualBookingScreen()),
                  );
                },
                child: const Text('+ Walk-In'),
              ),
            ],
          ),
          const SizedBox(height: 8),
          _buildAppointmentTile(context, 'Aysel Mammadova', 'Haircut & Styling', '10:00 AM', 'Confirmed'),
          _buildAppointmentTile(context, 'Elvin Aliyev', 'Beard Trim', '11:30 AM', 'Confirmed'),
          _buildAppointmentTile(context, 'Nigar Huseynova', 'Manicure', '02:00 PM', 'Pending'),
        ],
      ),
    );
  }

  Widget _buildOperationsHubTab(BuildContext context) {
    final actions = <_HubAction>[
      _HubAction('Staff & Shifts (Overtime)', Icons.badge_outlined, Colors.cyan, const StaffScheduleScreen()),
      _HubAction('Services Catalog', Icons.content_cut, Colors.blue, const ServicesListScreen()),
      _HubAction('Walk-In / Phone Booking', Icons.person_add_alt_1, Colors.teal, const ManualBookingScreen()),
      _HubAction('Payments & Vouchers Log', Icons.receipt_long, Colors.green, const PaymentsLogScreen()),
      _HubAction('Branches & Geo-Routing', Icons.store_mall_directory_outlined, Colors.amber, const BranchManagerScreen()),
      _HubAction('Cross-Branch Analytics', Icons.insights, Colors.purpleAccent, const CrossBranchDashboardScreen()),
      _HubAction('Branch & AI Guardrails', Icons.tune, Colors.indigoAccent, const BranchSettingsScreen()),
      _HubAction('WhatsApp QR Onboarding', Icons.qr_code_scanner, Colors.lightGreen, const OnboardingScreen()),
      _HubAction('Customer CRM Profile', Icons.people_outline, Colors.pinkAccent, const CustomerProfileScreen()),
      _HubAction('Plan & AI Entitlements', Icons.workspace_premium, Colors.orangeAccent, const SubscriptionScreen()),
    ];

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        ...actions.map(
          (item) => Card(
            color: const Color(0xFF11141E),
            margin: const EdgeInsets.only(bottom: 10),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: item.color.withOpacity(0.15),
                child: Icon(item.icon, color: item.color),
              ),
              title: Text(item.title, style: const TextStyle(fontWeight: FontWeight.bold)),
              trailing: const Icon(Icons.chevron_right, color: Colors.grey),
              onTap: () {
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => item.screen),
                );
              },
            ),
          ),
        ),
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: () async {
            await ApiService().logout();
            if (!context.mounted) return;
            Navigator.of(context).pushAndRemoveUntil(
              MaterialPageRoute(builder: (_) => const LoginScreen()),
              (_) => false,
            );
          },
          icon: const Icon(Icons.logout, color: Colors.redAccent),
          label: const Text('Sign Out', style: TextStyle(color: Colors.redAccent)),
        ),
      ],
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF11141E),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.white10),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: color),
            const SizedBox(height: 8),
            Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
          ],
        ),
      ),
    );
  }

  Widget _buildAppointmentTile(
    BuildContext context,
    String name,
    String service,
    String time,
    String status,
  ) {
    return Card(
      color: const Color(0xFF11141E),
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
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
        leading: GestureDetector(
          onTap: () {
            Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => CustomerProfileScreen(name: name),
              ),
            );
          },
          child: CircleAvatar(child: Text(name[0])),
        ),
        title: Text(name),
        subtitle: Text('$service • $time'),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: status == 'Confirmed' ? Colors.green.withOpacity(0.2) : Colors.orange.withOpacity(0.2),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            status,
            style: TextStyle(
              color: status == 'Confirmed' ? Colors.green : Colors.orange,
              fontSize: 12,
            ),
          ),
        ),
      ),
    );
  }
}

class _HubAction {
  final String title;
  final IconData icon;
  final Color color;
  final Widget screen;

  const _HubAction(this.title, this.icon, this.color, this.screen);
}
