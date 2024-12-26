from geopolrisk.assessment.main import gprs_calc
from geopolrisk.assessment.utils import regions

NewRegions = {
    "EFTA": ["Iceland", "Norway", "Switzerland"],
    "NAFTA": ["Canada", "Mexico", "USA"],
}

ListofMetals = [
    260400,
]
ListofCountries = ["EU"]
ListofYear = [2022]
regions(NewRegions)
gprs_calc(ListofYear, ListofCountries, ListofMetals)
