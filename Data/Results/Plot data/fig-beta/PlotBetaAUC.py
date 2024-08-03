import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle
import glob

# 设置 matplotlib 配置
config = {
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "font.size": 20,
    "axes.unicode_minus": False,
    "mathtext.fontset": "stix",
}
plt.rcParams.update(config)

# 加载参考数据以确定颜色映射
with open('./I_different_beta.pkl', 'rb') as fh:
    data = pickle.load(fh)

# 将简化率转换为浮点数并排序
sorted_keys = sorted(data.keys(), key=lambda x: float(x))
sorted_keys = [float(key) for key in sorted_keys]

# 创建渐变色 colormap
cmap = plt.get_cmap('viridis_r')
N = len(sorted_keys)+4
colors = [cmap(i / N) for i in range(N)][-len(sorted_keys):]

# 获取所有 Excel 文件
files = glob.glob('auc_value_beta=*.xlsx')

# 创建图表
fig, ax = plt.subplots(figsize=(12, 8))

# 常数
normalization_factor = 16236023

# 读取每个文件并绘制曲线
for i, file in enumerate(sorted(files)):
    # 读取 Excel 文件
    df = pd.read_excel(file)

    # 提取 beta 值
    beta_value = float(file.split('=')[-1].split('.xlsx')[0])

    # 计算 y 值
    y_values = df['delta_auc'] / normalization_factor

    # 找到 beta 值的索引以确定颜色
    index = sorted_keys.index(beta_value)

    # 绘制曲线
    ax.plot(df['simplify_ratio'], y_values, color=colors[index], marker='.', label=f'β={beta_value:.1f}')

# 设置对数 y 轴
ax.set_yscale('log')

# 设置标签和图例
ax.set_xlabel('Simplification Rate ρ', fontsize=24)
ax.set_ylabel(r'Simulation Error $\Delta \epsilon$', fontsize=24)
ax.legend(title='Transmissibility', loc='lower right', ncol=3, fontsize=16)
ax.grid(ls="-.", lw=0.3, color='gray')

ax.set_xlim(-0.001,1.001)

plt.tight_layout()
# plt.show()
plt.savefig('BetaAUC.png', dpi=600)
