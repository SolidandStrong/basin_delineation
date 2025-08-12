# -*- coding: utf-8 -*-
"""
@Time ： 2024/9/16 15:37
@Auth ： Bin Zhang
@File ：GNWL_lake.py
@IDE ：PyCharm
"""
import Raster
from osgeo import gdal,ogr
import numpy as np


dmove=[(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)]
dmove_dic = {1: (0, 1), 2: (1, 1), 4: (1, 0), 8: (1, -1), 16: (0, -1), 32: (-1, -1), 64: (-1, 0), 128: (-1, 1)}
def Check_extent(row,col,x,y):
    if 0<=x<row and 0<=y<col:
        return True
    return False

def get_rever_D8(dir, row, col):
    """
    查询输入栅格的上游栅格
    :param dir: array of dir
    :param row: row of the cell
    :param col:
    :return: [(i,j),(),]
    """
    up_cell = []
    row_num, col_num = dir.shape

    for i in range(8):
        now_loc = (row + dmove[i][0], col + dmove[i][1])
        # print(now_loc)
        if 0<=now_loc[0]<row_num and 0<=now_loc[1]<col_num:
            if dir[now_loc[0], now_loc[1]] == 2 ** ((i + 4) % 8):
                up_cell.append(now_loc)

    return up_cell

def reconstruct_channel(lake_file,dir_file,stream_file,acc_file):

    lake = Raster.get_raster(lake_file)
    dir = Raster.get_raster(dir_file)
    stream = Raster.get_raster(stream_file)

    acc = Raster.get_raster(acc_file)
    proj,geo,s_nodata = Raster.get_proj_geo_nodata(stream_file)
    proj,geo,l_nodata = Raster.get_proj_geo_nodata(lake_file)
    proj,geo,d_nodata = Raster.get_proj_geo_nodata(dir_file)

    row,col = dir.shape

    stream1 = np.zeros((row, col))
    stream1[stream != s_nodata] = 1


    lakes = {}
    for i in range(row):
        for j in range(col):
            if lake[i,j] != l_nodata:
                lakes.setdefault(lake[i,j],[]).append((i,j,acc[i,j]))
    # print(lakes)
    for lakeId in lakes:
        lakeCells = lakes[lakeId]
        lakeCells.sort(key = lambda x:x[2],reverse = True)
        maxAccCell = lakeCells[0]
        if stream[maxAccCell[0],maxAccCell[1]] == s_nodata:
            print(lakeId)
            # 从该点寻找下游直到遇到湖泊或河道
            cells = [(maxAccCell[0],maxAccCell[1])]
            while cells:
                cell = cells.pop()
                stream1[cell[0],cell[1]] = 1
                nowDir = dir[cell[0],cell[1]]
                nextCell = (cell[0]+dmove_dic[nowDir][0],cell[1]+dmove_dic[nowDir][1])
                if not Check_extent(row,col,nextCell[0],nextCell[1]):
                    break
                if stream[nextCell[0],nextCell[1]] == s_nodata and lake[nextCell[0],nextCell[1]] == l_nodata:

                    cells.append(nextCell)

    Raster.save_raster(r'F:\全球数据集\论文\GNWL\制图\DATA\GNWL\stream_modified.tif',stream1,proj,geo,gdal.GDT_Byte,0)

def extract_hillslope_lake(stream_link_file,dir_file,lake_file):

    lake = Raster.get_raster(lake_file)
    dir = Raster.get_raster(dir_file)
    stream = Raster.get_raster(stream_link_file)

    proj, geo, s_nodata = Raster.get_proj_geo_nodata(stream_link_file)
    proj, geo, l_nodata = Raster.get_proj_geo_nodata(lake_file)
    proj, geo, d_nodata = Raster.get_proj_geo_nodata(dir_file)

    row, col = dir.shape

    lakes = {}
    riverChannels = {}
    for i in range(row):
        for j in range(col):
            if lake[i,j] != l_nodata:
                lakes.setdefault(lake[i,j],[]).append((i,j))
            elif stream[i,j] != s_nodata:
                riverChannels.setdefault(stream[i,j],[]).append((i,j))

    watershed = np.zeros((row,col))


    # 追溯河流上游
    for riverId in riverChannels:
        rivers = riverChannels[riverId]
        while rivers:
            pop_cell = rivers.pop()
            watershed[pop_cell[0],pop_cell[1]] = riverId
            upCells = get_rever_D8(dir,pop_cell[0],pop_cell[1])
            for cell in upCells:
                if stream[cell[0],cell[1]] == s_nodata and lake[cell[0],cell[1]] == l_nodata:
                    rivers.append(cell)
    Raster.save_raster(r'F:\全球数据集\论文\GNWL\制图\DATA\GNWL\watershed1.tif',watershed,proj,geo,gdal.GDT_Byte,0)
    # 追溯湖泊坡面
    n = 98
    for riverId in lakes:
        lakeCells = lakes[riverId]
        while lakeCells:
            pop_cell = lakeCells.pop()
            watershed[pop_cell[0],pop_cell[1]] = n
            upCells = get_rever_D8(dir,pop_cell[0],pop_cell[1])
            for cell in upCells:
                if stream[cell[0],cell[1]] == s_nodata and lake[cell[0],cell[1]] == l_nodata:
                    lakeCells.append(cell)
        n += 1
    Raster.save_raster(r'F:\全球数据集\论文\GNWL\制图\DATA\GNWL\watershed2.tif', watershed, proj, geo, gdal.GDT_Byte,
                       0)






if __name__ == '__main__':

    lake_file = r'F:\全球数据集\论文\GNWL\制图\DATA\GNWL\lakes.tif'
    dir_file = r'F:\全球数据集\论文\GNWL\制图\DATA\GNWL\Dir.tif'
    stream_file = r'F:\全球数据集\论文\GNWL\制图\DATA\GNWL\stream_modified_link.tif'
    acc_file = r'F:\全球数据集\论文\GNWL\制图\DATA\GNWL\Acc.tif'

    # reconstruct_channel(lake_file,dir_file,stream_file,acc_file)
    extract_hillslope_lake(stream_file,dir_file,lake_file)
    pass
