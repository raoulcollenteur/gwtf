# gwtf: Groundwater Table Fluctuation Method in Python

<img src="docs/_static/logo.png" alt="gwtf logo" height="120" align="left">

[![PyPI version](https://img.shields.io/pypi/v/gwtf.svg)](https://pypi.org/project/gwtf/)
[![GitHub License](https://img.shields.io/github/license/raoulcollenteur/gwtf)](https://github.com/raoulcollenteur/gwtf?tab=MIT-1-ov-file)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![Tests](https://github.com/raoulcollenteur/gwtf/actions/workflows/test.yml/badge.svg)](https://github.com/raoulcollenteur/gwtf/actions)

---

## What is gwtf?

gwtf is an open-source Python package for estimating and analyzing groundwater recharge using the Water Table Fluctuation (WTF) method. The package provides tools for event extraction, recharge estimation, and uncertainty analysis, all in a user-friendly and extensible framework.

---

## Code Example

```
import gwtf

wt = pd.read_csv("head.csv", parse_dates=["date"], index_col="date")

ml = wtf.Model(wt, name="Wagna", mcr=wtf.MCR())
ml.mcr.fit_mcr(wt)

r2= ml.estimate_recharge(rise_rule="rises", sy=0.15)
r.resample("YE").sum().plot(kind="bar", figsize=(10, 2))
```

---

## Documentation & Examples

- Full documentation: [gwtf.readthedocs.io](https://gwtf.readthedocs.io/)
- Example notebooks: [`examples/`](examples/)

---

## Get in Touch

- Questions? Use [GitHub Discussions](https://github.com/raoulcollenteur/gwtf/discussions)
- Found a bug or want a feature? Open an [issue](https://github.com/raoulcollenteur/gwtf/issues)
- Contributions are welcome! See [`CONTRIBUTING.md`](CONTRIBUTING.md)

---

## Quick Installation Guide

gwtf requires Python 3.9 or higher. We recommend using [Anaconda](https://www.anaconda.com/products/distribution) for easy management of dependencies, but any other Python distribution should work. Check `pyproject.toml` for the dependencies on other Python packages.

### Stable version

```bash
pip install gwtf
```

### Update

```bash
pip install gwtf --upgrade
```

### Development version

```bash
pip install git+https://github.com/raoulcollenteur/gwtf.git@main#egg=gwtf
```

---

---

## How to cite gwtf

If you use gwtf in your research, please cite:

> Collenteur, R.A. (2025). gwtf: Python implementation of the Water Table Fluctuation (WTF) Method. Zenodo. [https://doi.org/10.5281/zenodo.XXXXXXX](https://doi.org/10.5281/zenodo.XXXXXXX)

---

## License

gwtf is licensed under the GNU General Public License. See the [LICENSE](LICENSE) file for details.
