#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 16:15:49 2023

@author: liesdeceuninck
"""

"""
=========================================================================================================
test analysis: mod:`attentionAnalyses.test`
=========================================================================================================

.. currentmodule:: attentionAnalyses.test

This is an analysis to test the context functionning.

.. autosummary::
        :toctree: generated/

        analyze


"""

import fklab.utilities.data
import os
import re
import h5py
import numpy as np
from .utilities import read_h5py_variable
from .utilities import find_sessionType
from .utilities import dict_to_csv


# info = dict(version=0.1, tags=["phase"])
info = dict(version=0.1)


def analyze(
    context,
):
    """Create and save time alignment object

    Parameters
    ----------
    epoch : string

    Dependencies
    ------------
    None

    Returns
    -------

    """
    # ----------------------------------------------------------
    # read data
    # ----------------------------------------------------------

    mouseID = context.levels["mouseID"]
    stimFilesMainFolder = context.datasources["raw"].joinpath("raw/StimFiles/")

    # ----------------------------------------------------------
    # select the correct sessions
    # ----------------------------------------------------------

    session_data = {}
    for root, dirs, files in os.walk(stimFilesMainFolder):
        for dir_name in dirs:
            # Extract session name from the folder name
            match = re.search(r"(\d{6}_\d{4})$", dir_name)
            if match:
                session_name = match.group(0)
                subfolder_path = os.path.join(root, dir_name)

                # Find a stim file in the subfolder
                stimFiles = [
                    f for f in os.listdir(subfolder_path) if f.endswith(".mat")
                ]
                if stimFiles:
                    stimPath = os.path.join(subfolder_path, stimFiles[0])
                    try:
                        with h5py.File(stimPath, "r") as file:
                            stimData = {
                                key: read_h5py_variable(file[key])
                                for key in [
                                    "StimulusContrast",
                                    "RewardMode",
                                    "locationMode",
                                    "stimulusType",
                                ]
                            }
                            stimData["StimulusLocation"] = np.unique(
                                file["stimLocationHistoryPX"][:, 0]
                            )
                    except Exception as e:
                        context.log.error(f"Error reading {stimPath}: {e}")

                    # Save all data to dictionary
                    session_data[session_name] = stimData
                    session_data[session_name]["sessionType"] = find_sessionType(
                        session_data[session_name]
                    )

                    # Store relative paths (to context.datasources['raw'])
                    # Convert the path to a string and find the position of "Data"
                    path_str = str(stimPath)
                    start_index = path_str.find("Data")
                    end_index = path_str.find("StimFiles")

                    session_data[session_name]["StimFilesPath"] = path_str[start_index:]
                    session_data[session_name]["TriggerPath"] = (
                        path_str[start_index:end_index] + f"Triggers/{dir_name}.npy"
                    )
                    camFolderPath = path_str[:end_index] + f"Cam/{dir_name}"

                    camFiles = [
                        f for f in os.listdir(camFolderPath) if f.endswith(".mp4")
                    ]
                    if len(camFiles) == 0:
                        session_data[session_name]["CamPath"] = "None"
                    else:
                        session_data[session_name]["CamPath"] = os.path.join(
                            camFolderPath[start_index:], camFiles[0]
                        )
                    session_data[session_name]["FusiPath"] = (
                        path_str[start_index:end_index]
                        + f"fUSi/{session_data[session_name]['sessionType']}/{dir_name}"
                    )

                    context.log.info(f"Loaded session {session_name} from {mouseID}")

    # -----------------------------------------------------------------------------
    # Save data to csv
    # -----------------------------------------------------------------------------
    # fklab.utilities.data.map_to_hdf5(context.result, data)
    dict_to_csv(
        context,
        session_data,
        filename=context.datasources["raw"].joinpath(f"overviewSessions{mouseID}.csv"),
    )


def visualize(context, dpi=300):
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import random
    from datetime import datetime
    import seaborn as sns
    from attentionAnalyses import plot_styles_and_colors

    # Read the CSV file
    mouseID = context.levels["mouseID"]
    df = pd.read_csv(
        context.datasources["raw"].joinpath(f"overviewSessions{mouseID}.csv")
    )

    # Convert session date strings to datetime objects
    df["datetime"] = df["session"].apply(
        lambda x: datetime.strptime(x, "%y%m%d_%H%M").date()
    )

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Generate a unique color for each session name
    palette = sns.color_palette("colorblind", n_colors=15)
    unique_sessions = df["sessionType"].unique()

    # Define the order of the categories

    # Convert the 'sessionType' column to a categorical type with a specific order
    df["sessionType"] = pd.Categorical(
        df["sessionType"], categories=context.config.sessionType_order, ordered=True
    )

    # Sort by the categorical column
    df = df.sort_values(by="sessionType")

    # Plot each session as a rectangle
    for idx, row in df.iterrows():
        start_date = row["datetime"]

        ax.barh(
            row["sessionType"],
            width=0.9,
            left=start_date,
            color=row["sessionType"],
            edgecolor="black",
        )

    # Format x-axis as dates
    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))

    # Rotate x-tick labels
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_size(8)

    # Add labels and title
    ax.set_xlabel("Date")
    ax.set_ylabel("Session Name")
    ax.set_title("Session Timeline")

    plt.tight_layout()

    context.io.save_fig(
        f"overview_{mouseID}.png",
        fig,
        dpi=dpi,
        overwrite=True,
    )
