import numpy as np
import pandas as pd
import fklab.utilities.data

info = dict(version=0.1, tags=["session"])


def analyze(context, session, statistic="median"):
    """Extract velocity data for different types of trials

    Parameters
    ----------
    context : fklab.analysis.Context

    Returns
    -------
    None
    """

    func_map = {"mean": np.mean, "median": np.median}
    stimFileAnalysisResult = (
        context.analysis[f"stimFileAnalysis/session={session}"].get().result
    )
    stimFileAnalysisInfo = (
        context.analysis[f"stimFileAnalysis/session={session}"].get().info
    )

    frameRate = stimFileAnalysisInfo["analyze"]["parameters"]["frameRate"]
    secondsBefore = stimFileAnalysisInfo["analyze"]["parameters"]["secondsBefore"]
    secondsAfter = stimFileAnalysisInfo["analyze"]["parameters"]["secondsAfter"]

    behaviorData = stimFileAnalysisResult["behaviorData"]
    rewardedTrials = stimFileAnalysisResult["rewardedTrials"]
    nonRewardedTrials = stimFileAnalysisResult["nonRewardedTrials"]
    nonValidTrials = stimFileAnalysisResult["nonValidTrials"]

    movement = np.linalg.norm(
        behaviorData[1:, :, :], axis=0
    )  # size of the total movement vector (cm/s)

    # Calculate average speed in selected timewindows for different categories
    nSubSessions = int(stimFileAnalysisResult["nSubsessions"][()])
    nTrialsPerSubsession = int(stimFileAnalysisResult["nTrialsPerSubsession"][()])
    trialCategories = ["rewarded", "unrewarded"] + [
        f"subsession{i+1}" for i in np.arange(0, nSubSessions)
    ]
    trialCategoriesIndices = [rewardedTrials, nonRewardedTrials] + [
        np.arange(0, nTrialsPerSubsession + i * nTrialsPerSubsession)
        for i in np.arange(0, nSubSessions)
    ]
    # exclued invalid trials:
    for i in range(len(trialCategoriesIndices)):
        trialCategoriesIndices[i] = [
            t for t in trialCategoriesIndices[i] if t not in nonValidTrials
        ]
    timeWindows = ["baseline", "3sPreStim", "stim", "3sPostStim", "aftermath"]
    timeWindowsSeconds = [
        [0, secondsBefore * frameRate],
        [3 * frameRate, secondsBefore * frameRate],
        [secondsBefore * frameRate, (secondsBefore + 3) * frameRate],
        [(secondsBefore + 3) * frameRate, (secondsBefore + 6) * frameRate],
        [(secondsBefore + 3) * frameRate, None],  # None represents slicing to the end
    ]
    avSpeedT = {}
    avMovementT = {}
    avSpeed = {}
    avMovement = {}
    for timeWindow, t in zip(timeWindows, timeWindowsSeconds):
        avSpeedT[timeWindow] = {}
        avMovementT[timeWindow] = {}
        avSpeed[timeWindow] = {}
        avMovement[timeWindow] = {}
        for cat, trialIdx in zip(trialCategories, trialCategoriesIndices):
            avSpeedT[timeWindow][cat] = func_map[statistic](
                np.abs(behaviorData[1, t[0] : t[1], trialIdx]), axis=0
            )  # only considering forward movement
            avMovementT[timeWindow][cat] = func_map[statistic](
                movement[t[0] : t[1], trialIdx], axis=0
            )
            avSpeed[timeWindow][cat] = func_map[statistic](avSpeedT[timeWindow][cat])
            avMovement[timeWindow][cat] = func_map[statistic](
                avMovementT[timeWindow][cat]
            )
    data = {
        "sessionType": stimFileAnalysisResult["sessionType"].encode(),
        "averageSpeedPerTrial": avSpeedT,
        "averageMovementPerTrial": avMovementT,
        "averageSpeed": avSpeed,
        "averageMovement": avMovement,
    }
    fklab.utilities.data.map_to_hdf5(context.result, data)


def visualise(context, session):
    import seaborn as sns

    speed = context.result["averageSpeedPerTrial"]
    movement = context.result["averageMovementPerTrial"]

    rows = []

    for timeWindow in speed:
        for cat in speed[timeWindow]:
            # Assume the arrays are 1D: one value per subject/trial
            for i, (speed_val, movement_val) in enumerate(
                zip(speed[timeWindow][cat], movement[timeWindow][cat])
            ):
                rows.append(
                    {
                        "timeWindow": timeWindow,
                        "trialCategory": cat,
                        "median speed (cm/s)": speed_val,
                        "median movement (cm/s)": movement_val,
                    }
                )

    # Convert to DataFrame
    df_long = pd.DataFrame(rows)

    fig1, ax1 = plt.subplots()
    sns.stripplot(
        x="timeWindow",
        y="median speed (cm/s)",
        hue="trialCategory",
        data=df_long[df_long["trialCategory"].isin(["rewarded", "unrewarded"])],
        legend=False,
        alpha=0.5,
        ax=ax1,
    )
    sns.boxplot(
        x="timeWindow",
        y="median speed (cm/s)",
        hue="trialCategory",
        data=df_long[df_long["trialCategory"].isin(["rewarded", "unrewarded"])],
        ax=ax1,
    )

    fig2, ax2 = plt.subplots()
    sns.stripplot(
        x="timeWindow",
        y="median speed (cm/s)",
        hue="trialCategory",
        data=df_long[df_long["trialCategory"].isin(["rewarded", "unrewarded"])],
        legend=False,
        alpha=0.5,
        ax=ax2,
    )
    sns.boxplot(
        x="timeWindow",
        y="median speed (cm/s)",
        hue="trialCategory",
        data=df_long[df_long["trialCategory"].isin(["rewarded", "unrewarded"])],
        ax=ax2,
    )

    context.io.save_fig(
        f"speed_{context.result['sessionType'][()].decode()}.png",
        fig1,
        dpi=dpi,
    )
    context.io.save_fig(
        f"movement_{context.result['sessionType'][()].decode()}.png",
        fig2,
        dpi=dpi,
    )
