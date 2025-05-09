# import datetime
import attentionAnalyses.utilities as ac

path_analysis = "/mnt/farrowlab/farrowlabwip2024/Data/"
path_preprocess = "/mnt/farrowlab/farrowlabwip2024/Data/"
path_raw = "/mnt/farrowlab/farrowlabwip2024/Data/"

# The following 2 lines will create analysis folder and save path to .config/fklab.analysis. When it is set up, no need to rerunthemt again.
ac.create_analysis_context(path_analysis)
ac.configure_analysis_context(path_analysis, {"raw": path_raw, "pre": path_preprocess} )
