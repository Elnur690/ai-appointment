import 'package:flutter/material.dart';
import 'screens/splash_screen.dart';

void main() {
  runApp(const CustomerApp());
}

class CustomerApp extends StatelessWidget {
  const CustomerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Randevu.vip',
      debugShowCheckedModeBanner: false,
      locale: const Locale('az'),
      themeMode: ThemeMode.dark,
      darkTheme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF06080F),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF38BDF8),
          secondary: Color(0xFFF59E0B),
          surface: Color(0xFF0F1420),
        ),
      ),
      home: const CustomerSplashScreen(),
    );
  }
}
