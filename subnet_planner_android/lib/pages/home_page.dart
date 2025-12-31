
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:subnet_planner_android/pages/split_page.dart';
import 'package:subnet_planner_android/pages/plan_page.dart';
import 'package:subnet_planner_android/pages/tools_page.dart';
import 'package:subnet_planner_android/providers/app_provider.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('子网规划工具'),
        centerTitle: true,
      ),
      body: Consumer<AppProvider>(
        builder: (context, provider, child) {
          return IndexedStack(
            index: provider.currentTabIndex,
            children: const [
              SplitPage(),
              PlanPage(),
              ToolsPage(),
            ],
          );
        },
      ),
      bottomNavigationBar: Consumer<AppProvider>(
        builder: (context, provider, child) {
          return BottomNavigationBar(
            currentIndex: provider.currentTabIndex,
            onTap: provider.switchTab,
            items: const [
              BottomNavigationBarItem(
                icon: Icon(Icons.split),
                label: '子网切分',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.event_note),
                label: '子网规划',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.build),
                label: '高级工具',
              ),
            ],
          );
        },
      ),
    );
  }
}