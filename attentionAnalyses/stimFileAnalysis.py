import numpy as np
import pandas as pd
import mat73
from pathlib import Path
import fklab.utilities.data
import logging

info = dict(version=0.1, tags=["session"])


def convert_to_int(arr):
    if isinstance(arr, list):  # If it's a list, process each element recursively
        return [convert_to_int(item) for item in arr]
    elif isinstance(arr, str):  # If it's a string, try converting it
        return int(arr)
    elif arr is None:  # If it's a string, try converting it
        return None
    else:  # If it's already another type, return as is
        return arr


def analyze(
    context,
    session,
    frameRate=66,
    secondsBefore=10,
    secondsAfter=9,
):
    """
    Extract behavior and lick data aligned to stimulation timestamps.

    This function loads camera tracking data, trigger times, and lick data
    from a behavioral experiment, aligns them to the stimulation onset in each trial,
    and saves the segmented trial-wise data for further analysis.

    Parameters
    ----------
    context : fklab.analysis.Context
        Analysis context containing data sources, logging, and result saving utilities.
    session : str
        Session identifier to look up the relevant data in the overview file.
    frameRate : int, optional
        Number of frames per second in the camera data (default is 66).
    secondsBefore : int, optional
        Time window (in seconds) before stimulation to include (default is 10).
    secondsAfter : int, optional
        Time window (in seconds) after stimulation to include (default is 9).

    Returns
    -------
    None
        The aligned data is saved to `context.result` using HDF5 format.

    """

    # Read overview file
    # context.log.info(f"session : {session}")
    mID = context.levels["mouseID"]
    overview_file = context.datasources["raw"].joinpath(f"overviewSessions{mID}.csv")
    overview = pd.read_csv(overview_file)

    # Load stim and trigger file
    parts = context.datasources["raw"].parts
    index = parts.index("Data")
    root_path = Path(*parts[:index])

    # Save original logging level
    logger = logging.getLogger()
    previous_level = logger.level

    # Suppress error-level logs (and below)
    logger.setLevel(logging.CRITICAL + 1)
    stimData = mat73.loadmat(
        Path.joinpath(
            root_path,
            overview[overview["session"] == session]["StimFilesPath"].values[0],
        )
    )
    # Restore original logging level
    logger.setLevel(previous_level)
    triggers = np.load(
        Path.joinpath(
            root_path, overview[overview["session"] == session]["TriggerPath"].values[0]
        ),
        allow_pickle=True,
    )
    trigT = triggers[0]

    # Read ball camera data
    ballCamData = np.array(stimData["BallCamData"])
    time = ballCamData[:, 0] / 1000  # ms to s

    # Align camera data to trigger length #SOL1
    diff = len(time) - len(trigT)
    if diff > 0:
        forward = ballCamData[:, 4][:-diff]
        turn = ballCamData[:, 5][:-diff]
        lateral = ballCamData[:, 6][:-diff]
    else:
        forward = ballCamData[:, 4]
        turn = ballCamData[:, 5]
        lateral = ballCamData[:, 6]

    # Timing info
    stimStartSec = (
        stimData["options"]["Trialtsecbegin"] - stimData["options"]["tsecbegin"][0]
    )  # start of the stimulation with respect to start of the first trial

    stimStartSecPerTrial = (
        stimData["options"]["Trialtsecbegin"] - stimData["options"]["tsecbegin"]
    )  # start of the stimulation (s) with respect to start of the each respective trial

    # filter out trials where ballcamdata was not recorded #SOL2
    noBallCamDataTrials = stimStartSec < time[-1]
    stimStartSec = stimStartSec[noBallCamDataTrials]
    stimStartSecPerTrial = stimStartSecPerTrial[: len(stimStartSec)]

    # Check if redFrames has more than one dimension, and extract accordingly
    redFrames = stimData["redFrames"]
    if len(np.shape(redFrames)) > 1:
        redFrames = redFrames[
            0
        ]  # Take the first dimension if it's multi-dimensional #SOL3

    # Convert redFrames to integers
    redFrames = np.array(
        [int(x) for x in redFrames]
    )  # start of each trial (s) with respect to start of session

    lickData = np.array(
        convert_to_int(stimData["lickData"])
    ).T  # Lick times (s) with respect to start of the session
    if lickData.ndim > 0:
        maxLickInTrial = np.shape(stimData["lickData"])[0]
    else:
        maxLickInTrial = 1
    numTrials = len(stimStartSec)

    # Stim start timestamps in trigger time
    stimStartTrigT = np.array([trigT[np.where(time > s)[0][0]] for s in stimStartSec])

    # Pre-allocate output arrays
    behaviorData = np.full(
        (4, frameRate * (secondsBefore + secondsAfter), numTrials),
        fill_value=np.nan,
    )
    licksDataTrials = np.full((maxLickInTrial, numTrials), fill_value=np.nan)
    trialSegTrigT = []
    nonValidTrials = []
    rewardedTrials = []
    nonRewardedTrials = []

    # Trial loop
    for n, s in enumerate(stimStartTrigT):
        stimStartFrame = np.where(trigT > s)[0][0]
        start = stimStartFrame - frameRate * secondsBefore
        end = stimStartFrame + frameRate * secondsAfter
        if (
            (len(trigT) <= end)
            or (len(trigT) <= start)
            or (trigT[start] < time[0])
            or (trigT[end] > time[-1])
        ):  # SOL4
            context.log.info(f"Trial {n} out of bounds, discardingskipping.")
            nonValidTrials.append(n)
            continue

        # save if trial is rewarded or non-rewarded, otherwise discard
        stimulusLocation = stimData["stimLocationHistoryPX"][n]

        if any(
            (stimulusLocation == sublist).all()
            for sublist in [[475.0, 230.0, 525.0, 280.0], [227.0, 230.0, 277.0, 280.0]]
        ):
            rewardedTrials.append(n)
        elif any(
            (stimulusLocation == sublist).all()
            for sublist in [
                [1035.0, 230.0, 1085.0, 280.0],
                [1221.0, 230.0, 1271.0, 280.0],
            ]
        ):
            nonRewardedTrials.append(n)
        else:
            context.log.info("Stimulation not in valid spot, discarding trial")
            nonValidTrials.append(n)
            continue

        trialSegTrigT.append([trigT[start], trigT[end]])

        for i, b in enumerate([np.array(triggers[0]), forward, turn, lateral]):
            behaviorData[i, :, n] = b[start:end] * frameRate

        # Lick data aligned to stim start
        if (
            isinstance(lickData, np.ndarray)
            and lickData.ndim > 0
            and lickData.shape[0] > n
        ):  # if there ar no licks in leftover trials, lickData doesn't contain 'none' values #SOL5
            lickTrial = np.array(lickData[n, lickData[n] != None])
            lickTimestamps = (lickTrial - redFrames[n]) * 1e-3 - stimStartSecPerTrial[n]
            lickTimestamps = lickTimestamps[
                (lickTimestamps >= -secondsBefore) & (lickTimestamps < secondsAfter)
            ]
            licksDataTrials[: len(lickTimestamps), n] = lickTimestamps
    """
    Save Data (context.result)
    ---------------------------
    The function saves a dictionary with the following keys:

    - "trialSeg" : list of list of float
        Each element is [start_time, end_time] (in seconds) of the aligned trial window
        based on trigger timestamps. Length = number of valid trials.

    - "nonValidTrials" : list of int
        Indices of trials that were skipped due to out-of-bounds timing or errors.

    - "behaviorData" : np.ndarray, shape (4, T, N)
        Trial-aligned behavioral data where:
            - Axis 0 (length 4): signal types
                [0] = trigger signal (s)
                [1] = forward movement (cm/s)
                [2] = side movement (cm/s)
                [3] = headdirection (Yaw (degree/s))
            - Axis 1 (length T): time points per trial (T = frameRate * (secondsBefore + secondsAfter))
            - Axis 2 (length N): number of trials

        Missing/invalid data is filled with NaNs.

    - "lickData" : np.ndarray, shape (maxLicks, N)
        Lick timestamps aligned to stimulation onset for each trial, where:
            - Axis 0: individual lick events (maxLicks = maximum licks in any trial)
            - Axis 1: trial index (N = number of trials)
        Lick times are in seconds relative to stim onset. Invalid/missing entries are NaN.
    """
    data = {
        "sessionType": overview[overview["session"] == session]["sessionType"]
        .values[0]
        .encode(),
        "trialSeg": trialSegTrigT,
        "nonValidTrials": nonValidTrials,
        "behaviorData": behaviorData,
        "lickData": licksDataTrials,
        "nTrialsLostAtEnd": np.sum(noBallCamDataTrials),
    }
    fklab.utilities.data.map_to_hdf5(context.result, data)


