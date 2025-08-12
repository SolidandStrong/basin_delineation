# -*- coding: utf-8 -*-
"""
@Time ： 2024/10/12 16:05
@Auth ： Solid
@File ：Draw.py
@IDE ：PyCharm
"""
import math
import os

import matplotlib.pyplot as plt
import numpy as np
import csv
import os
from matplotlib.ticker import ScalarFormatter,FuncFormatter
def color(r,g,b):
    return (r/255,g/255,b/255)

def log(list):
    return [math.log10(o) for o in list]

def drawFig1(globalAreaFile):
    """
    绘制各个州的湖泊数量和NWEI的阈值变化图
    :param globalAreaFile:
    :return:
    """
    # 先读取NWEI的统计数据，获得NWEI各个州的各个层级的平均面积
    NWEI = {}
    with open(r'F:\全球数据集\论文\GNWL\制图\DATA\dataUse\NWEI_Avg_area.csv','r') as f:
        reader = csv.reader(f)
        for info in reader:
            nowTitle = info[0].split('.')
            if nowTitle[-1] == 'gdb':
                nowContinent = nowTitle[0].split('_')[-1]
                continue
            NWEI.setdefault(nowContinent,{}).setdefault(info[0],info[3])
        f.close()
    print(NWEI)
    # 读取GNWL的统计数据
    continentInfos = {}
    with open(globalAreaFile,'r') as f:
        reader = csv.reader(f)

        for info in reader:
            nowTitle = info[0].split('.')
            if nowTitle[-1] == 'gdb':
                nowContinent = nowTitle[0]
                continue
            continentInfos.setdefault(nowContinent,[]).append(info)
        f.close()

    # print(continentInfos)
    colors = [color(242,121,112),color(187,151,39),color(84,179,69),color(50,184,151),color(5,185,226),color(137,131,191),color(199,109,162),color(147,75,67),color(177,206,70)]
    fig, axs = plt.subplots(3, 3, figsize=(20,10))
    for i in range(3):
        for j in range(3):

            infos = continentInfos.popitem()
            print(len(continentInfos),infos)
            lakeArea = []
            lakeNum = []
            levelName = []
            lake_avg_area = []

            lakeArea_label = []
            lakeNum_label = []
            for info in infos[1]:
                levelName.append('L' + info[0].split('_')[1])
                # lakeArea_label.append(str(math.ceil(float(info[5]))))
                # lakeNum_label.append(str(math.ceil(float(info[7]))))
                lakeArea.append(float(NWEI[infos[0]][info[0]])/10)#lakeArea.append(float(info[5]))  float(NWEI[infos[0]][info[0]])
                lakeNum.append(float(info[7]))
                lake_avg_area.append(float(info[5]))
            lakeArea[-1] = 0.1
            lakeArea[-2] = 1
            lakeArea[-3] = 2
            lakeArea[-4] = 3
            # lakeArea = log(lakeArea)
            # lakeNum = log(lakeNum)
            lake_avg_area = log(lake_avg_area)


            def log_tick_formatter(val, _):
                if val <= 0:
                    return ""  # 对数轴不能为0或负数
                exponent = np.log10(val)
                if np.isclose(exponent, round(exponent)):
                    return r"$10^{{{:.0f}}}$".format(exponent)  # 显示为 10^x
                else:
                    return f"{val:.3g}"  # 否则正常三位有效数字

            title = infos[0]
            ax1=axs[i,j]
            # 绘制第一个 y 轴的数据
            # ax1.plot(range(len(lakeNum)),lakeArea,color ='blue', linewidth = 1)  #
            ax1.set_yscale("log")
            ax1.bar(range(len(lakeNum)),lakeArea,color =colors[4],edgecolor = 'black')
            # ax1.bar(range(len(lakeNum)), lakeArea, color=colors[j + i * 3], edgecolor='black')
            # ax1.scatter(range(len(lakeNum)), lakeNum)  #
            # ax1.set_xlabel('Level')  # X轴标签
            # ax1.set_ylabel('Average lake area')  # Y轴标签
            ax1.set_title(title)
            ax1.set_xticks(range(len(lakeNum)),levelName)
            # ax1.fill_between(range(len(lakeNum)),lakeArea, color=color(190,184,220), alpha=0.6)  # tian
            # ax1.tick_params(axis='y', labelcolor=colors[j + i * 3])  # 设置Y轴标签颜色
            ax1.tick_params(axis='y', labelcolor=colors[4])  # 设置Y轴标签颜色

            # ax1.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            ax1.yaxis.set_major_formatter(FuncFormatter(log_tick_formatter))
            # ax1.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))  # 使用科学计数法

            # ax1.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            # ax1.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))  # 使用科学计数法

            # 绘制第二个
            ax2 = ax1.twinx()
            ax2.set_yscale("log")
            ax2.plot(range(len(lakeNum)), lakeNum,color= 'black', linewidth = 1)  #
            ax2.scatter(range(len(lakeNum)), lakeNum, color='black', linewidth=1)  #
            # ax2.fill_between(range(len(lakeNum)), lakeNum,color=color(250,127,111), alpha=0.6)  # 绿色线
            ax2.tick_params(axis='y', labelcolor='black')  # 设置Y轴标签颜色
            ax2.yaxis.set_major_formatter(FuncFormatter(log_tick_formatter))
            # ax2.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            # ax2.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))  # 使用科学计数法

    plt.subplots_adjust(wspace=0.3, hspace=0.3)  # 增加子图之间的水平和垂直间距
    # plt.savefig(r'F:\全球数据集\论文\GNWL\制图\中间图\LakeArea_num.svg')
    plt.show()


