info = dict(version=0.1, tags=["session"])


def analyze(context, session,):
    """Extract velocity data for different types of trials

    Parameters
    ----------
    context : fklab.analysis.Context

    Returns
    -------
    None
    """

    stimFileAnalysisResult = mouse_context.analysis[f".stimFileAnalysis/session={session}"].get().result

    frameRate = stimFileAnalysis['analyze']['parameters']['frameRate']
    secondsBefore = stimFileAnalysis['analyze']['parameters']['secondsBefore']
    secondsAfter = stimFileAnalysis['analyze']['parameters']['secondsAfter']

    behaviorData = stimFileAnalysisResult['behaviorData']
    rewardedTrials = stimFileAnalysisResult['rewardedTrials']
    nonRewardedTrials = stimFileAnalysisResult['nonRewardedTrials']
    nonValidTrials = stimFileAnalysisResult['nonValidTrials']

    #Calculate average speed in selected timewindows for different categories
    trialCategories = ['rewarded', 'unrewarded'] + [f'subsession{i+1}' for i in range(stimFileAnalysisResult['nSubsessions'][()])]
    trialCategoriesIndices = [rewardedTrials, nonRewardedTrials, np.arange(0,int(stimFileAnalysisResult['nTrialsPerSubsession'][()]))+i*int(stimFileAnalysisResult['nTrialsPerSubsession'][()]) for i in np.arange(0,stimFileAnalysisResult['nSubsessions'][()])]]
    for cat in trialCategories:
        #average speed in Baseline [-secondsBefore; stimulusonset]