def visualize(context, session, dpi=150):
    import seaborn as sns
    import matplotlib.pyplot as plt

    behaviorData = context.result["behaviorData"]
    lickData = context.result["lickData"]

    fig, axs = plt.subplots(
        1, 2, figsize=(12, 5), sharey=True, width_ratios=[1.2, 1], layout="tight"
    )
    sns.heatmap(
        behaviorData[1, :, :].T,
        cmap="RdBu_r",
        xticklabels=False,
        yticklabels=25,
        ax=axs[0],
        cbar_kws={"label": "Velocity (cm/s)"},
    )

    # axs[1].hlines(
    #     y=nvt,
    #     xmin=axs[1].get_xlim()[0],
    #     xmax=axs[1].get_xlim()[1],
    #     color="grey",
    #     linewidth=5 / behaviorData.shape[2],
    # )
    # Set custom x-tick positions
    num_ticks = 5  # Number of ticks to show
    tick_positions = np.arange(0, behaviorData.shape[1], 66)
    tick_labels = np.arange(-10, 9, 1)

    axs[0].set_xticks(tick_positions)  # Set tick positions
    axs[0].set_xticklabels(tick_labels)  # Set labels & rotate

    # Set the x and y labels
    axs[0].set_xlabel("Time (s)")
    axs[1].set_xlabel("Time (s)")
    axs[0].set_ylabel("Trials")

    axs[0].invert_yaxis()
    axs[0].axvline(
        10 * 66,
        color="k",
        linestyle="--",
    )
    axs[0].axvline(
        13 * 66,
        color="k",
        linestyle="--",
    )

    for t in range(lickData.shape[1]):
        if t == 0:
            axs[1].plot(
                lickData[:, t],
                [t] * len(lickData[:, t]),
                "k.",
                markersize=2,
                label="lick",
            )
        axs[1].plot(lickData[:, t], [t] * len(lickData[:, t]), "k.", markersize=2)

    axs[1].set_xlim([-10, 9])
    axs[1].legend()
    # axs[1].set_xticks(np.arange(-10,9,1))
    fig.suptitle(f'session type: {context.result["sessionType"][()].decode()}')

    # plot non-valid trials
    for nvt in context.result["nonValidTrials"]:
        axs[0].fill_between(
            x=[axs[0].get_xlim()[0], axs[0].get_xlim()[1]],
            y1=nvt,
            y2=nvt + 1,
            color="k",
            linewidth=5 / behaviorData.shape[2],
        )
        axs[1].fill_between(
            x=[axs[1].get_xlim()[0], axs[1].get_xlim()[1]],
            y1=nvt,
            y2=nvt + 1,
            color="grey",
            linewidth=5 / behaviorData.shape[2],
        )

    context.io.save_fig(
        f"summary_behavior_{context.result['sessionType'][()].decode()}.png",
        fig,
        dpi=dpi,
    )
