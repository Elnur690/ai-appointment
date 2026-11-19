import 'dart:async';
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://api.randevu.vip/api/v1',
  );
  static const Duration _timeout = Duration(seconds: 15);
  static const _storage = FlutterSecureStorage();
  static const _tokenKey = 'randevu_business_jwt';

  String? token;

  ApiService({this.token});

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

  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http
        .post(
          Uri.parse('$baseUrl/auth/login'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'email': email.trim(), 'password': password}),
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
    if (response.statusCode == 401) {
      throw Exception('Invalid email or password');
    }
    throw Exception('Login failed (${response.statusCode})');
  }

  Future<void> forgotPassword(String email) async {
    final response = await http
        .post(
          Uri.parse('$baseUrl/auth/forgot-password'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'email': email.trim()}),
        )
        .timeout(_timeout);
    if (response.statusCode != 200) {
      throw Exception('Failed to send reset instructions');
    }
  }

  Future<Map<String, dynamic>?> getBusinessProfile() async {
    final headers = await _buildHeaders();
    final response = await http.get(Uri.parse('$baseUrl/businesses/'), headers: headers).timeout(_timeout);
    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    }
    return null;
  }

  Future<bool> updateBusinessProfile(Map<String, dynamic> payload) async {
    final headers = await _buildHeaders();
    final response = await http
        .put(
          Uri.parse('$baseUrl/businesses/'),
          headers: headers,
          body: jsonEncode(payload),
        )
        .timeout(_timeout);
    return response.statusCode == 200;
  }

  Future<Map<String, dynamic>?> getBusinessAnalytics() async {
    final headers = await _buildHeaders();
    final response = await http.get(Uri.parse('$baseUrl/businesses/analytics'), headers: headers).timeout(_timeout);
    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    }
    return null;
  }

  Future<Map<String, dynamic>?> getSubscription() async {
    final headers = await _buildHeaders();
    final response = await http.get(Uri.parse('$baseUrl/businesses/subscription'), headers: headers).timeout(_timeout);
    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    }
    return null;
  }

  Future<Map<String, dynamic>> createSubscriptionCheckout(String planId) async {
    final headers = await _buildHeaders();
    final response = await http
        .post(
          Uri.parse('$baseUrl/businesses/subscription/checkout'),
          headers: headers,
          body: jsonEncode({'plan_id': planId}),
        )
        .timeout(_timeout);
    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    }
    throw Exception('Checkout failed (${response.statusCode})');
  }

  Future<List<dynamic>> _getList(String path) async {
    final headers = await _buildHeaders();
    final response = await http.get(Uri.parse('$baseUrl$path'), headers: headers).timeout(_timeout);
    if (response.statusCode == 200) {
      final decoded = jsonDecode(response.body);
      if (decoded is List) return decoded;
    }
    if (response.statusCode == 401) {
      await logout();
    }
    return [];
  }

  Future<List<dynamic>> getAppointments() => _getList('/appointments/');
  Future<List<dynamic>> getServices() => _getList('/services/');
  Future<List<dynamic>> getStaff() => _getList('/staff/');
  Future<List<dynamic>> getBranches() => _getList('/branches/');
  Future<List<dynamic>> getCustomers() => _getList('/customers/');
  Future<List<dynamic>> getPayments() => _getList('/payments/');
  Future<List<dynamic>> getConversations() => _getList('/conversations/');

  Future<Map<String, dynamic>> getPaymentsSummary() async {
    final headers = await _buildHeaders();
    final response = await http.get(Uri.parse('$baseUrl/payments/summary'), headers: headers).timeout(_timeout);
    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    }
    return {'total_revenue': 0.0, 'count': 0};
  }

  Future<bool> createAppointment(Map<String, dynamic> payload) async {
    final headers = await _buildHeaders();
    final response = await http
        .post(Uri.parse('$baseUrl/appointments/'), headers: headers, body: jsonEncode(payload))
        .timeout(_timeout);
    return response.statusCode == 200 || response.statusCode == 201;
  }

  Future<bool> updateAppointmentStatus(String id, String status) async {
    final headers = await _buildHeaders();
    final response = await http
        .put(
          Uri.parse('$baseUrl/appointments/$id/status'),
          headers: headers,
          body: jsonEncode({'status': status}),
        )
        .timeout(_timeout);
    return response.statusCode == 200;
  }

  Future<bool> takeoverConversation(String conversationId) async {
    final headers = await _buildHeaders();
    final response = await http
        .post(Uri.parse('$baseUrl/conversations/$conversationId/takeover'), headers: headers)
        .timeout(_timeout);
    return response.statusCode == 200;
  }

  Future<bool> toggleStaffOvertime(String staffId, bool allowOvertime) async {
    final headers = await _buildHeaders();
    final response = await http
        .patch(
          Uri.parse('$baseUrl/staff/$staffId'),
          headers: headers,
          body: jsonEncode({'allow_overtime': allowOvertime}),
        )
        .timeout(_timeout);
    return response.statusCode == 200;
  }
}
