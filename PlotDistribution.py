import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, FixedLocator, LogFormatter
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import os
from datetime import datetime

# 设置字体和显示配置
config = {
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "font.size": 26,
    "axes.unicode_minus": False,
    "mathtext.fontset": "stix",
}
plt.rcParams.update(config)

class FlowDistributionVisualizer:
    def __init__(self, flow_history_path):
        # 从文件中加载每一步的流量矩阵
        self.flow_history = np.load(flow_history_path, allow_pickle=True)
        self.n_steps = len(self.flow_history)-1

    def plot_flow_distribution(self, simplification_rates, output_dir='./Output/Figure/FlowDistribution2'):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for rate in simplification_rates:
            step_index = int(rate * 1818)

            data = self.flow_history[step_index].copy()
            data = data.astype('int64')
            data = data[data > 0]

            print (data)

            # 设置每个数量级有两个条的 bin
            xmax = np.log10(max(data))
            subdivisions = np.arange(0, xmax + 0.5, 0.5)
            bins = np.power(10, subdivisions)

            counts, _ = np.histogram(data, bins=bins)
            percentages = (counts / sum(counts)) * 100

            # 绘制PDF直方图
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.subplots_adjust(left=0.12, right=0.96, top=0.90, bottom=0.10)

            ax.bar(subdivisions[:-1], percentages, width=0.5, align='edge', color='cornflowerblue', edgecolor='gray', lw=1.2, zorder=11)

            # 设置主图的x轴刻度和网格线
            full_orders = np.arange(0, 6.1)
            ax.set_xticks(full_orders)
            ax.set_xticklabels([f'$10^{{{int(x)}}}$' for x in full_orders])
            ax.set_xlabel('Flow Volume')
            ax.set_ylabel('Frequency (%)')
            ax.set_xlim(0, 6)
            ax.set_ylim(0, 50)

            # 使用 LogLocator 设置次要刻度和网格线
            ax.xaxis.set_minor_locator(FixedLocator(np.arange(0, 6, 0.5)))
            ax.xaxis.set_minor_formatter(plt.NullFormatter())

            ax.grid(True, which='major', ls='-.', lw=0.5, color='gray',     zorder=10)
            ax.grid(True, which='minor', ls='-',  lw=0.3, color='lightgray', zorder=9)


            # 启用上侧和右侧的刻度
            plt.gca().xaxis.set_ticks_position('top')
            plt.gca().yaxis.set_ticks_position('left')

            ax.tick_params(axis='x', which='major', pad=2)
            ax.tick_params(axis='x', which='both', direction='in')

            # 设置主图的y轴刻度
            ax.set_yticks(np.arange(0, 51, 10)[:-1])

            # 绘制CDF曲线
            sorted_data = np.sort(data)
            percentage = np.arange(len(data)) / len(data) * 100

            ax_inset = inset_axes(ax, 
                                  width="50%",
                                  height="50%",
                                  loc='upper right',
                                  bbox_to_anchor=(-0.05, -0.1, 1, 1),
                                  bbox_transform=ax.transAxes)

            ax_inset.scatter(sorted_data, percentage, color='orangered', marker='.', s=1, zorder=12)

            ax_inset.set_xscale('log')
            ax_inset.set_xlim(1, 10**xmax)
            ax_inset.set_ylim(0, 101)
            ax_inset.grid(True, which='major', ls='-.', lw=0.25, color='gray',     zorder=10)
            ax_inset.grid(True, which='minor', ls='-',  lw=0.15, color='lightgray', zorder=9)

            # 设置子图的x轴和y轴刻度
            ax_inset.set_xticks([1, 10**2, 10**4, 10**6])
            ax_inset.set_xticklabels([f'$10^{{{int(x)}}}$' for x in [0, 2, 4, 6]])
            ax_inset.set_yticks([0, 20, 40, 60, 80, 100])
            ax_inset.set_yticklabels([str(int(y)) for y in [0, 20, 40, 60, 80]]+[''])
            ax_inset.xaxis.set_tick_params(labelsize=18)
            ax_inset.yaxis.set_tick_params(labelsize=20)

            # 设置子图的次要网格线
            ax_inset.xaxis.set_minor_locator(FixedLocator([10**f for f in np.arange(0, 6, 0.5)]))
            ax_inset.xaxis.set_minor_formatter(plt.NullFormatter())

            # 启用上侧和右侧的刻度
            plt.gca().xaxis.set_ticks_position('top')
            plt.gca().yaxis.set_ticks_position('left')

            # 使用 tick_params() 设置刻度线方向朝内
            ax_inset.tick_params(axis='both', which='both', direction='in')

            # 设置 y 轴的标签间距更近
            ax_inset.tick_params(axis='x', which='major', pad=2)

            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"flow_distribution_{rate*100:.1f}_{timestamp}.png"
            filepath = os.path.join(output_dir, filename)

            plt.show()
            exit()


            # 保存图像
            plt.savefig(filepath, dpi=600)
            plt.close(fig)
            print(f"Saved figure to {filepath}")

if __name__ == '__main__':
    flow_history_path = "./Output/flow_history.npy"

    visualizer = FlowDistributionVisualizer(flow_history_path)
    visualizer.plot_flow_distribution(simplification_rates=[0.2, 0.4, 0.6, 0.8, 0.9])

