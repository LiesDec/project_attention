import os
import yaml
import argparse
import warnings
from pathlib import Path
import matplotlib

import fklab.analysis.core.context as con
import pandas as pd


def main():
    parser = argparse.ArgumentParser(
        description="create info.yaml file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--path",
        type=str,
        default="/Volumes/nerfceph/farrowlabwip2024/",
        help="Root path to farrowlapwip2024",
    )

    parser.add_argument(
        "--mouseIDs",
        type=str,
        nargs="*",
        default=["all"],
        help="MouseID to analyze eg 02203/m02",
    )
    parser.add_argument(
        "--sessionTypes",
        type=str,
        nargs="*",
        default=["all"],
        help="Sessiontypes to analyze",
    )
    parser.add_argument(
        "--sessions",
        type=str,
        nargs="*",
        default=["all"],
        help="Sessions to analyze",
    )

    parser.add_argument(
        "--analysis",
        type=str,
        nargs="*",
        default=["all"],
        help="analyses to run, options: [create_overview, stimFileAnalysis, velocityAnalysis] ",
    )

    parser.add_argument(
        "--ifNotSince",
        type=str,
        default=None,
        help='str or datetime, optional if no previous analysis had been performed since this date/time, then run now, otherwise skip. If given as a string it should represent a valid date, time or date/time that can be parsed by `dateutil`. For example: "2017-08-01" (time is 00:00:00), "9:14" (date is today) or "09-03 10:56" (current year).',
    )

    args = parser.parse_args()
    # warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)

    # get analysis context
    context = con.AnalysisContext(args.path + "Data/")
    # filter mouseIDs
    if "all" in args.mouseIDs:
        mouseIDs = context.config.mouseIDs
    else:
        mouseIDs = args.mouseIDs
    # Iterate through each mouse ID and run the command
    for mouseID in mouseIDs:
        # Extract the experiment number and mouse identifier from the mouseID
        experiment, mID = mouseID.split("/")

        # Construct the session path dynamically
        mouse_path = f"experiment/{experiment}/type/headfixed/mouseID/{mID}"
        mouse_context = context[mouse_path]

        if "create_overview" in args.analysis:
            # Run the visualize command
            mouse_context.run(".create_overview")
        # Find right sessions to iterate over
        overview_file = mouse_context.datasources["raw"].joinpath(
            f"overviewSessions{mID}.csv"
        )
        overview = pd.read_csv(overview_file)
        if "all" in args.sessionTypes:
            sessionTypes = overview["sessionType"].unique()
        else:
            sessionTypes = args.sessionTypes
        if "all" in args.sessions:
            sessions = overview[overview["sessionType"].isin(sessionTypes)][
                "session"
            ].unique()
        else:
            sessions = args.sessions

        for session in sessions:
            if overview.loc[overview["session"] == session, "include"].values[0]:
                if "stimFileAnalysis" in args.analysis:
                    mouse_context.run(
                        ".stimFileAnalysis",
                        parameters=dict(session=session),
                        if_not_since=args.ifNotSince,
                    )
                if "velocityAnalysis" in args.analysis:
                    mouse_context.run(
                        ".velocityAnalysis",
                        parameters=dict(session=session),
                        if_not_since=args.ifNotSince,
                    )
                if "dlcAnalysis" in args.analysis:
                    mouse_context.run(
                        ".dlcAnalysis",
                        parameters=dict(session=session),
                        if_not_since=args.ifNotSince,
                    )
            else:
                mouse_context.log.info(f"session {session} not inlcuded in dataset")


if __name__ == "__main__":
    main()
