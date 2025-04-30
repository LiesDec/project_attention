# Project fUSi attention
TBD
## Behavioral setup
To run this experiement all the seperate components need to be setup correctly. The figure below shows a schematic overview of all required components and how they should be connected to eachother.

![Figure 1: schematic overview of experimental setup]()

### Extra info setup

TBD

## Workflow
### 1. Store data
#### 1.1 Folder structure
TBD

##### 1.1.1 Raw data

TBD

### 2. Set up analysis environment
#### 2.1 Add all repositories to python path
Installing on a new computer
a) Set up the conda environment

      conda env create -f environment_droplet.yaml

b) clone both project_attention.git and analysis_context.git 

    git clone  https://link/to/git/repository

c) add both repositories to python path
    
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

### 3. Data analysis
All scripst for this project are saved under ***project_attention/attentionAnalyses/***.  
To run an analysis on a set of sessions you can use the following 

      python run_analyses.py 

checkout the help function (-h) to know how to select the analyses, mouseIDs or sessions 
