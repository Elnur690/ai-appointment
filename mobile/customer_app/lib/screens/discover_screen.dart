import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'booking_screen.dart';
import 'business_profile_screen.dart';

class DiscoverScreen extends StatefulWidget {
  const DiscoverScreen({super.key});

  @override
  State<DiscoverScreen> createState() => _DiscoverScreenState();
}

class _DiscoverScreenState extends State<DiscoverScreen> {
  final _api = CustomerApiService();
  final _searchCtrl = TextEditingController();
  String _selectedCategory = 'Hamısı';
  bool _loading = true;
  List<dynamic> _businesses = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final rows = await _api.discoverBusinesses(
      category: _selectedCategory,
      query: _searchCtrl.text,
    );
    if (!mounted) return;
    setState(() {
      _businesses = rows;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Biznesləri Kəşf Et'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(60),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: TextField(
              controller: _searchCtrl,
              onSubmitted: (_) => _load(),
              decoration: InputDecoration(
                hintText: 'Klinika, salon, mərkəz axtar...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: IconButton(icon: const Icon(Icons.arrow_forward), onPressed: _load),
                filled: true,
                fillColor: Colors.white10,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
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
              children: ['Hamısı', 'medical', 'dental', 'beauty', 'barbershop', 'auto', 'legal'].map((cat) {
                final isSel = _selectedCategory == cat;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: FilterChip(
                    label: Text(cat),
                    selected: isSel,
                    selectedColor: const Color(0xFFD4AF37).withOpacity(0.25),
                    onSelected: (sel) {
                      setState(() => _selectedCategory = cat);
                      _load();
                    },
                  ),
                );
              }).toList(),
            ),
          ),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
                : RefreshIndicator(
                    onRefresh: _load,
                    child: _businesses.isEmpty
                        ? ListView(
                            children: const [
                              SizedBox(height: 120),
                              Center(child: Text('Uyğun biznes tapılmadı.', style: TextStyle(color: Colors.grey))),
                            ],
                          )
                        : ListView.builder(
                            padding: const EdgeInsets.all(16),
                            itemCount: _businesses.length,
                            itemBuilder: (context, idx) {
                              final b = _businesses[idx] as Map<String, dynamic>;
                              final id = b['id']?.toString() ?? '';
                              final name = b['name']?.toString() ?? '';
                              final category = b['category']?.toString() ?? '';
                              final address = b['address']?.toString() ?? '';
                              return Card(
                                margin: const EdgeInsets.only(bottom: 16),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                                child: InkWell(
                                  borderRadius: BorderRadius.circular(16),
                                  onTap: () {
                                    Navigator.of(context).push(
                                      MaterialPageRoute(
                                        builder: (_) => BusinessProfileScreen(businessId: id, businessName: name),
                                      ),
                                    );
                                  },
                                  child: Column(
                                    children: [
                                      Container(
                                        height: 100,
                                        decoration: BoxDecoration(
                                          color: const Color(0xFFD4AF37).withOpacity(0.14),
                                          borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
                                        ),
                                        child: const Center(child: Icon(Icons.store, size: 42, color: Color(0xFFD4AF37))),
                                      ),
                                      ListTile(
                                        title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 17)),
                                        subtitle: Text('$category • $address'),
                                        trailing: ElevatedButton(
                                          onPressed: () {
                                            Navigator.of(context).push(
                                              MaterialPageRoute(
                                                builder: (_) => BookingScreen(businessId: id, businessName: name),
                                              ),
                                            );
                                          },
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: const Color(0xFFD4AF37),
                                            foregroundColor: const Color(0xFF070A0E),
                                          ),
                                          child: const Text('Randevu', style: TextStyle(fontWeight: FontWeight.bold)),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              );
                            },
                          ),
                  ),
          ),
        ],
      ),
    );
  }
}
