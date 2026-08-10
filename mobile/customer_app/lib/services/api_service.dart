import 'dart:convert';
import 'package:http/http.dart' as http;

class CustomerApiService {
  static const String baseUrl = 'http://localhost:8000/api/v1';
  String? token;

  CustomerApiService({this.token});

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      };

  Future<bool> sendOtp(String phone) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/otp/send'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'phone': phone}),
    );
    return response.statusCode == 200;
  }

  Future<Map<String, dynamic>> verifyOtp(String phone, String code) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/otp/verify'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'phone': phone, 'code': code}),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('OTP verification failed');
  }

  Future<List<dynamic>> getMyAppointments() async {
    final response = await http.get(
      Uri.parse('$baseUrl/appointments/my'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return [];
  }
}
