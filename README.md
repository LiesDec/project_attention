# paper-aswr-stm

This project investigates the contribution of hippocampal activity and PFC interaction to short-term memory (stm) using bilateral neuropixel recordings in the hippocampus and optogenetic manipulation in the PFC.  
## Behavioral setup
To run this experiement all the seperate components need to be setup correctly. The figure below shows a schematic overview of all required components and how they should be connected to eachother.

![Figure 1: schematic overview of experimental setup](schema.png)

### Extra info setup

1. 
      - Make sure you have version xxx and install the Neuropix-PXI plugin.
      - the pipeline in open ephys should contain: Neuropix-PXI, record node, LFP viewer (to view signals)
2. 
      - Computer needs to be connected to internet
      - Download the ZQM software [here](https://bitbucket.org/kloostermannerflab/netcomclients/src/master/ZMQRouter/)
3. 
      - Preferably install linux Mint
      - Install [hive](https://bitbucket.org/kloostermannerflab/fklab-controller-lab/src/master/)
      - Install [fklab-python-internal](https://bitbucket.org/kloostermannerflab/fklab-python-internal/src/master/) for tracking app 
      - In Hive use this [config file](https://bitbucket.org/kloostermannerflab/paper-np-optogenetics/src/master/8-maze2PWS.yaml)
4. 
      - Configure as instructed on the [neuropixels website](https://www.neuropixels.org/getting-started) 
5. 
      - Configure as instructed on the cheetah website
      - Create named events for stimulations
      - DO NOT create named events for time pulses
6.    
      - Download the controlling software [here](https://www.mightexsystems.com/product/slc-sa-aa-series-universal-four-channel-led-controllers-with-external-triggers/)
7. 
      - The arduino communicates via USB with Hive input. 
      - Install this programm on it [location_stim.imo](https://bitbucket.org/kloostermannerflab/paper-np-optogenetics/src/master/Location_detection.ino)
      - Change the config file to change the stimulation protocol
8.    
      - Download this programm on the arduino [timesync](https://bitbucket.org/kloostermannerflab/fklab-experiments/src/master/SpikeGLX_Neuralynx_sync/SpikeGLX_Neuralynx_sync.ino)
9. 
      - Wide field camera that needs to be detected by Cheetah.
      - the video data will in this way be synchronised with the timestamps
10. 
      - Raspberry Pi for live tracking with the tracking app
      - configure as instructed on the lab [teams channel](https://teams.microsoft.com/l/entity/com.microsoft.teamspace.tab.wiki/tab::e92d01b2-f405-4f52-83f7-2fde9745857a?context=%7B%22subEntityId%22%3A%22%7B%5C%22pageId%5C%22%3A13%2C%5C%22origin%5C%22%3A2%7D%22%2C%22channelId%22%3A%2219%3Afc29e0a33c724aabb3ae1cf00bd2d6d9%40thread.skype%22%7D&tenantId=a72d5a72-25ee-40f0-9bd1-067cb5b770d4)

## Workflow
### 1. Store data
#### 1.1 Folder structure

To work with an analysis context the project folder should be sturctured as follows:

1. Project folder with folders  
     - data (stores all the recorded data)  
     - analysis (stores result from all the analyses)  
2. Data folder contains the following folders  
     - raw (raw data)  
     - cache  (will be used during the analysis)     
     - preprocess  (will be used during the analysis)  
     - spikesorting (results from the spikesorting)  
3. All data foldesr contains your data in the form of folders per animal, which each consist of 'session' folders, named with the day and hour in the format YYY_MM_DD-hh_mm_ss   

##### 1.1.1 Raw data

Each 'session' folder in raw data contains the recorded data from both open ephys (neural data) and from neuralynx (behavior data) and the meta data containing information about the experiment and the setup.  
        
for example:  

    data/raw/LD47/2021-01-25_14-06-37/  
    
**recorded data**  

	*open ephys  
    
		- Recording node XXX (normally always 102)
			(a new experiment starts when you restart aquisition) 
			- experiment 1   
				(a new recording starts when you restart recording)   
				-recording 1   
                   - continuous
                      - Neuropix-PXI-100.0 ( x hemisphere)
                      - Neuropix-PXI-100.1 (x hemisphere)
                   - events 
                      - Neuropix-PXI-100.0 ( x hemisphere)
                      - Neuropix-PXI-100.1 (x hemisphere)
				- recording ...  
			- experiment ...  
         Note: Normally, you should have 1 recording node (Record Node 102), one experiment (experiment 1) and one recording (recording 1). 
            
	*Neuralynx 
    
		-event.nev (time sync pulses)  
		-VT1.nvt (tracking of LED's)
        -VT1.mpg (video with behavior)  
        -VT1.smi (time subtitles in video)
        -CheetahLogFile.txt (details about recording)
        -DataProcessingErrors.nde (log of potential errors during data aquisition)
        
**meta data**  

- info.yaml   |   *information about the experiment and different epochs (trials and inter_trials). run [this script]() to create an info.yaml template*  
- 8-maze2PWS.yaml   |    *config file used for experimental control in hive, see [this repository](https://bitbucket.org/kloostermannerflab/fklab-controller-lab/src)*  
    

#### 1.2 Back up data to nerf servers
To make sure your data is safe you should store it on the nerf servers. For work in progress data, use the storage server nerffs13. For published data, use the storage server nerfhf01.
Backup your folders ***once a month***. 

To speed up the upload, login via the nerfcluser and use screen.  
The 'screen' command will log you on to a new screen where you can enter the command. ctrl+A+D will log you out of this screen again. To return to the old screen: screen -l [ID number of screen]

   `ssh ratlab@nerfcluster-fs`  
   `screen`  
   
To copy your data use the following command  
`rsync --recursive /mnt/fk-fileserver2/Project_NP_optogenetics /mnt/nerffs13/kloostermanlabwip2020/`  

To list all currently open screens  
` screen -r`  

To open a specific screen  
`screen -r SCREEN_NUMBER`

To quit a specific screen
`screen -X -S SCREEN_NUMBER quit`  

### 2. Set up analysis environment
Follow the instructions written in the fklab documentation to set up your python conda environment. It is recommended to follow the [developer user guide](https://kloostermannerflab.bitbucket.io/set_up/guide_power_user.html).  
Make sure you always run your code in the right conda environment! 
#### 1.1 Add git repository to python path
a) clone this project repository 

    git clone  https://link/to/git/repository

b) add this repository to python path
    
    cd path/to/your/cloned/git/repository
    python setup.py build_ext --inplace
    pip install -e . --no-deps
    
#### 1.2 Create analysis context
To run the code you need to set up an analysis context. To set it up you should run the file `context_config.py`     
      
      cd path/to/your/cloded/git/repository/fklab/papers/np_opto/  
      python context_config.py  
   
It will create analysis folder and save path to ***.config/fklab.analysis***. When it is set up, no need to re-run the file again.

To create an analysis object referencing your analysis context you run:

```python   
   context = analysis.AnalysisContext(path_analysis)
```

### 2. Raw data preprocess 
1. preprocess every session with Localise (to refine the position tracking)  
2. preprocess every session with Amaze by running  

      python run_amaze.py
      
    
### 3. Data analysis
All scripst for this project are saved under ***paper-NP-optogenetics/fklab/analyses***.  
To run an analysis on a set of sessions you should create a local python file that allows you to select the correct analyses and sessions. 

### 4. Implant configuration
<img src="optodrive1.png" alt="drawing" width="200"/>


1. Probe A  
      - right hemisphere  
      - shank 0: posterior, shank 3: anterior  
2. Probe B  
      - Left hemisphere  
      - shank 0: anterior, shank 3: posterior

