__version__ = "0.2.0"


def show_versions():
    """Show the version of gwtf and its dependencies."""
    import matplotlib as mpl
    import numpy as np
    import pandas as pd
    import scipy as sp

    print(f"gwtf: {__version__}")
    print(f"pandas: {pd.__version__}")
    print(f"numpy: {np.__version__}")
    print(f"scipy: {sp.__version__}")
    print(f"matplotlib: {mpl.__version__}")
