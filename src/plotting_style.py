import matplotlib.pyplot as plt


def apply_style():
    """
    Consistent, readable look for every figure in the project:
    larger fonts, a light default grid, clean spines, and a
    fixed color cycle so the same variable reads the same way
    across different plots.
    """

    plt.rcParams.update({

        "figure.dpi": 100,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",

        "font.size": 12,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "legend.frameon": True,
        "legend.framealpha": 0.9,

        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linestyle": "-",

        "axes.spines.top": False,

        "axes.axisbelow": True,

        "lines.linewidth": 1.5,

        "axes.prop_cycle": plt.cycler(
            color=[
                "tab:blue",
                "tab:orange",
                "tab:green",
                "tab:red",
                "tab:purple",
                "tab:brown",
                "tab:pink",
                "tab:gray",
            ]
        ),

    })
