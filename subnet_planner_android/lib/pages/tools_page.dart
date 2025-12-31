import 'package:flutter/material.dart';

class ToolsPage extends StatelessWidget {
  const ToolsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '高级工具',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          
          GridView.count(
            shrinkWrap: true,
            crossAxisCount: 2,
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
            physics: const NeverScrollableScrollPhysics(),
            children: [
              _buildToolCard(
                icon: Icons.calculate,
                title: '子网计算',
                description: '计算子网掩码、广播地址等',
                onTap: () {
                  // TODO: Implement subnet calculation
                },
              ),
              _buildToolCard(
                icon: Icons.swap_horiz,
                title: '地址转换',
                description: 'IP地址与二进制/十六进制转换',
                onTap: () {
                  // TODO: Implement address conversion
                },
              ),
              _buildToolCard(
                icon: Icons.find_in_page,
                title: '地址查询',
                description: '查询IP地址所属区域',
                onTap: () {
                  // TODO: Implement address lookup
                },
              ),
              _buildToolCard(
                icon: Icons.shield,
                title: '子网验证',
                description: '验证子网划分是否正确',
                onTap: () {
                  // TODO: Implement subnet validation
                },
              ),
              _buildToolCard(
                icon: Icons.history,
                title: '历史记录',
                description: '查看历史操作记录',
                onTap: () {
                  // TODO: Implement history view
                },
              ),
              _buildToolCard(
                icon: Icons.settings,
                title: '设置',
                description: '应用设置和偏好',
                onTap: () {
                  // TODO: Implement settings
                },
              ),
            ],
          ),
          const SizedBox(height: 24),
          
          Card(
            elevation: 2,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('关于', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 8),
                  const Text(
                    '子网规划工具 v1.0.0\n'\n                    '一个功能强大的子网规划和计算工具，支持多种子网划分方式，\n'\n                    '帮助网络管理员快速进行子网规划和管理。',
                    style: TextStyle(fontSize: 14),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildToolCard({
    required IconData icon,
    required String title,
    required String description,
    required VoidCallback onTap,
  }) {
    return Card(
      elevation: 3,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 48, color: Colors.blue),
              const SizedBox(height: 12),
              Text(
                title,
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                description,
                style: const TextStyle(fontSize: 12, color: Colors.grey),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}