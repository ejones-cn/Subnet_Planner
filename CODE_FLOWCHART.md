# 子网规划师 - 代码流程图

## 1. 应用程序启动流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant M as Main (main.py)
    participant W as IPSubnetSplitterApp
    participant S as Style (ttk.Style)
    participant T as TopLevelNotebook
    
    Note over M,W: === 应用程序启动 ===
    U->>M: 双击运行程序
    M->>M: 创建tk.Tk根窗口
    M->>M: 设置窗口标题和大小
    M->>W: 创建IPSubnetSplitterApp实例
    W->>W: __init__初始化
    W->>W: 加载版本信息
    W->>W: 配置CIDR验证正则
    W->>S: 配置ttk样式
    W->>W: 创建主框架
    W->>T: 创建顶级标签页
    T->>T: 添加"子网切分"标签
    T->>T: 添加"子网规划"标签
    W->>W: 初始化子网切分模块
    W->>W: 初始化子网规划模块
    M->>M: root.mainloop()
    
    Note over M,W: === 窗口事件循环开始 ===
```

## 2. 子网切分核心流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant UI as 界面层
    participant V as 验证模块
    participant E as execute_split
    participant C as ip_subnet_calculator
    participant R as 结果显示
    
    Note over UI,R: === 子网切分主流程 ===
    U->>UI: 输入父网段和切分网段
    UI->>V: validate_cidr()
    alt 格式验证失败
        V-->>UI: 返回False，显示红色
        UI-->>U: 提示格式错误
    else 格式验证通过
        V-->>UI: 返回True，显示黑色
        UI->>UI: 启用执行按钮
        U->>UI: 点击"执行切分"
        UI->>E: execute_split()
        
        E->>E: 获取输入值
        E->>C: split_subnet(parent_cidr, split_cidr)
        
        C->>C: 验证切分网段合法性
        alt 验证失败
            C-->>E: 返回错误信息
            E->>UI: show_error()
            UI-->>U: 显示错误提示
        else 验证成功
            C->>C: 计算剩余网段
            C->>C: 生成网段信息
            C-->>E: 返回完整结果
            E->>E: 解析返回结果
            E->>UI: 更新切分信息表格
            E->>UI: 更新剩余网段表格
            E->>UI: 绘制网段分布图
            UI-->>U: 显示切分结果
        end
    end
```

## 3. PDF导出流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant UI as 导出按钮
    participant E as export_result
    participant D as 对话框
    participant P as PDF生成器
    participant F as 文件系统
    
    Note over UI,F: === PDF导出流程 ===
    U->>UI: 点击"导出结果"
    UI->>E: export_result()
    E->>D: filedialog.asksaveasfilename()
    alt 用户取消保存
        D-->>E: 返回空
        E-->>UI: 取消操作
    else 用户选择文件路径
        D-->>E: 返回文件路径
        E->>E: 确定导出格式
        alt 导出PDF
            E->>P: generate_pdf()
            P->>P: 创建A4文档
            P->>P: 添加标题信息
            P->>P: 绘制网段分布图
            P->>P: 绘制柱状图
            P->>P: 绘制图例说明
            P-->>E: 返回PDF文件
        else 导出Excel
            E->>E: generate_excel()
            E->>F: 保存Excel文件
        end
        E->>F: 保存文件
        E->>UI: show_info()
        UI-->>U: 显示导出成功
    end
```

## 4. 网段分布图绘制流程

```mermaid
sequenceDiagram
    participant E as execute_split
    participant G as 图表生成器
    participant C as Canvas
    participant I as Image (PIL)
    participant F as Font
    
    Note over E,F: === 图表绘制流程 ===
    E->>G: draw_distribution_chart()
    G->>G: 获取切分数据
    G->>G: 计算图表尺寸
    G->>G: 确定画布高度
    
    rect rgb(40, 40, 40)
    Note over G,F: === 图像生成阶段 ===
    G->>I: 创建Image对象
    I->>F: 加载字体
    F-->>I: 返回字体对象
    I->>I: 绘制背景
    I->>I: 绘制标题
    I->>I: 绘制网格线
    I->>I: 绘制柱状图
    I->>I: 绘制数值标签
    I->>I: 绘制图例说明
    end
    
    G->>I: 转换为PhotoImage
    I-->>G: 返回图像对象
    G->>C: create_image()
    C->>C: 在Canvas上显示
    G->>C: 绑定滚动事件
    C-->>E: 完成绘制
```

## 5. 子网规划流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant P as PlanningUI
    participant T as 需求表格
    participant A as suggest_subnet_planning
    participant C as ip_subnet_calculator
    participant R as 规划结果
    
    Note over P,R: === 子网规划流程 ===
    U->>P: 添加子网需求
    P->>T: 添加行
    U->>T: 输入名称和主机数
    U->>P: 点击"智能规划"
    P->>P: 收集所有需求
    P->>A: suggest_subnet_planning(parent_cidr, requirements)
    
    A->>C: 排序需求
    C->>C: 计算所需子网大小
    
    loop 每个子网需求
        C->>C最优CID: 寻找R
        C->>C: 分配子网
        C->>C: 更新剩余空间
    end
    
    C-->>A: 返回规划结果
    A-->>P: 显示已分配子网
    A-->>P: 显示剩余网段
    P-->>U: 展示规划方案
```

## 6. 核心类关系图

