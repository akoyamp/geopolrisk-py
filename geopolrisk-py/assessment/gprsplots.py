# Copyright (C) 2023 University of Bordeaux, CyVi Group & Anish Koyamparambath
# This file is part of geopolrisk-py library.
#
# geopolrisk-py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# geopolrisk-py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with geopolrisk-py.  If not, see <https://www.gnu.org/licenses/>.

from matplotlib import rcParams

rcParams["font.family"] = "sans-serif"
rcParams["font.sans-serif"] = ["Tahoma"]
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline, BSpline
from matplotlib.ticker import MaxNLocator
from textwrap import wrap
from .__init__ import (
    instance,
    logging,
)
_outputfile = instance.exportfile
logging.info("Accessed gprsplots module.")

# Read output file
global csvfile
csvfile = "/export.csv"
try:
    data = pd.read_csv(_outputfile + csvfile)
except Exception as e:
    logging.debug(e)

try:
    data.columns = [
        "Year",
        "Resource",
        "Country",
        "RR",
        "RRScenario",
        "GeoPolRisk",
        "CF",
        "HHI",
        "WTA",
    ]
except Exception as e:
    logging.debug(e)


# Splining function
def splining(x, y, degree):
    try:
        x = np.array(x)
        y = np.array(y)
        xnew = np.linspace(x.min(), x.max(), 1000)
        spl = make_interp_spline(x, y, k=degree)  # type: BSpline
        smooth = spl(xnew)
    except Exception as e:
        logging.debug(e)
    return xnew, smooth


def trendplot(country, period, resources):
    fig = plt.figure(figsize=(7, 5), dpi=200, facecolor="#f4f6fa", edgecolor="k")
    gs = fig.add_gridspec(1, 1)
    fig.suptitle("Evolution of the supply risk of selected resources", fontsize=14)
    ax = fig.add_subplot(gs[0, 0])
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.yticks(np.arange(0, 1, 0.1))

    for i in resources:
        GPRS, year = [], []
        rm_temp = 0
        for j in period:
            try:
                year.append(int(j))
            except Exception as e:
                logging.debug(e)
            try:
                GPRS.append(
                    data.loc[
                        (data["Resource"] == i)
                        & (data["Country"] == country[0])
                        & (data["Year"] == j)
                        & (data["RRScenario"] == 0),
                        "GeoPolRisk",
                    ].values[0]
                )
            except Exception as e:
                logging.debug(e)
        rm = max(GPRS)
        rm_temp = rm if rm > rm_temp else rm_temp
        try:
            x, y = splining(year, GPRS, 2)
            plt.plot(x, y, label=i)
        except Exception as e:
            logging.debug(e)

    plt.xlabel("Year")
    plt.ylabel("GPRS")
    ax.set_ylim([0, rm_temp + 0.1])
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="center right")
    fig.tight_layout()
    fig.subplots_adjust(top=0.90, right=0.80, left=0.15)
    return fig


