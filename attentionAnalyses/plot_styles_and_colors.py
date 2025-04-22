# make sure to install fklab colors and styles

from fklab.utilities.plots import install_custom_colors
import seaborn as sns

COLORS = {
    "Baseline": sns.color_palette()[7],
    "SQR08_100L": sns.color_palette("Greens")[1],
    "SQR08_100LR": sns.color_palette("Greens")[3],
    "GAB08_100LR": sns.color_palette("Greens")[5],
    "Training": sns.color_palette()[8],
    "SpatialTaskNoReward_100": sns.color_palette("BrBG")[5],
    "SpatialTask2_30": sns.color_palette("BrBG")[3],
    "SpatialTask2_100": sns.color_palette("BrBG")[4],
    "SpatialTask4P_15": sns.color_palette("BrBG")[0],
    "SpatialTask4P_30": sns.color_palette("BrBG")[1],
    "SpatialTask_100": sns.color_palette("Blues", n_colors=12)[11],
    "SpatialTask_30": sns.color_palette("Blues", n_colors=12)[9],
    "SpatialTask_15": sns.color_palette("Blues", n_colors=12)[7],
    "SpatialTask_09": sns.color_palette("Blues", n_colors=12)[5],
    "SpatialTask_05": sns.color_palette("Blues", n_colors=12)[3],
}

install_custom_colors(COLORS)
