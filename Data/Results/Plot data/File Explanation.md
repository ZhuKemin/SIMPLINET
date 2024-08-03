fig1: 社区简化结果，以及各社区delta_auc，同上次一样
    comm_delta_auc：各社区的delta_auc，一维（社区数，）
    comm_ID：社区编号，一维（2236，），-1表示无人流的网格，也就是csv文件comm_ID那一列
    OD：人口流动矩阵，二维（社区数*社区数）
    POP：社区总人数，一维（社区数，）
    csv文件：新加了一列comm_ID，-1表示无人流地区以及无人口流入流出地区

fig2: 整体传播曲线随简化率变化
    draw_I: 字典数据，通过draw_I['0.00']读取简化率为0.00的0-200天每日感染者数量。用于绘制子图1、2
    simplify_ratio, delta_auc: 一维numpy数组，表示简化率和delta_auc，用于绘制子图3

fig4: 各社区的dalta_auc
    data.pkl: list数据，每个子list的为一个简化率下各社区dalta_auc
    positions：list数据，每个元素表示一个简化率，也即对应箱型图的位置
    这样就可以绘图：plt.boxplot(data, positions=positions, widths=0.008)

fig5: 敏感性分析 色带表示beta
    I_different_beta: 字典数据，通过I_different_beta['0.1']读取beta=0.1时的0-800天每日感染者数量。

fig7：不同方法的delta_auc
    scXXXX_simplify_ratio, scXXXX_delta_auc: 一维numpy数组，表示不同方法的简化率和delta_auc