def indplot(Country, Year, resource, scenario):
    Year = int(Year[0])
    switch_dict = {"Resource": resource, "Country": Country}
    if len(resource) > 1 and len(Country) == 1:
        switch = switch_dict["Resource"]
        catch = switch_dict["Country"]
    else:
        switch = switch_dict["Country"]
        catch = switch_dict["Resource"]

    fig = plt.figure(figsize=(7, 5), dpi=200, facecolor="#f4f6fa", edgecolor="k")
    gs = fig.add_gridspec(1, 1)
    fig.suptitle("Comparison of supply risk of resources", fontsize=14)
    ax = fig.add_subplot(gs[0, 0])
    plt.yticks(np.arange(0, 1, 0.1))
    for i in switch:
        try:
            if scenario == 0:
                _Year = (
                    data.loc[
                        (
                            data[
                                list(switch_dict.keys())[
                                    list(switch_dict.values()).index(switch)
                                ]
                            ]
                            == i
                        )
                        & (
                            data[
                                list(switch_dict.keys())[
                                    list(switch_dict.values()).index(catch)
                                ]
                            ]
                            == switch_dict[
                                list(switch_dict.keys())[
                                    list(switch_dict.values()).index(catch)
                                ]
                            ][0]
                        ),
                        "Year",
                    ]
                    .values.tolist()
                    .index(Year)
                )
                trend = data.loc[
                    (
                        data[
                            list(switch_dict.keys())[
                                list(switch_dict.values()).index(switch)
                            ]
                        ]
                        == i
                    )
                    & (
                        data[
                            list(switch_dict.keys())[
                                list(switch_dict.values()).index(catch)
                            ]
                        ]
                        == switch_dict[
                            list(switch_dict.keys())[
                                list(switch_dict.values()).index(catch)
                            ]
                        ][0]
                    ),
                    "GeoPolRisk",
                ].values[_Year]
                plt.bar([i], trend, label=catch[0])

            else:
                # Best Case Scenario
                _Year = (
                    data.loc[
                        (
                            data[
                                list(switch_dict.keys())[
                                    list(switch_dict.values()).index(switch)
                                ]
                            ]
                            == i
                        )
                        & (
                            data[
                                list(switch_dict.keys())[
                                    list(switch_dict.values()).index(catch)
                                ]
                            ]
                            == switch_dict[
                                list(switch_dict.keys())[
                                    list(switch_dict.values()).index(catch)
                                ]
                            ][0]
                        )
                        & (data["RRScenario"] == 2),
                        "Year",
                    ]
                    .values.tolist()
                    .index(Year)
                )
                trend = data.loc[
                    (
                        data[
                            list(switch_dict.keys())[
                                list(switch_dict.values()).index(switch)
                            ]
                        ]
                        == i
                    )
                    & (
                        data[
                            list(switch_dict.keys())[
                                list(switch_dict.values()).index(catch)
                            ]
                        ]
                        == switch_dict[
                            list(switch_dict.keys())[
                                list(switch_dict.values()).index(catch)
                            ]
                        ][0]
                    )
                    & (data["RRScenario"] == 2),
                    "GeoPolRisk",
                ].values[_Year]
                plt.bar([i], trend, label=catch[0])
                # Worst Case Scenario
                _Year = (
                    data.loc[
                        (
                            data[
                                list(switch_dict.keys())[
                                    list(switch_dict.values()).index(switch)
                                ]
                            ]
                            == i
                        )
                        & (
                            data[
                                list(switch_dict.keys())[
                                    list(switch_dict.values()).index(catch)
                                ]
                            ]
                            == switch_dict[
                                list(switch_dict.keys())[
                                    list(switch_dict.values()).index(catch)
                                ]
                            ][0]
                        )
                        & (data["RRScenario"] == 1),
                        "Year",
                    ]
                    .values.tolist()
                    .index(Year)
                )
                trend = data.loc[
                    (
                        data[
                            list(switch_dict.keys())[
                                list(switch_dict.values()).index(switch)
                            ]
                        ]
                        == i
                    )
                    & (
                        data[
                            list(switch_dict.keys())[
                                list(switch_dict.values()).index(catch)
                            ]
                        ]
                        == switch_dict[
                            list(switch_dict.keys())[
                                list(switch_dict.values()).index(catch)
                            ]
                        ][0]
                    )
                    & (data["RRScenario"] == 1),
                    "GeoPolRisk",
                ].values[_Year]
                plt.bar([i], trend, label=catch[0])
        except Exception as e:
            logging.debug(e)

    plt.ylabel("GPRS")
    ax.set_ylim([0.00, 0.10])
    handles, labels = ax.get_legend_handles_labels()
    labels = ["\n".join(wrap(l, 10)) for l in labels]
    fig.legend(
        handles,
        labels,
        loc="center right",
    )
    fig.tight_layout()
    fig.subplots_adjust(top=0.90, right=0.75, left=0.15)
    return fig


def compareplot(Country, Year, resource, scenario):
    if len(Year) == 1 and scenario == 0:
        Year = int(Year[0])
        fig = plt.figure(figsize=(7, 5), dpi=200, facecolor="#f4f6fa", edgecolor="k")
        gs = fig.add_gridspec(1, 1)
        fig.suptitle("Comparison of supply risk of resources", fontsize=14)
        ax = fig.add_subplot(gs[0, 0])
        plt.yticks(np.arange(0, 1, 0.1))
        columns = ["Country"]
        columns.extend(resource)
        allrows = []
        for i in Country:
            GPRS, HHI, WTA = [], [], []
            dfrow = [i]
            for j in resource:
                GPRS.append(
                    data.loc[
                        (data["Resource"] == j)
                        & (data["Country"] == i)
                        & (data["Year"] == Year)
                        & (data["RRScenario"] == 0),
                        "GeoPolRisk",
                    ].values[0]
                )
                HHI.append(
                    data.loc[
                        (data["Resource"] == j)
                        & (data["Country"] == i)
                        & (data["Year"] == Year)
                        & (data["RRScenario"] == 0),
                        "HHI",
                    ].values[0]
                )
                WTA.append(
                    data.loc[
                        (data["Resource"] == j)
                        & (data["Country"] == i)
                        & (data["Year"] == Year)
                        & (data["RRScenario"] == 0),
                        "WTA",
                    ].values[0]
                )
            total = sum(GPRS)
            GPRS = [(i / total) * 100 for i in GPRS]
            dfrow.extend(GPRS)
            allrows.append(dfrow)
        newpd = pd.DataFrame(allrows, columns=columns)
        newpd.plot(
            x="Country",
            kind="bar",
            stacked=True,
            title="Percentage Stacked Bar Graph",
            mark_right=True,
        )
        plt.ylabel("GPRS")
        plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
        ax.set_ylim([0.00, 100])
        fig.tight_layout()
        fig.subplots_adjust(top=0.90, right=0.75, left=0.15)
        return fig
