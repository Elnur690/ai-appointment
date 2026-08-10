import 'package:flutter/material.dart';
import 'screens/otp_login_screen.dart';

void main() {
  runApp(const CustomerApp());
}

class CustomerApp extends StatelessWidget {
  const CustomerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Book Appointment',
      debugShowCheckedModeBanner: false,
      locale: const Locale('az'),
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF0EA5E9)),
      ),
      home: const OtpLoginScreen(),
    );
  }
}
