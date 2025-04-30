import pathlib

import fklab.analysis.automation as analysis
import h5py
import numpy as np
import pandas as pd
import csv
import os


def create_analysis_context(path):
    path = pathlib.Path(path)

    if not path.exists():
        # create path (and parent paths)
        path.mkdir(parents=True, exist_ok=True)
    # elif not path.is_dir() or len(list(path.iterdir())) > 0:
    #     raise IOError("Path is not an empty directory.")

    # set up default config
    config = analysis.configuration()

    # create context object
    context = analysis.AnalysisContext(path, package="attentionAnalyses")

    context.save_config(target="local", exclude=["datasources"])

    # create subject rule
    # relative path for analyses: subjects/<subjectID>
    # relative path for raw data source: <subjectID>
    # subjectID follows pattern: {initials}{id}
    # where {initials} is composed of 2 or 3 letters (lower or upper case),
    # or {initials} is a letter-number-letter combination
    # and {id} is one or more numbers
    # examples: fk0001, abc2, Az99999, S5E001
    context.rules["experiment"] = analysis.GroupRule(
        "experiment",
        pattern="\d{5}",  # todo:change!!!!
        datasources={"raw": "."},
    )

    # create session rule
    # relative path for analyses: sessions/<sessionID>
    # relative path for raw data source: <sessionID>
    # sessionID follows pattern: {date}_{time}
    # where {date} follows pattern: YYYY-MM-DD (i.e. year, month and day in numbers)
    # and time follows pattern: HH-MM-SS (i.e. hour, minutes, seconds in numbers)
    # examples: 2017-08-03_12-14-01
    context.rules["experiment/type"] = analysis.GroupRule(
        "type",
        pattern="(headfixed|behavior)",
        datasources={"raw": "."},
    )

    context.rules["experiment/type/mouseID"] = analysis.GroupRule(
        "mouseID",
        pattern="[mM]\d{2}",
        datasources={"raw": "."},
    )

    # create rule for session info.yaml file in raw data source
    # context.rules["subject/session/info"] = analysis.AliasRule(
    #     "info.yaml", source="raw"
    # )

    # create rule for *.ncs files in raw data source
    # file names follow pattern: CSC_TT{tt}_{channel}.ncs
    # where {tt} is tetrode number and {channel} is channel number
    # examples: CSC_TT1_1.ncs
    # context.rules["subject/session/recording/csc"] = analysis.PatternRule(
    #     ".",
    #     glob="*.ncs",
    #     pattern="CSC_TT(?P<tt>[0-9]{1,2})_(?P<channel>[0-9]).ncs",
    #     kind="file",
    #     source="raw",
    # )

    # create rule for *.ntt files in raw data source
    # file names follow pattern: TT{tt}.ntt
    # where {tt} is tetrode number
    # examples: TT1.ntt
    # context.rules["subject/session/tt"] = analysis.PatternRule(
    #     ".", glob="*.ntt", pattern="TT(?P<tt>[0-9]{1,2}).ntt", kind="file", source="raw"
    # )

    # # create rule for *.nvt files in raw data source
    # context.rules["subject/session/tracker"] = analysis.PatternRule(
    #     ".", glob="*.nvt", pattern=None, kind="file", source="raw"
    # )

    # # create rule for *.nev file in raw data source
    # context.rules["subject/session/events"] = analysis.AliasRule(
    #     "Events.nev", source="raw"
    # )

    # # create recording rule
    # # this is very similar to the sessions rule
    # context.rules["subject/session/recording"] = analysis.GroupRule(
    #     "recordings",
    #     pattern="(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})_(?P<time>[0-9]{2}-[0-9]{2}-[0-9]{2})",
    #     datasources={"raw": ".", "cache": "."},
    # )

    # # create rule for info.yaml file in recording
    # context.rules["subject/session/recording/info"] = analysis.AliasRule(
    #     "info.yaml", source="raw"
    # )

    # # create rule for *.ncs files in recording
    # context.rules["subject/session/recording/csc"] = analysis.PatternRule(
    #     ".",
    #     glob="*.ncs",
    #     pattern="CSC_TT(?P<tt>[0-9]{1,2})_(?P<channel>[0-9]).ncs",
    #     kind="file",
    #     source="raw",
    # )

    # # create rule for *.ntt files in recording
    # context.rules["subject/session/recording/tt"] = analysis.PatternRule(
    #     ".", glob="*.ntt", pattern="TT(?P<tt>[0-9]{1,2}).ntt", kind="file", source="raw"
    # )

    # # create rule for *.nvt files in recording
    # context.rules["subject/session/recording/tracker"] = analysis.PatternRule(
    #     ".", glob="*.nvt", pattern=None, kind="file", source="raw"
    # )

    # # create rule for *.nev file in recording
    # context.rules["subject/session/recording/events"] = analysis.AliasRule(
    #     "Events.nev", source="raw"
    # )

    context.save_rules()

    return context


