import os
import pickle
import sqlite3
import networkx as nx
from osgeo import ogr
from multiprocessing import Pool
import csv
import dbfread
class topoStruct(object):
    def __init__(self):
        self.downDict = {}
        self.upDict = {}



def get_basin_topo_info_sqlite(filePath):

    attrTableName = "data"
    idFieldName = "Pfaf_ID"
    downIdFieldName = "Down_ID"

    conn = sqlite3.connect(filePath)
    cursor = conn.cursor()
    sql_line = "select %s, %s from %s;" % (idFieldName, downIdFieldName, attrTableName)
    cursor.execute(sql_line)
    result = cursor.fetchall()

    conn.close()
    return result


def find_upstream_basins(outlet_basin, dictPath, nxModel=False):

    if nxModel is True:
        G = nx.read_gpickle(dictPath)
        subGraph = nx.bfs_tree(G, outlet_basin, reverse=True)
        result = subGraph.nodes()

    else:
        # 加载拓扑字典
        with open(dictPath, "rb") as fs:
            topoDict = pickle.load(fs)
        fs.close()
        # 初始化返回结果
        upDict = topoDict.upDict

        result = []
        query_queue = [outlet_basin]
        num = 1
        # 查询上游
        while num > 0:
            temp = query_queue.pop()
            result.append(temp)
            num -= 1
            ups = upDict[temp]
            up_num = len(ups)
            if up_num > 0:
                num += up_num
                query_queue.extend(ups)

    return result

def batch(GPKG_venu,out_venu):
    """
    并行批量生成dic文件
    :param gpkg_dir:
    :param out_venu:
    :return:
    """

    rigion = os.listdir(GPKG_venu)
    input = []
    for i in rigion:   # Af,As,...
        files_dir=os.path.join(GPKG_venu,i)
        shp_files=os.listdir(files_dir)
        for file in shp_files:   # Af_level12.gpkg
            basename = file.split('.')
            if file[-4:]=='gpkg':
                gpkg_file=os.path.join(files_dir,file)
                out_dir=os.path.join(out_venu,i)
                if not os.path.exists(out_dir):
                    os.mkdir(out_dir)
                out_dic=os.path.join(out_venu,basename[1]+'.dic')
                print(gpkg_file,out_dic)
                input.append([gpkg_file,out_dic,True,False])
    po=Pool(30)
    for j in input:
        po.apply_async(create_topo_dict_GNWL,(j[0],j[1],j[2],j[3],))

# 处理GNWL
def get_basin_topo_info_GNWL(filePath):

    print(filePath)

    dbfFileName = os.path.basename(filePath).split('.')[0] + '.dbf'
    dbfFile = os.path.join(os.path.dirname(filePath), dbfFileName)
    # FIDArea = readdbf(dbfFile)
    BasinIdArea = []
    table = dbfread.DBF(dbfFile)
    # print(len(table))
    n = 0
    for i in table:
        BasinIdArea.append(((int(i['Basin_ID'])),int(i['Down_ID'])))
        n += 1
    return BasinIdArea

def create_topo_dict_GNWL(inFilePath, outDictPath, sqlQuery=False, nxModel=False):
    """
    构建字典的
    :param inFilePath:
    :param outDictPath:
    :param sqlQuery:
    :param nxModel:
    :return:
    """

    # 查询拓扑信息
    if sqlQuery is True:
        topoInfo = get_basin_topo_info_sqlite(inFilePath)
    else:
        topoInfo = get_basin_topo_info_GNWL(inFilePath)

    # 构建拓扑
    # networkx
    if nxModel is True:
        # 构建有向五环图
        G = nx.DiGraph()
        G.add_edges_from(topoInfo)
        # 保存文件
        nx.write_gpickle(G, outDictPath)
    # Python字典
    else:
        # 构建上下游字典
        topoD = topoStruct()
        downDict = topoD.downDict
        upDict = topoD.upDict
        # 构建下游字典，同时初始化上游字典
        for cur_basin, down_basin in topoInfo:
            downDict[cur_basin] = down_basin
            upDict[cur_basin] = []
        # 构建上游字典
        for cur_basin, down_basin in downDict.items():
            if down_basin > 0:
                upDict[down_basin].append(cur_basin)
        # 保存文件
        with open(outDictPath, "wb") as fs:
            pickle.dump(topoD, fs)
        fs.close()

def calculate_lake_upstreamarea_GNWL(filePath,dicPath,outAreaPath):
    """

    :param filePath: .shp
    :param dicPath: .dic
    :param outAreaPath: 输出.csv
    :return:
    """

    dbfFileName = os.path.basename(filePath).split('.')[0] + '.dbf'
    dbfFile = os.path.join(os.path.dirname(filePath),dbfFileName)
    FIDArea,id_FID,FID_id = readdbf(dbfFile)


    #
    Lake_area = []
    for lakeid in id_FID:

        upstream_ids = find_upstream_basins(lakeid,dicPath)
        # print(upstream_ids)
        sumarea = 0
        for upstream_id in upstream_ids:
            sumarea += float(FIDArea[upstream_id])
        # print(id_FID[lakeid], sumarea)
        Lake_area.append([id_FID[lakeid],sumarea])
    #

    with open(outAreaPath,'w',newline="") as f:
        writer = csv.writer(f)
        writer.writerows(Lake_area)
        f.close()

