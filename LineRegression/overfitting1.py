# -*- encoding: utf-8 -*-

# 为了解决过拟合问题：我们可以选择在损失函数中加入正则项（惩罚项），对于系数过大的惩罚
# 对于系数过多也有一定的惩罚能力，主要分为L1-norm 与 L2-norm
# LASSO 可以产生稀疏解，要用于特征选择（去掉冗余与无用的特征属性）


import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import warnings

from sklearn.linear_model import LinearRegression, LassoCV, RidgeCV, ElasticNetCV
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.exceptions import ConvergenceWarning

# 设置字符集，防止中文乱码
mpl.rcParams['font.sans-serif'] = [u'simHei']
mpl.rcParams['axes.unicode_minus'] = False
# 拦截异常
warnings.filterwarnings(action='ignore', category=ConvergenceWarning)
warnings.filterwarnings(action='ignore', category=FutureWarning)

# 创建模型数据
np.random.seed(100)
# 显示方式设置，每次的字符数用于插入换行符，是否使用科学计数法
np.set_printoptions(linewidth=1000, suppress=True)

N = 10
x = np.linspace(0, 6, N) + np.random.randn(N)
y = 1.8 * x ** 3 + x ** 2 - 14 * x - 7 + np.random.randn(N)
# 将其设置为矩阵
x.shape = -1, 1
y.shape = -1, 1

# EidgeCV和Ridge的区别是：前者可以进行交叉验证
models = [
    Pipeline([
        ('Poly', PolynomialFeatures(include_bias=False)),
        ('Linear', LinearRegression(fit_intercept=False))
    ]),
    Pipeline([
        ('Poly', PolynomialFeatures(include_bias=False)),
        # alpha 给定的是Ridge算法中，L2正则项的权重值，也就是ppt中的兰木达
        # alphas是给定CV交叉验证过程中，Ridge算法的alpha参数值得取值范围
        ('Linear', RidgeCV(alphas=np.logspace(-3, 2, 50), fit_intercept=False))
    ]),
    Pipeline([
        ('Poly', PolynomialFeatures(include_bias=False)),
        ('Linear', LassoCV(alphas=np.logspace(0, 1, 10), fit_intercept=False))
    ]),
    Pipeline([
        ('Poly', PolynomialFeatures(include_bias=False)),
        # l1_ratio: 给定EN算法中L1正则项在整个惩罚项中的比例，这里给定一个列表；
        # l1_ratio: 也就是ppt中的p，p的范围是[0, 1]
        # alphas也就是ppt中的兰木达
        # alphas表示的是在CV交叉验证的过程中，EN算法L!正则项的权重比例的可选值的范围
        ('Linear', ElasticNetCV(alphas=np.logspace(0, 1, 10), l1_ratio=[.1, .5, .7, .9, .95, 1], fit_intercept=False))
    ]),
]

# 线性模型过拟合图形识别
plt.figure(facecolor='w')
degree = np.arange(1, N, 4)  # 阶
dm = degree.size
colors = []  # 颜色
for c in np.linspace(16711680, 255, dm):
    colors.append('#%06x' % int(c))

model = models[0]
for i, d in enumerate(degree):
    plt.subplot(int(np.ceil(dm / 2.0)), 2, i + 1)
    plt.plot(x, y, 'ro', ms=10, zorder=N)

    # 设置阶数
    model.set_params(Poly__degree=d)
    # 模型训练
    model.fit(x, y.ravel())

    lin = model.get_params('Linear')['Linear']
    output = u'%d阶，系数为：' % (d)
    # 判断lin对象中是否有对应的属性
    if hasattr(lin, 'alpha_'):
        idx = output.find(u'系数')
        output = output[:idx] + (u'alpha=%.6f, ' % lin.alpha_) + output[idx:]
    if hasattr(lin, 'l1_ratio_'):
        idx = output.find(u'系数')
        output = output[:idx] + (u'l1_radio=%.6f, ' % lin.l1_radio_) + output[idx:]
    x_hat = np.linspace(x.min(), x.max(), num=100)  # 产生模拟数据
    x_hat.shape = -1, 1
    y_hat = model.predict(x_hat)
    s = model.score(x, y)

    z = N - 1 if (d == 2) else 0
    label = u'%d阶，正确率=%.3f' % (d, s)
    plt.plot(x_hat, y_hat, color=colors[i], lw=2, alpha=0.75, label=label, zorder=z)

    plt.legend(loc='upper left')
    plt.grid(True)
    plt.xlabel('X', fontsize=16)
    plt.xlabel('Y', fontsize=16)

plt.tight_layout(1, rect=(0, 0, 1, 0.95))
plt.suptitle(u'线性回归过拟合显示', fontsize=22)
plt.show()


# 线性回归，Lasso回归，Ridge回归，ElasticNet比较
plt.figure(facecolor='w')
degree = np.arange(1, N, 2)
dm = degree.size
colors = []  # 颜色
for c in np.linspace(16711680, 255, dm):
    colors.append('#%06x' % int(c))
titles = [u'线性回归', u'Ridge回归', u'Lasso回归', u'ElasticNet']

for t in range(4):
    model = models[t]  # 选择了模型--具体的pipeline(线性、Lasso、Ridge、EN)
    plt.subplot(2, 2, t + 1)  # 选择具体的子图
    plt.plot(x, y, 'ro', ms=10, zorder=N)  # 在子图中画原始数据点； zorder：图像显示在第N个位置

    # 遍历不同的多项式的阶，看不同阶的情况下，模型的效果
    for i, d in enumerate(degree):
        # 设置阶数（多项式）
        model.set_params(Poly__degree=d)
        # 模型训练
        model.fit(x, y.ravel())

        # 获取得到具体的算法模型
        # model.get_params()方法返回的其实是一个dict对象，后面的Linear其实是dict对象的key
        # 也是我们在定义Pipeline的时候给定的一个名称值
        lin = model.get_params()['Linear']
        # 打印数据
        output = u'%s:%d阶，系数为：' % (titles[t], d)
        # 判断lin对象中是否有对应的属性
        if hasattr(lin, 'alpha_'):  # 判断lin这个模型中是否有alpha这个属性
            idx = output.find(u'系数')
            output = output[:idx] + (u'alpha=%.6f, ' % lin.alpha_) + output[idx:]
        if hasattr(lin, 'l1_radio'):  # 判断lin这个模型中是否有l1_radio这个属性
            idx = output.find(u'系数')
            output = output[:idx] + (u'l1_radio=%.6f, ' % lin.l1_radio) + output[idx:]
        # line.coef_: 获取线性模型的参数列表，也就是我们ppt中的theta值，ravel()将结果转换为行列式
        print(output, lin.coef_.ravel())

        # 产生模拟数据
        x_hat = np.linspace(x.min(), x.max(), num=100)
        x_hat.shape = -1, 1
        # 数据预测
        y_hat = model.predict(x_hat)
        # 计算准确率
        s = model.score(x, y)

        # 当d等于5的时候，设置为N-1层，其他设置为0层；将d=5得这条线凸显出来
        z = N + 1 if d == 5 else 0
        label = u'%d阶，正确率%.3f' % (d, s)
        plt.plot(x_hat, y_hat, color=colors[i], lw=2, alpha=0.75, label=label, zorder=z)

    plt.legend(loc='upper left')
    plt.grid(True)
    plt.title(titles[t])
    plt.xlabel('X', fontsize=16)
    plt.ylabel('Y', fontsize=16)

plt.tight_layout(1, rect=(0, 0, 1, 0.95))
plt.suptitle(u'各种不同线性回归过拟合显示', fontsize=22)
plt.show()
