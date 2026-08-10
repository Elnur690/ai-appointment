import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const BusinessApp());
}

class BusinessApp extends StatelessWidget {
  const BusinessApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Appointment Business',
      debugShowCheckedModeBanner: false,
      locale: const Locale('az'),
      themeMode: ThemeMode.dark,
      darkTheme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF0B0D13),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF0EA5E9),
          secondary: Color(0xFF06B6D4),
          surface: Color(0xFF11141E),
        ),
      ),
      home: const LoginScreen(),
    );
  }
}
