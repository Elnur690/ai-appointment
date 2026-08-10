import 'package:flutter/material.dart';

class DiscoverScreen extends StatefulWidget {
  const DiscoverScreen({super.key});

  @override
  State<DiscoverScreen> createState() => _DiscoverScreenState();
}

class _DiscoverScreenState extends State<DiscoverScreen> {
  String _selectedCategory = 'All';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Discover Businesses'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(60),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Search salons, clinics, fitness...',
                prefixIcon: const Icon(Icons.search),
                filled: true,
                fillColor: Colors.grey.shade100,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
              ),
            ),
          ),
        ),
      ),
      body: Column(
        children: [
          SizedBox(
            height: 50,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              children: ['All', 'Hair & Beauty', 'Dental', 'Spa & Wellness', 'Fitness'].map((cat) {
                final isSel = _selectedCategory == cat;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: FilterChip(
                    label: Text(cat),
                    selected: isSel,
                    onSelected: (sel) => setState(() => _selectedCategory = cat),
                  ),
                );
              }).toList(),
            ),
          ),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _buildBusinessCard('Beauty Studio Baku', 'Hair & Beauty • 4.9 ★', 'Nizami St 42, Baku (0.5 km)', 'https://example.com/logo.png'),
                _buildBusinessCard('Baku White City Dental', 'Dental Care • 4.8 ★', 'White City Blvd 12 (2.1 km)', 'https://example.com/logo2.png'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBusinessCard(String title, String subtitle, String address, String img) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          Container(
            height: 120,
            decoration: BoxDecoration(color: const Color(0xFF0EA5E9).withOpacity(0.2), borderRadius: const BorderRadius.vertical(top: Radius.circular(16))),
            child: const Center(child: Icon(Icons.store, size: 48, color: Color(0xFF0EA5E9))),
          ),
          ListTile(
            title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            subtitle: Text('$subtitle\n$address'),
            trailing: ElevatedButton(
              onPressed: () {},
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0EA5E9)),
              child: const Text('Book', style: TextStyle(color: Colors.white)),
            ),
          ),
        ],
      ),
    );
  }
}
