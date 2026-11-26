import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'home_screen.dart';

class OtpLoginScreen extends StatefulWidget {
  const OtpLoginScreen({super.key});

  @override
  State<OtpLoginScreen> createState() => _OtpLoginScreenState();
}

class _OtpLoginScreenState extends State<OtpLoginScreen> {
  final _phoneController = TextEditingController(text: '+994 50 123 45 67');
  final _otpController = TextEditingController();
  final _api = CustomerApiService();
  bool _otpSent = false;
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _phoneController.dispose();
    _otpController.dispose();
    super.dispose();
  }

  Future<void> _sendOtp() async {
    final phone = _phoneController.text.trim();
    if (phone.length < 7) {
      setState(() => _error = 'Please enter a valid phone number.');
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final sent = await _api.sendOtp(phone);
      if (!mounted) return;
      if (!sent) {
        const message = 'Failed to send OTP code. Please try again.';
        setState(() {
          _loading = false;
          _error = message;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text(message)),
        );
        return;
      }
      setState(() {
        _loading = false;
        _otpSent = true;
      });
    } catch (e) {
      if (!mounted) return;
      final message = 'Failed to send OTP: ${e.toString().replaceFirst('Exception: ', '')}';
      setState(() {
        _loading = false;
        _error = message;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
    }
  }

  Future<void> _verifyOtp() async {
    final code = _otpController.text.trim();
    if (code.length < 4) {
      setState(() => _error = 'Please enter the OTP verification code.');
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final data = await _api.verifyOtp(_phoneController.text.trim(), code);
      final accessToken = data['access_token'] as String?;
      if (accessToken == null || accessToken.isEmpty) {
        throw Exception('Invalid authentication response. Please try again.');
      }
      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const HomeScreen()),
      );
    } catch (e) {
      if (!mounted) return;
      final message = e.toString().replaceFirst('Exception: ', '');
      setState(() {
        _loading = false;
        _error = message;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Center(
                child: Container(
                  width: 88,
                  height: 88,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(
                      color: const Color(0xFFF59E0B).withOpacity(0.5),
                      width: 1.5,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF38BDF8).withOpacity(0.28),
                        blurRadius: 24,
                      ),
                    ],
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(22),
                    child: Image.asset('assets/logo.png', fit: BoxFit.cover),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Randevu.vip',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
              ),
              const Text(
                'Sign in via WhatsApp / SMS OTP',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey),
              ),
              const SizedBox(height: 36),
              if (_error != null) ...[
                Text(_error!, style: const TextStyle(color: Colors.red), textAlign: TextAlign.center),
                const SizedBox(height: 12),
              ],
              TextField(
                controller: _phoneController,
                keyboardType: TextInputType.phone,
                decoration: const InputDecoration(
                  labelText: 'Phone Number',
                  hintText: '+994 50 123 45 67',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.phone),
                ),
              ),
              if (_otpSent) ...[
                const SizedBox(height: 16),
                TextField(
                  controller: _otpController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'OTP Code',
                    hintText: '123456',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.lock_clock),
                  ),
                ),
              ],
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _loading ? null : (_otpSent ? _verifyOtp : _sendOtp),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0EA5E9),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: _loading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : Text(
                        _otpSent ? 'Verify OTP' : 'Send Code via WhatsApp',
                        style: const TextStyle(fontSize: 16, color: Colors.white),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
