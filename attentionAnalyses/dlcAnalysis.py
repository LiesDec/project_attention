import paramiko
from fklab.analysis.core.analysis_io import get_analysis_path
from fklab.analysis.core.analysis_io import get_tag_path
from fklab.analysis.core.analysis_io import get_version_path

info = dict(version=0.1, tags=["session"])


def initialize_client(hostname, username, password):
    # initialize the SSH client
    client = paramiko.SSHClient()
    # add to known hosts
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=hostname, username=username, password=password)
    except:
        print("[!] Cannot connect to the SSH Server")
        exit()
    return client


def execute_commands(client, commands):
    # execute the commands
    for command in commands:
        print("=" * 50, command, "=" * 50)
        stdin, stdout, stderr = client.exec_command(command)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(err)


def analyze(
    context,
    session,
    clusterNode="nerfcluster01",
    clusterUser="liesd-farrowlab",
    clusterPassword="VarcSomnQelu6(",
    root="/mnt/farrowlab/farrowlabwip2024/",
    json_file="/mnt/farrowlab/farrowlabwip2024/User/Lies/DLC/DLC_params_analyse.json",
    out_directory="home/liesd-farrowlab/DLC",
    user_email="deceun56@imec.be",
):
    mID = context.levels["mouseID"]

    # get paths for bashfile
    analysis_path = get_analysis_path(context.datasources["raw"], "run_dlc")
    tag_path, _ = get_tag_path(analysis_path, context.config.tags)

    version_path, version = get_version_path(tag_path, None, action="exist")

    bash_path_local = os.path.join(version_path, "bash.sh")

    bash_path_local_str = str(bash_path_local)
    start_index = bash_path_local_str.find("Data")

    bash_path_nerfcluster = root + bash_path_local_str[start_index:]

    # make session directory to store output dlc
    os.mkdir(os.path.join(out_directory, session))

    # create dlc_analysis json file
    with open(
        os.path.join(root, "User/Lies/DLC/DLC_params_analyse.json"), "r"
    ) as openfile:
        analyseParams = json.load(openfile)
    # find video path
    overview_file = context.datasources["raw"].joinpath(f"overviewSessions{mID}.csv")
    overview = pd.read_csv(overview_file)

    print(overview)
    videoPath = os.path.join(
        root,
        overview[overview["session"] == session]["CamPath"].values[0],
    )
    analyseParams["Videos"] = [videoPath]
    analyseParams["AnalyzeVideo"]["destfolder"] = version_path
    # Serializing json
    with open(os.path.join(version_path, "DLC_params_analyse.json"), "w") as outfile:
        json.dump(analyseParams, outfile)

    # Make and save the bash file that will run deeplabcut on the cluster
    with open(bash_path_local, "w", newline="\n") as bash_file:
        bash_file.write("#!/bin/bash\n")
        bash_file.write("set -e\n")
        bash_file.write("nerf_deeplabcut_launch_slurm.py")
        bash_file.write(
            f"   --input_json_file {os.path.join(version_path, 'DLC_params_analyse.json')}"
        )
        bash_file.write(f"   --out_directory {os.path.join(out_directory,session)}")
        bash_file.write(f"   --program_to_run analysis")
        bash_file.write(f"   --job_name {mID}/{session}")
        bash_file.write(f"   --n_cpus_per_task 10")
        bash_file.write(f"   --n_gpus 2")
        bash_file.write(f"   --email {user_email}")
        bash_file.close()

    commands = [f"bash {bash_path_nerfcluster}"]

    # client = initialize_client(clusterNode, clusterUser, clusterPassword)

    # cluster_jobs.execute_commands(client, commands)

    # while not os.path.exists(os.path.join(server_local, raw_path, 'done.txt')):
    #     # Check that nerfcluster job is still running
    #     commands = [
    #         f"squeue"
    #     ]
    #     nerfcluster_jobs.execute_commands(client, commands)
    #     print("Waiting for file to be created")
    #     time.sleep(60*5)
