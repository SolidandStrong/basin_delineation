import Draw
import Compare_dhp2dic

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':

    # validation
    # 计算RiverLakeBasins中湖泊的上游面积
    Compare_dhp2dic.sbatch_main_calculate_upstreamarea_GNWL('\AllContinent','\dic')
    # 计算Lake-Topo中湖泊的上游面积
    Compare_dhp2dic.sbatch_main_calculate_upstreamarea_TopoCat('\Catchments','\LakeUpstreamArea')
    # 整和RiverLakeBasins和Lake-Topo中共同的湖泊，得到最终的验证结果
    Compare_dhp2dic.merge_csv_TopoCat('\LakeUpstreamArea','\TopoCatArea.csv')



    # Draw Figure 6
    Draw.drawFig1('Global_statis1.csv')

    # Draw Figure 8
    Draw.drawFig2('dic','TopoCatArea.csv','Compare')