def main_calculate_upstreamarea_GNWL(venu,filePath):
    get_basin_topo_info_GNWL(filePath)
    basename = os.path.basename(filePath)
    name = basename.split('.')[0]
    outDicPath = os.path.join(venu,name+'.dic')
    # create_topo_dict_GNWL(filePath,outDicPath)
    outAreaPath = os.path.join(venu,name+'_area.csv')
    calculate_lake_upstreamarea_GNWL(filePath,outDicPath,outAreaPath)

def sbatch_main_calculate_upstreamarea_GNWL(catchmentDir,venu):

    catchmentfileNames = os.listdir(catchmentDir)
    for catchmentfileName in catchmentfileNames:
        if catchmentfileName.split('.')[-1] != 'shp':
            continue
        # print(catchmentfileName)
        main_calculate_upstreamarea_GNWL(venu,os.path.join(catchmentDir,catchmentfileName))

def readdbf(dbfFile):
    """
    矢量图层的dbf数据库，记录BASINID：面积，Hylak_id
    :param dbfFile:
    :return:
    """

    BasinIdArea = {}
    table = dbfread.DBF(dbfFile)
    # print(len(table))
    n = 0
    FID_id = {}
    id_FID = {}
    for i in table:
        BasinIdArea.setdefault(int(i['Basin_ID']),i['Area'])
        if i['Hylak_id'] != 0:
            # FID_id.setdefault(n,i['Basin_ID'])
            id_FID.setdefault(i['Basin_ID'],i['Hylak_id'])
            # print(i['Hylak_id'])
        n += 1
    return BasinIdArea,id_FID,FID_id


# 处理Lake-TopoCat
def create_topo_dict_TopoCat(inFilePath, outDictPath, sqlQuery=False, nxModel=False):
    """
    构建字典的
    :param inFilePath:
    :param outDictPath:
    :param sqlQuery:
    :param nxModel:
    :return:
    """

    # 查询拓扑信息
    if sqlQuery is True:
        topoInfo = get_basin_topo_info_sqlite(inFilePath)
    else:
        topoInfo = get_basin_topo_info_TopoCat(inFilePath)

    # 构建拓扑
    # networkx
    if nxModel is True:
        # 构建有向五环图
        G = nx.DiGraph()
        G.add_edges_from(topoInfo)
        # 保存文件
        nx.write_gpickle(G, outDictPath)
    # Python字典
    else:
        # 构建上下游字典
        topoD = topoStruct()
        downDict = topoD.downDict
        upDict = topoD.upDict
        # 构建下游字典，同时初始化上游字典
        for cur_basin, down_basin in topoInfo:
            downDict[cur_basin] = down_basin
            upDict[cur_basin] = []
        # 构建上游字典
        for cur_basin, down_basin in downDict.items():
            if down_basin > 0:
                upDict[down_basin].append(cur_basin)
        # 保存文件
        with open(outDictPath, "wb") as fs:
            pickle.dump(topoD, fs)
        fs.close()

def get_basin_topo_info_TopoCat(filePath):

    inDs = ogr.Open(filePath)
    inLayer = inDs.GetLayer(0)

    IdFieldName = "Outlet_id"
    IdFieldIndex = inLayer.FindFieldIndex(IdFieldName, 1)
    downIdFieldName = "D_out_id"
    downIdFieldIndex = inLayer.FindFieldIndex(downIdFieldName, 1)

    result = [(feature.GetField(IdFieldIndex), feature.GetField(downIdFieldIndex)) for feature in inLayer]
    # print(result)
    inDs.Destroy()
    return result

def calculate_lake_upstreamarea_TopoCat(filePath,dicPath,outAreaPath):

    inDs = ogr.Open(filePath)
    inLayer = inDs.GetLayer(0)

    IdFieldName = "Outlet_id"
    IdFieldIndex = inLayer.FindFieldIndex(IdFieldName, 1)


    FID_id = {}
    id_FID = {}
    for feature in enumerate(inLayer, 0):
        FID_id.setdefault(feature[0],feature[1].GetField(IdFieldIndex))
        id_FID.setdefault(feature[1].GetField(IdFieldIndex),feature[0])

    Lake_area = []
    for lakeid in id_FID:
        upstream_ids = find_upstream_basins(lakeid,dicPath)
        sumarea = 0
        for upstream_id in upstream_ids:
            # print(upstream_id)
            temp_Fea = inLayer.GetFeature(id_FID[upstream_id])
            sumarea += temp_Fea.GetField('Cat_area')
        Lake_area.append([inLayer.GetFeature(id_FID[lakeid]).GetField('Hylak_id'),sumarea])

    inDs.Destroy()
    with open(outAreaPath,'w',newline="") as f:
        writer = csv.writer(f)
        writer.writerows(Lake_area)
        f.close()

