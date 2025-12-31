import 'package:flutter/material.dart';

class PlanPage extends StatelessWidget {
  const PlanPage({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '子网规划',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          
          Card(
            elevation: 2,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('子网规划功能正在开发中', style: TextStyle(fontSize: 18)),
                  const SizedBox(height: 16),
                  const Text('该功能将允许您：'),
                  const SizedBox(height: 8),
                  _buildFeatureItem('• 根据主机数量自动规划子网'),
                  _buildFeatureItem('• 生成子网分配表'),
                  _buildFeatureItem('• 可视化子网结构'),
                  _buildFeatureItem('• 导出子网规划报告'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          
          Card(
            elevation: 2,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('使用说明', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 8),
                  const Text(
                    '1. 输入网络地址和子网掩码\n'\n                    '2. 设置每个子网所需的主机数量\n'\n                    '3. 点击"自动规划"按钮\n'\n                    '4. 查看生成的子网规划结果',
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

  Widget _buildFeatureItem(String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Text(text),
    );
  }
}