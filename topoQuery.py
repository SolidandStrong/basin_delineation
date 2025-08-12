import os
import pickle
import sqlite3
import networkx as nx
from osgeo import ogr
from multiprocessing import Pool

class topoStruct(object):
    def __init__(self):
        self.downDict = {}
        self.upDict = {}


def get_basin_topo_info(filePath):

    inDs = ogr.Open(filePath)
    inLayer = inDs.GetLayer(0)

    IdFieldName = "Pfaf_ID"
    IdFieldIndex = inLayer.FindFieldIndex(IdFieldName, 1)
    downIdFieldName = "Down_ID"
    downIdFieldIndex = inLayer.FindFieldIndex(downIdFieldName, 1)

    result = [(feature.GetField(IdFieldIndex), feature.GetField(downIdFieldIndex)) for feature in inLayer]

    inDs.Destroy()
    return result


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


def create_topo_dict(inFilePath, outDictPath, sqlQuery=False, nxModel=False):
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
        topoInfo = get_basin_topo_info(inFilePath)

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
        po.apply_async(create_topo_dict,(j[0],j[1],j[2],j[3],))





if __name__ == "__main__":

    # inPath = r"D:\demo\Asia\lake_result\level_12.gpkg"

    # networkx查询效率较低


    # outPath = r"D:\demo\Asia\lake_result\Dictionary\level_12.dic"

    # arg1 = r"D:\demo\Asia\lake_result\Dictionary\level_12.dic"
    # arg2 = r"D:\demo\Asia\lake_result\Dictionary\level_12.gpickle"
    # #
    # outlet_id = 412100309321
    # time1 = time.time()
    # res = find_upstream_basins(outlet_id, arg1, False)
    # time2 = time.time()
    # rest = find_upstream_basins(outlet_id, arg2, True)
    # time3 = time.time()
    # # create_topo_dict(inPath, arg1, True, False)
    # print(time2 - time1, time3 - time2)

    arg1 = r"D:\demo\Asia\basin_result\gpkg\level_12.gpkg"
    arg2 = r"D:\demo\Asia\basin_result\Dictionary\level_12.dic"
    create_topo_dict(arg1, arg2, True, False)

    pass