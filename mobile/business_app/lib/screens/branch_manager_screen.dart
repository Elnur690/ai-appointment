import 'package:flutter/material.dart';
import '../services/api_service.dart';

class BranchManagerScreen extends StatefulWidget {
  const BranchManagerScreen({super.key});

  @override
  State<BranchManagerScreen> createState() => _BranchManagerScreenState();
}

class _BranchManagerScreenState extends State<BranchManagerScreen> {
  final _api = ApiService();
  bool _loading = true;
  List<dynamic> _branches = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final rows = await _api.getBranches();
    if (!mounted) return;
    setState(() {
      _branches = rows;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Filiallar')),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : RefreshIndicator(
              onRefresh: _load,
              child: _branches.isEmpty
                  ? ListView(
                      children: const [
                        SizedBox(height: 120),
                        Center(child: Text('Filial tapılmadı.', style: TextStyle(color: Colors.grey))),
                      ],
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _branches.length,
                      itemBuilder: (context, idx) {
                        final b = _branches[idx] as Map<String, dynamic>;
                        final active = b['is_active'] != false;
                        return Card(
                          margin: const EdgeInsets.only(bottom: 12),
                          child: ListTile(
                            leading: Icon(Icons.store, color: active ? const Color(0xFF10B981) : Colors.grey),
                            title: Text(b['name']?.toString() ?? '', style: const TextStyle(fontWeight: FontWeight.bold)),
                            subtitle: Text(b['address']?.toString() ?? b['timezone']?.toString() ?? 'Asia/Baku'),
                            trailing: Text(
                              active ? 'Aktiv' : 'Deaktiv',
                              style: TextStyle(color: active ? const Color(0xFF10B981) : Colors.redAccent),
                            ),
                          ),
                        );
                      },
                    ),
            ),
    );
  }
}
