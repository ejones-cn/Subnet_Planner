import 'package:flutter/material.dart';

class AppProvider extends ChangeNotifier {
  // 当前选中的标签页
  int _currentTabIndex = 0;
  
  // 历史记录
  List<Map<String, dynamic>> _history = [];
  
  // 获取当前标签页
  int get currentTabIndex => _currentTabIndex;
  
  // 获取历史记录
  List<Map<String, dynamic>> get history => _history;
  
  // 切换标签页
  void switchTab(int index) {
    _currentTabIndex = index;
    notifyListeners();
  }
  
  // 添加历史记录
  void addHistory(Map<String, dynamic> record) {
    _history.insert(0, record);
    // 限制历史记录数量
    if (_history.length > 50) {
      _history.removeLast();
    }
    notifyListeners();
  }
  
  // 清空历史记录
  void clearHistory() {
    _history.clear();
    notifyListeners();
  }
  
  // 示例方法：执行子网切分
  Map<String, dynamic> splitSubnet(String parent, String split) {
    // 这里将调用核心算法
    // 现在返回模拟数据
    return {
      'success': true,
      'message': '子网切分成功',
      'parent_info': {
        'cidr': parent,
        'network': '10.0.0.0',
        'netmask': '255.0.0.0',
        'broadcast': '10.255.255.255',
        'num_addresses': 16777216
      },
      'split_info': {
        'cidr': split,
        'network': '10.1.0.0',
        'netmask': '255.255.0.0',
        'broadcast': '10.1.255.255',
        'num_addresses': 65536
      },
      'remaining_subnets_info': [
        {
          'cidr': '10.2.0.0/16',
          'network': '10.2.0.0',
          'netmask': '255.255.0.0',
          'broadcast': '10.2.255.255',
          'num_addresses': 65536
        },
        {
          'cidr': '10.3.0.0/16',
          'network': '10.3.0.0',
          'netmask': '255.255.0.0',
          'broadcast': '10.3.255.255',
          'num_addresses': 65536
        }
      ]
    };
  }
}