def main_calculate_upstreamarea_TopoCat(venu,filePath):
    get_basin_topo_info_TopoCat(filePath)
    basename = os.path.basename(filePath)
    name = basename.split('.')[0]
    outDicPath = os.path.join(venu,name+'_dic.dic')
    create_topo_dict_TopoCat(filePath,outDicPath)
    outAreaPath = os.path.join(venu,name+'_area.csv')
    calculate_lake_upstreamarea_TopoCat(filePath,outDicPath,outAreaPath)

def sbatch_main_calculate_upstreamarea_TopoCat(catchmentDir,venu):

    catchmentfileNames = os.listdir(catchmentDir)
    for catchmentfileName in catchmentfileNames:
        if catchmentfileName.split('.')[-1] != 'shp':
            continue
        print(catchmentfileName)
        main_calculate_upstreamarea_TopoCat(venu,os.path.join(catchmentDir,catchmentfileName))

def merge_csv_TopoCat(venu,areacsvPath):
    fileNames = os.listdir(venu)
    result = []
    for fileName in fileNames:
        if fileName.split('.')[-1] != 'csv':
            continue
        temp_infos = {}
        temp_con = []
        with open(os.path.join(venu,fileName),'r') as f:
            con = csv.reader(f)
            for info in con:
                temp_infos.setdefault(info[0],[]).append(float(info[1]))
            for info in temp_infos:
                temp_con.append([info,sum(temp_infos[info])])
            result += temp_con
            f.close()

    with open(areacsvPath,'w+',newline="") as f:
        writer = csv.writer(f)
        writer.writerows(result)
        f.close()

if __name__ == "__main__":


    # 处理LAKE-TopoCat的代码
    # get_basin_topo_info_TopoCat(r'F:\全球数据集\论文\GNWL\制图\DATA\HydroLAKES_TopoCat_v1.1.shp\Catchments\Catchments_pfaf_14.shp')
    # create_topo_dict(r'F:\全球数据集\论文\GNWL\制图\DATA\HydroLAKES_TopoCat_v1.1.shp\Catchments\Catchments_pfaf_14.shp',r'F:\全球数据集\论文\GNWL\制图\DATA\Trial_dic\Dic.dic')
    # find_upstream_basins(14000959,r'F:\全球数据集\论文\GNWL\制图\DATA\Trial_dic\Dic.dic')
    # calculate_lake_upstreamarea_TopoCat(r'F:\全球数据集\论文\GNWL\制图\DATA\HydroLAKES_TopoCat_v1.1.shp\Catchments\Catchments_pfaf_14.shp')
    # 主函数
    # main_calculate_upstreamarea_TopoCat(r'F:\全球数据集\论文\GNWL\制图\DATA\Trial_dic',r'F:\全球数据集\论文\GNWL\制图\DATA\HydroLAKES_TopoCat_v1.1.shp\Catchments\Catchments_pfaf_14.shp')
    # 批量处理
    # sbatch_main_calculate_upstreamarea_TopoCat(r'F:\全球数据集\论文\GNWL\制图\DATA\HydroLAKES_TopoCat_v1.1.shp\Catchments',r'F:\全球数据集\论文\GNWL\制图\DATA\HydroLAKES_TopoCat_v1.1.shp\LakeUpstreamArea')
    # 结果整合
    # merge_csv_TopoCat(r'F:\全球数据集\论文\GNWL\制图\DATA\HydroLAKES_TopoCat_v1.1.shp\LakeUpstreamArea',r'F:\全球数据集\论文\GNWL\制图\DATA\HydroLAKES_TopoCat_v1.1.shp\A.csv')

    # 处理GNWL的代码
    # get_basin_topo_info_GNWL(r'F:\全球数据集\论文\GNWL\制图\DATA\GNWL\gpkg\Ar_level_12.gpkg')
    # create_topo_dict_GNWL()
    # calculate_lake_upstreamarea_GNWL(r'F:\全球数据集\论文\GNWL\制图\DATA\GNWL\AllContinent\Arctic_12.shp',r'F:\全球数据集\论文\GNWL\制图\DATA\GNWL\dic\Arctic_12.dic',r'F:\全球数据集\论文\GNWL\制图\DATA\GNWL\watershedShp\A.csv')


    # 最终使用的代码
    # sbatch_main_calculate_upstreamarea_GNWL(r'F:\全球数据集\论文\GNWL\制图\DATA\GNWL\AllContinent',
    #                                         r'F:\全球数据集\论文\GNWL\制图\DATA\GNWL\dic')
    #
    # sbatch_main_calculate_upstreamarea_TopoCat(
    #     r'F:\全球数据集\论文\GNWL\制图\DATA\HydroLAKES_TopoCat_v1.1.shp\Catchments',
    #     r'F:\全球数据集\论文\GNWL\制图\DATA\HydroLAKES_TopoCat_v1.1.shp\LakeUpstreamArea')

    merge_csv_TopoCat(r'F:\全球数据集\论文\GNWL\制图\DATA\HydroLAKES_TopoCat_v1.1.shp\LakeUpstreamArea',
                      r'F:\全球数据集\论文\GNWL\制图\DATA\dataUse\TopoCatArea.csv')
    pass