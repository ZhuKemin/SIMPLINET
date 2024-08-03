import pickle
import matplotlib.pyplot as plt
import numpy as np

config = {
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "font.size": 22,
    "axes.unicode_minus": False,
    "mathtext.fontset": "stix",
}
plt.rcParams.update(config)

# 加载数据
with open('./I_different_beta.pkl', 'rb') as fh:
    data = pickle.load(fh)

# 将简化率转换为浮点数并排序
sorted_keys = sorted(data.keys(), key=lambda x: float(x))
sorted_keys = [float(key) for key in sorted_keys]

# 创建渐变色 colormap
cmap = plt.get_cmap('viridis_r')
N = len(sorted_keys)+4
colors = [cmap(i / N) for i in range(N)][-len(sorted_keys):]

# 创建主图，增加图的大小
fig, ax = plt.subplots(figsize=(10, 8))

for i, key in enumerate(sorted_keys):
    ax.plot(data[str(key)], color=colors[i], label=f'β={key:.1f}')

ax.set_xlim(0, 200)
ax.set_ylim(bottom=-1e3)
ax.set_xlabel('Simulation Days')
ax.set_ylabel('Incidence')
ax.legend(title='Transmissibility', bbox_to_anchor=(0.56, 0.2), fontsize=12, title_fontsize=15, ncol=3)
ax.yaxis.get_offset_text().set_fontsize(18)
ax.grid(ls="-.", lw=0.3, color='gray')


# 创建插图，整体左移一些
inset_ax = fig.add_axes([0.6, 0.55, 0.3, 0.3])

for i, key in enumerate(sorted_keys):
    inset_ax.plot(data[str(key)], color=colors[i])

inset_ax.set_xlim(200, 600)
inset_ax.set_ylim(bottom=-1e3)
inset_ax.set_xlabel('Simulation Days', fontsize=16)
inset_ax.set_ylabel('Incidence', fontsize=16)
inset_ax.tick_params(axis='both', which='major', labelsize=14)
inset_ax.yaxis.get_offset_text().set_fontsize(14)
inset_ax.grid(ls="-.", lw=0.1, color='gray')

plt.tight_layout()  # 调整布局，以确保文本和图例都能正确显示

# plt.show()
plt.savefig('Beta.png', dpi=600)