```mermaid
classDiagram
    class tkinter {
        +mainloop()
        +title()
        +geometry()
    }
    
    class IPSubnetSplitterApp {
        -root: tk.Tk
        -cidr_pattern: str
        -split_parent_networks: list
        -split_networks: list
        +__init__()
        +validate_cidr()
        +execute_split()
        +export_result()
        +draw_distribution_chart()
        +setup_planning_page()
    }
    
    class ColoredNotebook {
        -unique_id: int
        -tabs: list
        -active_tab: int
        +add_tab()
        +select_tab()
        +on_configure()
    }
    
    class ip_subnet_calculator {
        +split_subnet()
        +ip_to_int()
        +get_subnet_info()
        +suggest_subnet_planning()
    }
    
    class PDFGenerator {
        +generate_pdf()
        +create_chart_image()
        +draw_legend()
    }
    
    tkinter <|-- IPSubnetSplitterApp
    IPSubnetSplitterApp "1" *-- "1" ColoredNotebook : 包含
    IPSubnetSplitterApp "1" *-- "1" ip_subnet_calculator : 调用
    IPSubnetSplitterApp "1" *-- "1" PDFGenerator : 调用
```

## 7. 数据流向图

```mermaid
flowchart TB
    subgraph 用户输入
        A[父网段: 10.0.0.0/8] --> B[切分网段: 10.21.60.0/23]
    end
    
    subgraph 验证层
        B --> C{CIDR格式验证}
        C -->|通过| D[执行切分]
        C -->|失败| E[显示错误提示]
    end
    
    subgraph 业务逻辑层
        D --> F[split_subnet]
        F --> G[IPAddress计算]
        G --> H[address_exclude]
        H --> I[剩余网段列表]
    end
    
    subgraph 数据处理层
        I --> J[get_subnet_info]
        J --> K[网络地址]
        J --> L[子网掩码]
        J --> M[广播地址]
        J --> N[可用主机数]
    end
    
    subgraph 展示层
        K --> O[切分信息表格]
        L --> O
        M --> O
        N --> O
        I --> P[剩余网段表格]
        I --> Q[网段分布图]
    end
    
    subgraph 导出层
        O --> R[PDF/Excel导出]
        P --> R
        Q --> R
        R --> S[用户文件]
    end
```

## 8. 状态转换图

```mermaid
stateDiagram-v2
    [*] --> 初始状态: 程序启动
    
    初始状态 --> 等待输入: 显示主界面
    
    等待输入 --> 验证中: 用户输入CIDR
    
    验证中 --> 等待输入: 格式错误
    验证中 --> 准备执行: 格式正确
    
    准备执行 --> 执行切分: 点击执行按钮
    
    执行切分 --> 切分成功: 切分网段有效
    执行切分 --> 切分失败: 切分网段无效
    
    切分失败 --> 等待输入: 显示错误
    
    切分成功 --> 显示结果: 更新UI
    
    显示结果 --> 等待输入: 用户修改输入
    
    显示结果 --> 导出结果: 点击导出按钮
    
    导出结果 --> 显示结果: 导出完成
    
    state 显示结果 {
        [*] --> 切分网段信息
        切分网段信息 --> 剩余网段表
        剩余网段表 --> 网段分布图
        网段分布图 --> 切分网段信息
    }
```

## 9. 错误处理流程

```mermaid
flowchart TD
    A[开始执行切分] --> B{父网段格式正确?}
    B -->|否| C[返回错误: 父网段格式无效]
    B -->|是| D{切分网段格式正确?}
    
    D -->|否| E[返回错误: 切分网段格式无效]
    D -->|是| F{切分网段是父网段子网?}
    
    F -->|否| G[返回错误: 切分网段不是父网段的子网]
    F -->|是| H{两个网段相同?}
    
    H -->|是| I[返回空剩余列表]
    H -->|否| J[执行address_exclude]
    
    J --> K[生成剩余网段列表]
    K --> L[格式化输出]
    
    C --> M[显示错误对话框]
    E --> M
    G --> M
    
    L --> N[显示切分结果]
    M --> O[等待用户修正]
    O --> A
    
    N --> P[导出PDF]
```

## 10. 文件模块依赖关系

```mermaid
flowchart TB
    subgraph 程序入口
        main[main.py - 程序入口点]
    end
    
    subgraph 核心模块
        app[windows_app.py - GUI应用]
        web[web_app.py - Web应用]
    end
    
    subgraph 业务逻辑
        calc[ip_subnet_calculator.py<br/>子网计算核心算法]
        plan[子网规划算法]
    end
    
    subgraph 工具模块
        pdf[PDF生成器]
        excel[Excel导出器]
        pack[simple_pack.py - 打包工具]
        version[version.py - 版本管理]
    end
    
    subgraph 依赖库
        tk[tkinter - GUI框架]
        reportlab[reportlab - PDF生成]
        pillow[PIL - 图像处理]
        openpyxl[openpyxl - Excel处理]
    end
    
    main --> app
    main --> web
    app --> calc
    app --> pdf
    app --> excel
    app --> tk
    app --> reportlab
    app --> pillow
    app --> openpyxl
    calc --> plan
    web --> calc
    pack --> app
    version --> app
```

这个流程图完整展示了子网规划师的：
- 程序启动流程
- 核心业务逻辑（子网切分、子网规划）
- 用户交互流程
- 数据处理和展示流程
- 错误处理机制
- 模块依赖关系

所有流程图都遵循标准符号规范，使用Mermaid语法编写，可以直接在支持Mermaid的文档工具中渲染显示。