def drawFig2(GNWLAreaVenu,topoAreaFile,outVenu):

    """
    绘各个州的GNWL与TopoCat的面积比较图
    :param GNWLAreaVenu:
    :param topoAreaFile:
    :param outVenu:
    :return:
    """

    '''
    # 预处理数据，运行一次即可
    topoCAtArea = {}
    with open(topoAreaFile,'r') as f:
        reader = csv.reader(f)
        for info in reader:
            topoCAtArea.setdefault(info[0],info[1])
    print('TopoCat Area is red successfully')
    continentAreaNames = os.listdir(GNWLAreaVenu)
    for continentAreaName in continentAreaNames:
        if continentAreaName.split('.')[-1] != 'csv':
            continue
        print(continentAreaName)
        path = os.path.join(GNWLAreaVenu,continentAreaName)
        infos = [['Hylak_id','GNWLArea\km2','TopoCatArea\km2']]
        with open(path,'r') as f:
            reader = csv.reader(f)
            for info in reader:
                infos.append([info[0],info[1],topoCAtArea[info[0]]])
            f.close()
        outpath = os.path.join(outVenu,continentAreaName)
        with open(outpath,'w',newline="") as f:
            writer = csv.writer(f)
            writer.writerows(infos)
            f.close()
    
    '''

    fileNames = os.listdir(outVenu)
    fig,ax = plt.subplots(3,3,figsize=(20,10))
    loc = 0
    for filename in fileNames:
        print(filename)
        path = os.path.join(outVenu,filename)
        n = 0
        GNWL = []
        TopoCat = []
        with open(path,'r') as f:
            reader = csv.reader(f)
            for info in reader:
                if n<1:
                    n += 1
                    continue
                GNWL.append(float(info[1]))
                TopoCat.append(float(info[2]))
            f.close()

        ax1 = ax[int((loc-loc%3)/3),int(loc%3)]
        loc += 1
        # absErr = np.abs(np.array(TopoCat)-np.array(GNWL))
        # relErr = absErr/np.array(TopoCat)
        sita005 = [[],[]]
        sita00501 = [[],[]]
        sita0102 = [[],[]]
        sita02 = [[],[]]
        for i in range(len(TopoCat)):
            relErr = abs(TopoCat[i]-GNWL[i])/TopoCat[i]
            if relErr < 0.05:
                sita005[0].append(TopoCat[i])
                sita005[1].append(GNWL[i])
            elif relErr < 0.1:
                sita00501[0].append(TopoCat[i])
                sita00501[1].append(GNWL[i])
            elif relErr < 0.2:
                sita0102[0].append(TopoCat[i])
                sita0102[1].append(GNWL[i])
            else:
                sita02[0].append(TopoCat[i])
                sita02[1].append(GNWL[i])
        print(len(sita005[0])/len(TopoCat))
        ax1.set_title(filename.split('_')[0])
        ax1.plot([min(TopoCat),max(TopoCat)],[min(TopoCat),max(TopoCat)],color = 'black',linewidth = 0.5)
        ax1.scatter(sita02[1],sita02[0], s=12,color = color(40,120,181))
        ax1.scatter(sita0102[1], sita0102[0], s=12,color = color(248,172,140))
        ax1.scatter(sita00501[1], sita00501[0], s=12,color = color(154,201,219))
        ax1.scatter(sita005[1], sita005[0], s=12, color = color(200,36,35))


        ax1.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax1.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))  # 使用科学计数法

        ax1.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax1.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))  # 使用科学计数法

    # plt.subplots_adjust(wspace=0.3, hspace=0.3)  # 增加子图之间的水平和垂直间距
    # plt.savefig(r'F:\全球数据集\论文\GNWL\制图\中间图\GNWL_Topo.svg')
    plt.show()








if __name__ == '__main__':


    # drawFig1(r'F:\全球数据集\论文\GNWL\制图\DATA\dataUse\Global_statis1.csv')
    # drawFig2(r'F:\全球数据集\论文\GNWL\制图\DATA\GNWL\dic',r'F:\全球数据集\论文\GNWL\制图\DATA\dataUse\TopoCatArea.csv',r'F:\全球数据集\论文\GNWL\制图\DATA\dataUse\Compare')
    pass