The Land Processes Distributed Active Archive Center (LP DAAC) distributes NASA Visible Infrared Imaging Radiometer Suite (VIIRS) Surface Reflectance products. The NASA VIIRS Surface Reflectance products are archived and distributed in a file format call HDF-EOS5. The Hierarchical Data Format version 5 (HDF5) is a NASA selected format of choice for standard science product archival and distribution, and is the underlying format for HDF-EOS5. HDF-EOS is the standard format and I/O library for the Earth Observing System (EOS) Data and Information System (EOSDIS). HDF-EOS5 extends the capabilities of the HDF5 storage format, adding support for the various EOS data types (e.g., Point, Swath, and Grid) into the HDF5 framework.

This tutorial demonstrates how to open and interact with VIIRS Surface Reflectance data files (HDF-EOS5 (.h5)) in a python environment. Additionally, this tutorial demonstrates how to define the coordinate reference system (CRS) and export each science dataset layer as a GeoTIFF file that can be loaded with spatial referencing into a GIS and/or Remote Sensing software program. Visit the [LP DAAC website](https://lpdaac.usgs.gov/product_search/?keyword=Surface+Reflectance&query=VIIRS&sort=title&view=cards) for more information about NASA VIIRS Surface Reflectance products.
***  
## Topics Covered:
1. **Getting Started**    
    1a. Import Packages   
    1b. Set Up the Working Environment      
    1c. Retrieve Files           
    1d. Specify the filename for the output GeoTIFFs
2. **Importing Data**    
    2a. Read in a VIIRS HDF-EOS5 file     
    2b. Navigate the HDF-EOS5 file   
3. **Georeferencing**    

4. **Identify the Science Datasets (SDS) in the HDF-EOS5 file and SDS Metadata**      

5. **Visualize and Process VIIRS SDS - VNP09A1 Example**    
    5a.Extract the data for each SDS and apply the scale factor      
    5b. Create an RGB array         
    5c. Specify the fill values        
    5d. Visualize the RGB image            
    5e. Calculate NDVI            
    5f. Visualize the NDVI array            
6. **Create GeoTIFF outputs**      

***
## Before Starting this Tutorial:
### Dependencies:
- This tutorial was tested using Python 3.7.6.  
- A [NASA Earthdata Login](https://urs.earthdata.nasa.gov/) account is required to download the data used in this tutorial. You can create an account at the link provided.  
- Libraries:
  + `h5py`
  + `numpy`
  + `gdal`    
  + `matplotlib`  

### Python Environment Setup
#### 1. It is recommended to use [Conda](https://conda.io/docs/), an environment manager, to set up a compatible Python environment. Download Conda for your OS here: https://www.anaconda.com/download/. Once you have Conda installed, Follow the instructions below to successfully setup a Python environment on Windows, MacOS, or Linux.
#### 2. Setup
> 1.  Open a new command line interface (MacOS/Linux: Terminal, Windows: Command Prompt) and type: `conda create -n viirsprocessing -c conda-forge --yes python=3.7 h5py numpy gdal matplotlib`    
> TIP: Getting an error from the command line saying 'Conda is not an executable command' or something of that nature? Try re-opening a new terminal/Command Prompt.
> 2. Navigate to the directory where you downloaded the jupyter notebook
> 3. Activate VIIRS Python environment (created in step 1) in the Command Prompt/Terminal  
  > Type:  Windows: `activate viirsprocessing` or MacOS: `source activate viirsprocessing`    
> TIP: Having trouble activating your environment, or loading specific packages once you have activated your environment? Try the following:
  > Type: 'conda update conda'    
[Additional information](https://conda.io/docs/user-guide/tasks/manage-environments.html) on setting up and managing Conda environments.
***
### Data:
To use this tutorial, __start__ by downloading VIIRS Surface Reflectance data. VIIRS datasets can be downloaded from the [LP DAAC Data Pool](https://e4ftl01.cr.usgs.gov/VIIRS/) or via [NASA Earthdata Search](https://search.earthdata.nasa.gov/search). This tutorial uses a dataset from the [VNP09A1 product](https://doi.org/10.5067/VIIRS/VNP09A1.001) on March 13th, 2012 for tile h10v06. Use this link to download the file directly from the LP DAAC Data Pool: (https://e4ftl01.cr.usgs.gov/VIIRS/VNP09A1.001/2012.03.13/VNP09A1.A2012073.h10v06.001.2016297035634.h5).
Change the __inDir__ variable below to the path to the directory where your data is stored (e.g., C:/Data/VIIRS/VNP09A1) and begin working through each line in the notebook.
This tutorial was specifically developed for NASA VIIRS Surface Reflectance HDF-EOS5 files and should only be used for the data products including [VNP09A1](https://doi.org/10.5067/VIIRS/VNP09A1.001), [VNP09GA](https://doi.org/10.5067/VIIRS/VNP09GA.001), [VNP09H1](https://doi.org/10.5067/VIIRS/VNP09H1.001), and [VNP09CMG](https://doi.org/10.5067/VIIRS/VNP09CMG.001).
 ***