version = "0.1.0"

def show_versions():
    """Show the version of gwtf and its dependencies."""
    import matplotlib as mpl
    import numpy as np
    import pandas as pd
    import scipy as sp

    print(f"gwtf: {version}")
    print(f"pandas: {pd.__version__}")
    print(f"numpy: {np.__version__}")
    print(f"scipy: {sp.__version__}")
    print(f"matplotlib: {mpl.__version__}")