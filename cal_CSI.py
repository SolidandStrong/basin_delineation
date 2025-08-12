# -*- coding: utf-8 -*-
"""
@Time ： 2024/10/14 10:11
@Auth ： Bin Zhang
@File ：cal_CSI.py
@IDE ：PyCharm
"""
from osgeo import ogr
from topoQuery import topoStruct
import numpy as np
import pandas as pd
import extractBasin
import topoQuery
import os
import csv

def funcA(fn, inFile, basin_id):

    ds = ogr.Open(fn)
    layer = ds.GetLayer()
    feature = layer.GetFeature(0)
    geom = feature.GetGeometryRef()
    ds.Destroy()
    geom = geom.Buffer(0.0)

    inDs = ogr.Open(inFile)

    table_name = os.path.basename(inFile).split('.')[0]
    sql_line = "select * from %s where Pfaf_ID=%d;" % (table_name, basin_id)
    resLayer = inDs.ExecuteSQL(sql_line)

    resNum = resLayer.GetFeatureCount()
    # 判断是否有正确的空间查询结果
    flag = True
    if resNum <= 0:
        print("No basin found!")
        flag = False
    elif resNum > 1:
        print("More than one basin found!")
        flag = False
    else:
        pass
    if flag is False:
        inDs.ReleaseResultSet(resLayer)
        inDs.Destroy()
        exit(-1)

    feature = resLayer.GetNextFeature()
    area = feature.GetField("Total_Area")
    inGeom = feature.GetGeometryRef()
    inGeom = inGeom.Buffer(0.0)
    inDs.ReleaseResultSet(resLayer)
    inDs.Destroy()

    interGeom = geom.Intersection(inGeom)
    intersectArea = interGeom.GetArea()
    area = area * intersectArea / inGeom.GetArea()

    return intersectArea, inGeom.GetArea(), area


def funcB(fn, inFile, basin_id, dicFile):

    ds = ogr.Open(fn)
    layer = ds.GetLayer()
    feature = layer.GetFeature(0)
    geom = feature.GetGeometryRef()
    geom = geom.Buffer(0.0)
    ds.Destroy()

    upStreamBasins = topoQuery.find_upstream_basins(basin_id, dicFile, nxModel=False)
    upStreamBasins.remove(basin_id)
    conList = ",".join(map(str, upStreamBasins))

    inDs = ogr.Open(inFile)
    # table_name = "data"
    table_name = os.path.basename(inFile).split('.')[0]
    sql_column_name = "Pfaf_ID"
    sql_line = "select * from %s where %s in (%s);" % (table_name, sql_column_name, conList)

    resLayer = inDs.ExecuteSQL(sql_line)
    area = 0.0
    intersectArea = 0.0
    unionArea = 0.0
    for feature in resLayer:
        area += feature.GetField("Total_Area")
        inGeom = feature.GetGeometryRef()
        inGeom = inGeom.Buffer(0.0)
        intersectGeom = geom.Intersection(inGeom)
        intersectArea += intersectGeom.GetArea()
        unionArea += inGeom.GetArea()

    inDs.ReleaseResultSet(resLayer)
    inDs.Destroy()

    return intersectArea, unionArea, area, geom.GetArea()


def calc_csi_and_area(fn, inFile, dicFile):

    ds = ogr.Open(fn)
    layer = ds.GetLayer()
    feature = layer.GetFeature(0)

    lon = feature.GetField("LONG_NEW")
    lat = feature.GetField("LAT_NEW")
    # lon = feature.GetField("LONG_ORG")
    # lat = feature.GetField("LAT_ORG")
    rep_area = feature.GetField("AREA")
    hyd_area = feature.GetField("AREA_HYS")
    # 提取所处流域
    basin_id = extractBasin.locate_basin_by_point(lon, lat, inFile)

    if basin_id is None:
        return 0, 0, 0, 0, 0
    # 计算当前流域与完整流域范围的交集
    a, b, c = funcA(fn, inFile, basin_id)
    d, e, f, g = funcB(fn, inFile, basin_id, dicFile)
    # 提取上游流域范围和上游流域的面积
    area = c + f
    csi = (a + d) / (b + e + g - a - d)

    return csi, abs(area - rep_area) / rep_area, rep_area, area, hyd_area


