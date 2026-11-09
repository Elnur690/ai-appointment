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

  Future<List<dynamic>> getAppointments() async {
    final headers = await _buildHeaders();
    final response = await http
        .get(Uri.parse('$baseUrl/appointments'), headers: headers)
        .timeout(_timeout);
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    if (response.statusCode == 401) {
      await logout();
    }
    return [];
  }

  Future<List<dynamic>> getConversations() async {
    final headers = await _buildHeaders();
    final response = await http
        .get(Uri.parse('$baseUrl/conversations'), headers: headers)
        .timeout(_timeout);
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    if (response.statusCode == 401) {
      await logout();
    }
    return [];
  }

  Future<bool> takeoverConversation(String conversationId) async {
    final headers = await _buildHeaders();
    final response = await http
        .post(
          Uri.parse('$baseUrl/conversations/$conversationId/takeover'),
          headers: headers,
        )
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
