import pathlib
import pandas as pd
import shutil

import sys

sys.path.append("../IDR_stream/")
from idrstream.DP_idr import DeepProfilerRun

# directory with all locations data csvs (with plate/well/frame image location data for IDR_stream)
locations_dir = pathlib.Path("../../0.locate_data/locations/")

# idr ID for MitoCheck data
idr_id = "idr0013"

# path to users home dir
home_dir_path = pathlib.Path.home()

# set downloader paths
aspera_path = pathlib.Path(f"{home_dir_path}/.aspera/ascli/sdk/ascp")
aspera_key_path = pathlib.Path("../stream_files/asperaweb_id_dsa.openssh")
screens_path = pathlib.Path("../stream_files/idr0013-screenA-plates.tsv")

# set fiji path
fiji_path = pathlib.Path(f"{home_dir_path}/Desktop/Fiji.app")

# set segmentation params for MitoCheck data
nuclei_model_specs = {
    "model_type": "cyto",
    "channels": [0, 0],
    "diameter": 0,
    "flow_threshold": 0.8,
    "cellprob_threshold": 0,
    "remove_edge_masks": True,
}

for data_locations_path in sorted(locations_dir.iterdir()):
    # name of data being processed (training_data, negative_control_data, or positive_control_data)
    data_name = data_locations_path.name.replace("_locations.tsv", "_data")
    print(f"Running IDR_stream DP for {data_name}")

    # path to temporary data directory that holds intermediate idrstream files
    tmp_dir = pathlib.Path("tmp/")
    # remove tmp directory if it already exists (ex: from a previous IDR_stream run)
    shutil.rmtree(tmp_dir, ignore_errors=True)
    # path to final data directory (place final .csv.gz metadata+features are saved)
    final_data_dir = pathlib.Path(f"../extracted_features/{data_name}/DP_features")
    # path to log file
    log_file_path = pathlib.Path(f"logs/{data_name}/dp_idrstream.log")
    # remove log file if it already exists
    log_file_path.unlink(missing_ok=True)
    # create parent directory for log file if it doesn't exist
    log_file_path.parent.mkdir(exist_ok=True, parents=True)

    # initialize IDR_stream dp run
    stream = DeepProfilerRun(idr_id, tmp_dir, final_data_dir, log=log_file_path)

    # pandas dataframe with plate/well/frame image location data for IDR_stream
    data_to_process = pd.read_csv(data_locations_path, sep="\t", index_col=0)

    # initialize aspera downloader
    stream.init_downloader(aspera_path, aspera_key_path, screens_path)

    # initialize fiji preprocessor
    stream.init_preprocessor(fiji_path)

    # initialize CellPose segmentor for MitoCheck data
    stream.init_segmentor(nuclei_model_specs)

    # copy necessary DP files to tmp dir
    config_path = pathlib.Path(
        "../stream_files/DP_files/mitocheck_profiling_config.json"
    )
    checkpoint_path = pathlib.Path(
        "../stream_files/DP_files/efficientnet-b0_weights_tf_dim_ordering_tf_kernels_autoaugment.h5"
    )
    stream.copy_DP_files(config_path, checkpoint_path)

    # run dp IDR_stream!
    # if data is for training, also extract outlines (later MitoCheck labels can be associated with the outlines)
    if data_name == "training_data":
        stream.run_dp_stream(
            data_to_process,
            batch_size=3,
            start_batch=0,
            batch_nums=[0],
            extra_metadata=["object_outlines"],
        )
    else:
        stream.run_dp_stream(
            data_to_process, batch_size=3, start_batch=0, batch_nums=[0]
        )
