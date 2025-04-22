# info = dict(version=0.1, tags=["session"])


def analyze(context, session, sessionTypes=None, sessions=None):
    """Extract behavior and lick data aligned to stimulation timestamps.

    Parameters
    ----------
    context : fklab.analysis.Context

    Returns
    -------
    None
    """
    print(context.result)
