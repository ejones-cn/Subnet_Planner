import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:subnet_planner_android/providers/app_provider.dart';

class SplitPage extends StatefulWidget {
  const SplitPage({super.key});

  @override
  State<SplitPage> createState() => _SplitPageState();
}

class _SplitPageState extends State<SplitPage> {
  final TextEditingController _parentController = TextEditingController(text: '10.0.0.0/8');
  final TextEditingController _splitController = TextEditingController(text: '10.1.0.0/16');
  Map<String, dynamic>? _splitResult;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '子网切分',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          
          // 输入区域
          Card(
            elevation: 2,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('父网段:', style: TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _parentController,
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                      hintText: '输入父网段，如 10.0.0.0/8',
                    ),
                    keyboardType: TextInputType.text,
                  ),
                  const SizedBox(height: 16),
                  const Text('切分网段:', style: TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _splitController,
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                      hintText: '输入要切分的网段，如 10.1.0.0/16',
                    ),
                    keyboardType: TextInputType.text,
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _executeSplit,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: const Text(
                        '执行切分',
                        style: TextStyle(fontSize: 16),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          
          // 结果区域
          if (_splitResult != null) ...[
            const Text(
              '切分结果',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            
            // 父网段信息
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('父网段信息:', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    _buildInfoRow('CIDR', _splitResult!['parent_info']['cidr']),
                    _buildInfoRow('网络地址', _splitResult!['parent_info']['network']),
                    _buildInfoRow('子网掩码', _splitResult!['parent_info']['netmask']),
                    _buildInfoRow('广播地址', _splitResult!['parent_info']['broadcast']),
                    _buildInfoRow('地址总数', _splitResult!['parent_info']['num_addresses'].toString()),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            
            // 切分网段信息
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('切分网段信息:', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    _buildInfoRow('CIDR', _splitResult!['split_info']['cidr']),
                    _buildInfoRow('网络地址', _splitResult!['split_info']['network']),
                    _buildInfoRow('子网掩码', _splitResult!['split_info']['netmask']),
                    _buildInfoRow('广播地址', _splitResult!['split_info']['broadcast']),
                    _buildInfoRow('地址总数', _splitResult!['split_info']['num_addresses'].toString()),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            
            // 剩余网段信息
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('剩余网段信息:', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    _buildRemainingNetworksTable(),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(width: 100, child: Text(label, style: const TextStyle(fontWeight: FontWeight.bold))),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  Widget _buildRemainingNetworksTable() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        columns: const [
          DataColumn(label: Text('序号')),
          DataColumn(label: Text('CIDR')),
          DataColumn(label: Text('网络地址')),
          DataColumn(label: Text('子网掩码')),
          DataColumn(label: Text('广播地址')),
          DataColumn(label: Text('地址总数')),
        ],
        rows: List.generate(
          _splitResult!['remaining_subnets_info'].length,
          (index) {
            final subnet = _splitResult!['remaining_subnets_info'][index];
            return DataRow(cells: [
              DataCell(Text((index + 1).toString())),
              DataCell(Text(subnet['cidr'])),
              DataCell(Text(subnet['network'])),
              DataCell(Text(subnet['netmask'])),
              DataCell(Text(subnet['broadcast'])),
              DataCell(Text(subnet['num_addresses'].toString())),
            ]);
          },
        ),
      ),
    );
  }

  void _executeSplit() {
    final appProvider = Provider.of<AppProvider>(context, listen: false);
    final result = appProvider.splitSubnet(_parentController.text, _splitController.text);
    
    setState(() {
      _splitResult = result;
    });
    
    // 添加到历史记录
    appProvider.addHistory({
      'action': '子网切分',
      'parent': _parentController.text,
      'split': _splitController.text,
      'timestamp': DateTime.now().toString(),
    });
  }
}