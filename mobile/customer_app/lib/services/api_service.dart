import 'dart:async';
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

class CustomerApiService {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://api.randevu.vip/api/v1',
  );
  static const Duration _timeout = Duration(seconds: 15);
  static const _storage = FlutterSecureStorage();
  static const _tokenKey = 'randevu_customer_jwt';

  String? token;

  CustomerApiService({this.token});

  Future<String?> getStoredToken() async {
    token ??= await _storage.read(key: _tokenKey);
    return token;
  }

  Future<void> saveToken(String newToken) async {
    token = newToken;
    await _storage.write(key: _tokenKey, value: newToken);
  }

  Future<void> logout() async {
    token = null;
    await _storage.delete(key: _tokenKey);
  }

  Future<Map<String, String>> _buildHeaders() async {
    final jwt = await getStoredToken();
    return {
      'Content-Type': 'application/json',
      if (jwt != null && jwt.isNotEmpty) 'Authorization': 'Bearer $jwt',
    };
  }

  Future<bool> sendOtp(String phone) async {
    final response = await http
        .post(
          Uri.parse('$baseUrl/auth/otp/send'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'phone': phone.trim()}),
        )
        .timeout(_timeout);
    return response.statusCode == 200;
  }

  Future<Map<String, dynamic>> verifyOtp(String phone, String code) async {
    final response = await http
        .post(
          Uri.parse('$baseUrl/auth/otp/verify'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'phone': phone.trim(), 'code': code.trim()}),
        )
        .timeout(_timeout);
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      final accessToken = data['access_token'] as String?;
      if (accessToken != null && accessToken.isNotEmpty) {
        await saveToken(accessToken);
      }
      return data;
    }
    throw Exception('OTP verification failed (${response.statusCode})');
  }

  Future<List<dynamic>> getMyAppointments() async {
    final headers = await _buildHeaders();
    final response = await http
        .get(Uri.parse('$baseUrl/appointments/my'), headers: headers)
        .timeout(_timeout);
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    if (response.statusCode == 401) {
      await logout();
    }
    return [];
  }
}
