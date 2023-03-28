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

ListofMetals = [
    2606,
    261710,
    2524,
    2511,
    8106,
    8107,
    2610,
    2701,
    810520,
    2603,
    7108,
    2504,
    2601,
    2607,
    283691,
    251910,
    2602,
    280540,
    2613,
    271111,
    2604,
    2709,
    2846,
    261610,
    2609,
    2611,
    2608,
    261510,
]

ListofYears = [
    2002,
    2003,
    2004,
    2005,
    2006,
    2007,
    2008,
    2009,
    2010,
    2011,
    2012,
    2013,
    2014,
    2015,
    2016,
    2017,
    2018,
    2019,
    2020,
]

ListofCountries = [
    36,
    124,
    97,
    251,
    276,
    392,
    826,
    842,
    32,
    40,
    50,
    56,
    191,
    203,
    208,
    246,
    300,
    381,
    348,
    372,
    442,
    528,
    579,
    616,
    724,
    642,
    620,
    703,
    705,
    752,
    757,
    76,
    64,
]

ListofMetalName = [
    "Aluminium",
    "Antimony",
    "Asbestos",
    "Barytes",
    "Bismuth",
    "Cadmium",
    "Chromium",
    "Coal",
    "Cobalt",
    "Copper",
    "Gold",
    "Graphite",
    "Iron",
    "Lead",
    "Lithium",
    "Magnesite",
    "Manganese",
    "Mercury",
    "Molybdenum",
    "NG",
    "Nickel",
    "Crude_Oil",
    "REE",
    "Silver",
    "Tin",
    "Tungsten",
    "Zinc",
    "Zirconium",
]
ListofCountryName = [
    "Australia",
    "Canada",
    "European Union",
    "France",
    "Germany",
    "Japan",
    "United Kingdom",
    "USA",
    "Argentina",
    "Austria",
    "Bangladesh",
    "Belgium",
    "Croatia",
    "Czechia",
    "Denmark",
    "Finland",
    "Greece",
    "Italy",
    "Hungary",
    "Ireland",
    "Luxembourg",
    "Netherlands",
    "Norway",
    "Poland",
    "Spain",
    "Romania",
    "Portugal",
    "Slovakia",
    "Slovenia",
    "Sweden",
    "Switzerland",
    "Brazil",
    "Bhutan",
]


import random


def random_sampler(A, n):
    return random.sample(A, n)