def calc_csi_and_area2(lon, lat, fn, inFile, dicFile):

    ds = ogr.Open(fn)
    layer = ds.GetLayer()
    feature = layer.GetFeature(0)

    rep_area = feature.GetField("AREA")
    hyd_area = feature.GetField("AREA_HYS")
    # 提取所处流域
    basin_id = extractBasin.locate_basin_by_point(lon, lat, inFile)
    if basin_id is None:
        return 0, 0, 0, 0, 0
    # 计算当前流域与完整流域范围的交集
    a, b, c = funcA(fn, inFile, basin_id)
    d, e, f, g = funcB(fn, inFile, basin_id, dicFile)
    # 提取上游流域范围和上游流域的面积
    area = c + f
    csi = (a + d) / (b + e + g - a - d)

    return csi, abs(area - rep_area) / rep_area, rep_area, area, hyd_area


def main(spath,folder, inFile, dicFile,out_file):
    """

    :param folder: 存储GRDC流域的路径
    :param inFile: NWEI的层级gpkg
    :param dicFile: NWEI的层级dic
    :return:
    """

    # 读取站点列表
    # spath = r"F:\全球数据集\图表\素材\画图data\GRDC\Result\Af_filter_stations.txt"
    stations = np.loadtxt(spath, dtype=np.int32)
    stations = stations.ravel()

    result = []
    for station in stations:
        # print(station)
        fn = os.path.join(folder, "grdc_basins_smoothed_md_no_%d.shp" % station)
        print(fn)
        temp = calc_csi_and_area(fn, inFile, dicFile)
        r = (station, ) + temp
        result.append(r)

    df = pd.DataFrame(result, columns=["GRDC_NO", "CSI", "RelativeError", "GRDC_AREA", "CUR_AREA", "HYS_AREA"])
    df.to_csv(out_file)


def single(a, b, c, folder, inFile, dicFile):


    fn = os.path.join(folder, "grdc_basins_smoothed_md_no_%d.shp" % a)
    temp = calc_csi_and_area2(c, b, fn, inFile, dicFile)
    r = (a, ) + temp
    print(r)


                            # ****************** 张斌新写的 **********************


def compare(global_file1,global_file2,out_file):
    """
    该函数是将两套数据进行整理。选择修正后的gauge点位进行验证
    # 构建字典，选择误差较小的数据，最后存起来，仅挑选GRDC面积大于100km2的
    :param global_file1:Long_OGR
    :param global_file2:Long_NEW
    :param out_file:
    :return:
    """
    result={}
    temp_data=[]
    with open(global_file1,'r') as f:
        A=csv.reader(f)
        # print(A)
        for i in A:
            temp_data.append(i)
    f.close()
    temp_data2 = []
    with open(global_file2,'r') as f:
        A=csv.reader(f)
        # print(A)
        for i in A:
            temp_data2.append(i)
    f.close()
    # print(temp_data)
    # GRDC_ID,CSI,Relative_error,GRDC_Area,Cur_Area,Hys_Area,Compare_Area,Q
    for data in temp_data[1:]:
        GRDC_id=data[1]
        if float(data[4]) > 100 and float(data[5]) > 100:
            Compare_Area=data[6] if (abs(float(data[4])-float(data[5]))>abs(float(data[6])-float(data[5]))) else data[4]
            Q=abs(float(Compare_Area)-float(data[5]))/float(Compare_Area)
            result.setdefault(GRDC_id,data[1:7]+[Compare_Area,Q])

    for data in temp_data2[1:]:
        GRDC_id=data[1]
        if GRDC_id in result:
            if float(data[4]) > 100 and float(data[5]) > 100:
                Q1=float(result[GRDC_id][7])
                Compare_Area=data[6] if (abs(float(data[4])-float(data[5]))>abs(float(data[6])-float(data[5]))) else data[4]
                Q=abs(float(Compare_Area)-float(data[5]))/float(Compare_Area)
                if Q<Q1:
                    result[GRDC_id]=data[1:7]+[Compare_Area,Q]
    title=['GRDC_NO', 'CSI', 'RelativeError', 'GRDC_AREA', 'CUR_AREA', 'HYS_AREA','Compare_Area','Q']
    write_con=[title]+list(result.values())
    with open(out_file,'w',newline='') as f:
        A=csv.writer(f)
        A.writerows(write_con)
    f.close()
    return list(result.values())
