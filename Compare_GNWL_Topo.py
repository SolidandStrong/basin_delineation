# -*- coding: utf-8 -*-
"""
@Time ： 2024/10/11 8:45
@Auth ： Solid
@File ：Compare_GNWL_Topo.py
@IDE ：PyCharm
"""
import os
import csv
from osgeo import gdal,ogr
import numpy as np


def Connect_Topo_GNWL(TopoArea,GNWLArea,outAreaFile):
    # 由于GNWL是按洲划分的，需要将每个州内的湖泊与TopoCat通过Hylak_id匹配

    GNWL = {}
    with open(GNWLArea,'r') as f:
        reader = csv.reader(f)
        for i in reader:
            GNWL.setdefault(i[0],float(i[1]))
        f.close()

    TopoGNWL = [['Hylak_id','TopoCatArea/km2','GNWLArea/km2']]
    with open(TopoArea,'r') as f:
        reader = csv.reader(f)
        for i in reader:
            if i[0] in GNWL:
                TopoGNWL.append([i[0],float(i[1]),GNWL[i[0]]])
        f.close()

    with open(outAreaFile,'w+') as f:
        writer = csv.writer(f)
        writer.writerows(TopoGNWL)
        f.close()

def Read_Cal_GNWL_Continent(ds_name,venu):
    """
    统计GNWL内的每个洲的湖泊数量、流域平均面积、湖泊平均面积、坡面平均面积
    :param ds_name:
    :return:
    """
    """Copye layers to feature dateset in a file geodatabase."""
    in_ds = ogr.Open(ds_name)
    if in_ds is None:
        raise RuntimeError('Could not Open dataSource')

    Result = [[os.path.basename(ds_name),'AllNumber',
               'basinArea_avg','basinArea_std','basinArea_num',
               'LakeArea_avg','LakeArea_std','LakeArea_num',
               'HillArea_avg','HillArea_std','HillArea_num',
               'EndorArea_avg','EndorArea_std','EndorArea_num'
               ]]


    for i in in_ds:
        Name = i.GetName()
        print(Name)
        allArea = []
        basinArea = []
        lakeArea = []
        hillArea = []
        endorArea = []
        allNum = 0
        for j in i:
            allNum +=1
            allArea.append(j.GetField('POLY_AREA'))
            feaType = j.GetField('Type')
            if feaType == 1:
                basinArea.append(j.GetField('POLY_AREA'))
            if feaType == 2:
                lakeArea.append(j.GetField('POLY_AREA'))
            if feaType == 3:
                hillArea.append(j.GetField('POLY_AREA'))
            if j.GetField('Endor') == 1:
                endorArea.append(j.GetField('POLY_AREA'))
            # print(j.GetField('POLY_AREA'))
        Result.append([Name,allNum,
                      np.mean(basinArea),np.std(basinArea),len(basinArea),
                      np.mean(lakeArea),np.std(lakeArea),len(lakeArea),
                      np.mean(hillArea),np.std(hillArea),len(hillArea),
                      np.mean(endorArea),np.std(endorArea),len(endorArea)])
    out_file = os.path.join(venu,str(os.path.basename(ds_name).split('.')[0]) + '.csv')
    print(out_file)
    with open(out_file, 'w+', newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(Result)
        f.close()

    return Result
def batch(venu,outVenu):
    Result=[]
    gdb_file=os.listdir(venu)
    for temp_file in gdb_file:
        print(temp_file)
        file=os.path.join(venu,temp_file)
        Result+=Read_Cal_GNWL_Continent(file,outVenu)
    out_file = os.path.join(outVenu,'Global_statis1.csv')
    with open(out_file,'w+',newline="") as f:
        csv_writer=csv.writer(f)
        csv_writer.writerows(Result)
        f.close()

if __name__ == '__main__':


    # ds_name = r'F:\全球数据集\论文\GNWL\制图\DATA\GNWL_prj\Arctic.gdb'
    # Read_Cal_GNWL_Continent(ds_name)

    # batch(r'F:\全球数据集\论文\GNWL\制图\DATA\GNWL_prj',r'F:\全球数据集\论文\GNWL\制图\DATA\dataUse')
    batch(r'F:\全球数据集\论文\GNWL\制图\DATA\数据库\GNWL_prj', r'F:\全球数据集\论文\GNWL\制图\DATA\dataUse')
    pass