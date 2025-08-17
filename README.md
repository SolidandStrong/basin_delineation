# Basin Delineation ： Data and codes availability statement

## 1. Structure

This project provides three ways to delineate catchments based on DEM, which are organized in the following three folders:
1) The "basin" folder: river-oriented catchment delineation without considering lakes or reservoirs (i.e. the usual way in digital terrain analysis);
2) The "lake-cat" folder: delineation of nested lake-catchments, including the delineation of full lake catchments and inter-lake catchments, the construction of topological relationship among lakes/lake-catchments, and the tracing of flow path among upstream and stream lakes. Rivers are not considered here.
2) The "lake-river-cat" folder: catchment delineation considering both rivers and lakes/reservoirs. The discretized units include subbasins (with one channel in each subbasin), hillslopes (without river channel and usually adjacent to lakes or reservoirs), rivers, and lakes/reservoirs. The upstream and downstream relationships among these units are constructed.

Besides, the code in the "core" folder is written in C and designed to conduct raster calculation more efficiently; The code in the "util" folder is written in Python and designed to provide general geographic data operation interfaces which are called many times. 

## 2. Dependencies

- Python >= 3.6

- GDAL >= 3.0.1

- Rtree >= 0.9.7

## 3. Data Requiremenmt

- D8 Flow Direction Data

  - datatype must be unsigned char

    - 0 - river mouth

    - 1- east

    - 2 - southeast

    - 4- south

    - 8 - southwest

    - 16 - west

    - 32 - northwest

    - 64 - north

    - 128 - northeast

    - 247 - nodata

    - 255 - inland depression
   
  - 
   Data and codes availability statement
This document describes the entire RiverLakeBasins analysis workflow, which consists of three main steps: dataset generation, data validation, and plotting. The following describes these three steps, including the data and code used, along with detailed instructions for code usage, data acquisition, and download links. Users are welcome to download these data and code and replicate the work described in this document.

Dataset Production Description
The main dataset production code is located in the lake-river-cat folder. The Python files used are main.py (which generates the tif and shp files for each level, organized into nested folders) and postprocess.py (which merges the shp files in nested folders into a complete hierarchical shp file).
1. Using main.py
First, prepare a configuration file, specifying the location of each parameter. The configuration file (ini) and specific parameters are as follows, using Asia as an example.

Asia.ini Configuration Parameter Table
Project_root = "./Asia" # Root directory
Basin_database = "./4_level.db" # NWEI .shp database address
Alter_database = "./lake_alter.db" # Automatically generated lake attribute database address
Lake_shp = "./Asia_lakes.shp" # Hydro Lakes .shp file address for the corresponding continent
Minimum_river_threshold = 30.0 # Minimum runoff accumulation threshold, change to your needs
Code = 4 # NWEI continent code
Src_code = 4 # RiverLakeBasins continent code, consistent with NWEI
The data are openly available at https://doi.org/10.5281/zenodo.15286063.

To use the code, enter a command prompt window and type:

python main.py [-p process] config level You can run it.

"-p process" indicates the number of CPUs to use for the code, which can be set based on your computer's configuration. "config" refers to the ini configuration file, and "level" indicates the level of the program. You can select from {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}.

2. Using postprocess.py

First, prepare the configuration file (Asia.ini) as above. Then, enter a command prompt and type "Python postprocess.py config level" to run it.

"config" refers to the ini configuration file, and "level" indicates the level of the program. You can select from {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}.
 
Data Validation Description
The validation dataset includes RiverLakeBasins and Lake-TopoCat. The data used can be downloaded from https://doi.org/10.5281/zenodo.15695045.
The code is stored in compare_dhp2dic.py. The main functions used are sbatch_main_calculate_upstreamarea_GNWL, sbatch_main_calculate_upstreamarea_TopoCat, and merge_csv_TopoCat.

sbatch_main_calculate_upstreamarea_GNWL(venu1, venu2) calculates the upstream area of lakes in RiverLakeBasins. The input parameters are venu1: the directory where the RiverLakeBasins files are stored, and venu2: the output directory for the calculation results.
sbatch_main_calculate_upstreamarea_TopoCat(venu1, venu2) calculates the upstream area of lakes in Lake-TopoCat. The input parameters are venu1: the directory where the Lake-TopoCat Catchments are stored, and venu2: the output directory for the calculation results.

merge_csv_TopoCat(venu2, file2) calculates the CSI verification results of the first two steps. The input parameters are venu2: the directory where the Lake-TopoCat results are stored, and file2: the results of the first step.
 
Draw Description
1. Draw Figure 6. Run Draw.drawFig1('Global_statis1.csv') in main.py. Because the Global_statis1.csv file exceeds Github's upload limit, it cannot be uploaded. The data can be found at 10.5281/zenodo.16809392.
2. Draw Figure 7 in ArcMap. The required data is the RiverLakeBains12-level vector data, available at https://doi.org/10.5281/zenodo.15695045.
3. Draw Figure 8. Run Draw.drawFig2('dic', 'TopoCatArea.csv', 'Compare') in main.py. Because the data files exceed Github's upload limit, they cannot be uploaded. The data can be found at 10.5281/zenodo.16809392.
4. Figure 9. This figure was drawn using Arcmap. The plot file (.mpk) is available at 10.5281/zenodo.16809392 and is titled "Comparison of GNWL and HyBAS Inner Flow Areas."
5. Figure 10. This figure was drawn using Arcmap. The plot file (.mpk) is available at 10.5281/zenodo.16809392 and is titled "Comparison of Lake 16256."
6. The data in Table 2 were obtained from https://doi.org/10.1016/j.scitotenv.2021.145463. For technical details, please refer to this paper, available at 10.5281/zenodo.16809392.
 