def configure_analysis_context(path, datasources):
    datasources = dict(datasources)

    if not "raw" in datasources or not "pre" in datasources:
        raise ValueError("expecting at least 'pre' and 'raw' data sources")

    context = analysis.AnalysisContext(path)

    context.config.datasources = datasources
    context.save_config(target="user", include=["datasources"])


def find_sessionType(matData):
    """
    Determine the behavioral session type from a dictionary of MATLAB-loaded parameters.

    Parameters
    ----------
    matData : dict
        A dictionary containing session metadata loaded from a .mat or HDF5 file.
        Expected keys:
            - 'StimulusContrast' (float or int)
            - 'locationMode' (str)
            - 'stimulusType' (str)
            - 'StimulusLocation' (list or iterable of ints)
            - 'RewardMode' (int)

    Returns
    -------
    str
        A string label describing the session type.
        Examples: 'Baseline', 'Training', 'SpatialTask_30', 'SQR08_100L', etc.

    Notes
    -----
    - Session types are determined based on combinations of contrast level, stimulus type,
      location mode, reward mode, and stimulus location.
    - This function is intended for behavioral or perceptual task categorization.
    """

    contrast_dict = {
        100: "100",
        25.0: "30",
        22.5: "15",
        21.5: "09",
        20.75: "05",
        20.8: "05",  # Allowing for small numeric variation
    }

    stimType_dict = {
        "square": "SQR08_100LR",
        "gabor": "GAB08_100LR",
    }

    # Extract variables from dictionary
    stimulusContrast = matData["StimulusContrast"]
    locationMode = matData["locationMode"]
    stimulusType = matData["stimulusType"]
    stimulusLocation = matData["StimulusLocation"]
    rewardMode = matData["RewardMode"]

    # Determine session type based on conditions
    if stimulusContrast == 20:
        sessionType = "Baseline"

    elif locationMode == "right":
        sessionType = "Training"

    elif locationMode == "oppositeSides":
        sessionType = stimType_dict[stimulusType]

    elif locationMode == "left":
        sessionType = "SQR08_100L"

    elif locationMode == "oppositeSidesRightRewarded":
        if rewardMode == 0:
            sessionType = "SpatialTaskNoReward_" + contrast_dict[stimulusContrast]
        elif any(x in stimulusLocation for x in [227, 1221]):
            sessionType = "SpatialTask2_" + contrast_dict[stimulusContrast]
        else:
            sessionType = "SpatialTask_" + contrast_dict[stimulusContrast]

    elif locationMode == "oppositeSidesRightRewarded4Locations":
        sessionType = "SpatialTask4P_" + contrast_dict[stimulusContrast]

    else:
        raise ValueError(f"Unknown locationMode: {locationMode}")

    return sessionType