def Cal_Q(result):

    num=[1 if float(result[i][7])<=0.05 else 0 for i in range(len(result))]
    return sum(num)/len(num)

def sbatch_compare(venu):
    rigion = ['As',  'Si', 'Ar','Af','Na','Sa','Eu','Au']
    OGR_path=os.path.join(venu,'OGR')
    NEW_path=os.path.join(venu,'NEW')
    OUT_path=os.path.join(venu,'Final')
    Result=[['GRDC_NO', 'CSI', 'RelativeError', 'GRDC_AREA', 'CUR_AREA', 'HYS_AREA','Compare_Area','Q']]
    Q_res=[]
    for i in rigion:
        print(i)
        global_file1 = os.path.join(OGR_path,i+'_result2.csv')
        global_file2 = os.path.join(NEW_path, i + '_result3.csv')
        out_file = os.path.join(OUT_path,i+'_result_100.csv')
        temp_result=compare(global_file1,global_file2,out_file)
        Q_res.append(Cal_Q(temp_result))
        Result+=temp_result

    Q_res.append(Cal_Q(Result[1:]))
    with open(r'F:\全球数据集\图表\素材\画图data\GRDC\Result\Result\OGR_NEW\global_result_100.csv','w',newline='') as f:
        A=csv.writer(f)
        A.writerows(Result)
    f.close()

    with open(r'F:\全球数据集\图表\素材\画图data\GRDC\Result\Result\OGR_NEW\Q_100.csv','w',newline="") as f:
        A = csv.writer(f)
        A.writerow(rigion)
        A.writerow(Q_res)
    f.close()






if __name__ == "__main__":
    # arg0= = r"F:\全球数据集\图表\素材\画图data\GRDC\Result\Af_filter_stations.txt"
    # arg1 = r"F:\全球数据集\图表\素材\画图data\GRDC\statbas_shp_zip"
    # arg2 = r"F:\全球数据集\图表\素材\画图data\GRDC\Result\Af\Af_level_12.gpkg"
    # arg3 = r"F:\全球数据集\图表\素材\画图data\GRDC\Result\Af\Af_level_12.dic"
    # arg4 = r"F:\全球数据集\图表\素材\画图data\GRDC\Result\Af\result2.csv"
    # main(arg0,arg1, arg2, arg3,arg4)

    rigion = ['Af','As', 'Ar', 'Eu', 'Sa', 'Na', 'Au', 'Si', 'Gr']
    for i in rigion:
        arg0 = os.path.join(r"F:\全球数据集\图表\素材\画图data\GRDC\Result",i,i+'_filter_stations.txt')
        arg1 = r"F:\全球数据集\图表\素材\画图data\GRDC\statbas_shp_zip"
        arg2 = os.path.join(r'F:\全球数据集\图表\素材\画图data\GRDC\Result',i,i+'_level_12.gpkg')
        arg3 = os.path.join(r'F:\全球数据集\图表\素材\画图data\GRDC\Result',i,i+'_level_12.dic')   # AU要改下划线
        arg4 = os.path.join(r'F:\全球数据集\图表\素材\画图data\GRDC\Result',i,i+'_result2.csv')
        print(i)
        main(arg0,arg1,arg2,arg3,arg4)

    # global_file1=r'F:\全球数据集\图表\素材\画图data\GRDC\Result\Result\OGR_NEW\OGR\As_result2.csv'
    # global_file2=r'F:\全球数据集\图表\素材\画图data\GRDC\Result\Result\OGR_NEW\NEW\As_result3.csv'
    # out_file=r'F:\全球数据集\图表\素材\画图data\GRDC\Result\Result\OGR_NEW\Final\As_result.csv'
    # compare(global_file1,global_file2,out_file)

    # sbatch_compare(r'F:\全球数据集\图表\素材\画图data\GRDC\Result\Result\OGR_NEW')


    # station_id = 2588201
    #
    #
    # new_lat = 34.897091
    # new_lon = 135.720834
    # single(station_id, new_lat, new_lon, arg1, arg2, arg3)