def read_h5py_variable(dataset):
    """
    Recursively read and convert a dataset or group from an HDF5 file into native Python types.

    Supports strings (including encoded bytes), numbers, arrays, and nested groups.

    Parameters
    ----------
    dataset : h5py.Dataset or h5py.Group
        An HDF5 dataset or group, typically obtained via h5py.File['key'].

    Returns
    -------
    object
        A native Python object:
        - str for strings
        - float/int for scalars
        - numpy.ndarray for arrays
        - dict for groups
        - None if the type is not recognized
    """

    if isinstance(dataset, h5py.Dataset):
        # Handle byte strings or objects (common in MATLAB-exported HDF5)
        if dataset.dtype.kind in {"S", "O"}:
            try:
                return dataset[()].decode("utf-8")
            except Exception:
                return "".join(
                    x.decode("utf-8") if isinstance(x, bytes) else str(x)
                    for x in dataset[:]
                )

        # Handle Unicode strings
        elif dataset.dtype.kind == "U":
            return "".join(dataset[:]) if dataset.shape else str(dataset[()])

        # Handle datasets encoded as ASCII character arrays (e.g., uint16)
        elif dataset.dtype == "uint16" and len(dataset.shape) > 1:
            try:
                return "".join([chr(x[0]) for x in dataset[:]])
            except Exception:
                pass

        # Handle singleton values
        elif dataset.shape == (1,):
            return np.array(dataset[0]).flatten()

        # Default: numeric arrays
        else:
            d = np.array(dataset[()]).flatten()
            return d[0] if d.size == 1 else d

    elif isinstance(dataset, h5py.Group):
        # Recursively read all keys in the group
        return {key: read_h5py_variable(dataset[key]) for key in dataset.keys()}

    return None


def dict_to_csv(context, data, filename="output.csv"):
    """
    Converts a dictionary to a CSV file and saves it

    Parameters
    ----------
    context : dict-like
        A structured context object (e.g., from DataJoint or a custom class)
        providing access to mouse-specific metadata and data paths.

    data (dict): The dictionary to convert.
                Format: {session: {property1: value1, property2: value2, ...}, ...}

    filename (str): The name of the output CSV file.

    Return
    ------
    None
    """
    try:
        # Open a CSV file for writing
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)

            # Get the header from the first dictionary entry
            headers = ["session"] + list(next(iter(data.values())).keys())
            writer.writerow(headers)

            # Write each session and its properties
            for session, properties in data.items():
                row = [session] + list(properties.values())
                writer.writerow(row)

        context.log.info(
            f"CSV file '{os.path.basename(filename)}' created successfully!"
        )

    except Exception as e:
        context.log.exception(f"An error occurred: {e}")


def get_files_path(
    context, mouseIDs=None, sessionTypes=None, fileTypes=None, OS="mac", root=""
):
    """
    Collects and formats the stimulus file paths for selected mice and session types.

    Parameters
    ----------
    context : dict-like
        A structured context object (e.g., from DataJoint or a custom class)
        providing access to mouse-specific metadata and data paths.

    mouseIDs : list of str, optional
        List of mouse identifiers in the format "experiment/mouseID".
        If None, the default list is taken from `context.config.mouseIDs`.

    sessionTypes : list of str, optional
        Session types to filter the sessions (e.g., ['Baseline', 'Training', 'SQR08_100LR',....]).
        If None, all session types are included.

    fileTypes: list of str, optional
        file types to recover ["StimFilesPath", "TriggerPath", "CamPath", "FusiPath"]
        If None, all file types are included.

    OS : str, optional
        Target operating system format for the output paths.
        Choose 'mac' (default) for Unix-style paths or 'windows' for backslash-separated paths.

    root : str, optional
        Optional prefix to prepend to each path (e.g., network drive or base directory).

    Returns
    -------
    list of str
        A flat list of stimulus file paths in the requested OS format, ready for export or further use.
    """

    if mouseIDs is None:
        mouseIDs = context.config.mouseIDs

    all_paths = []

    for mouseID in mouseIDs:
        # Split into experiment and mouse ID
        experiment, mID = mouseID.split("/")

        # Navigate to the correct context
        mouse_path = f"experiment/{experiment}/type/headfixed/mouseID/{mID}"
        mouse_context = context[mouse_path]

        # Read overview file
        overview_file = mouse_context.datasources["raw"].joinpath(
            f"overviewSessions{mID}.csv"
        )
        overview = pd.read_csv(overview_file)

        # Filter sessions by type if needed
        if sessionTypes is not None:
            overview = overview[overview["sessionType"].isin(sessionTypes)]

        if fileTypes is None:
            fileTypes = ["StimFilesPath", "TriggerPath", "CamPath", "FusiPath"]

        # Prepend root if needed, and store
        for fileType in fileTypes:
            mouse_paths = [
                root + p for p in overview[fileType][~overview[fileType].isna()]
            ]
            all_paths.extend(mouse_paths)

    # Format for OS
    if OS == "windows":
        all_paths = [p.replace("/", "\\") for p in all_paths]

    return all_paths
