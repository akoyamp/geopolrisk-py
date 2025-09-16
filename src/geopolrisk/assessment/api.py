from typing import Dict, List, Optional, Union

from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel

# Geopolrisk imports
from . import main, utils

class GprsCalcRequest(BaseModel):
    years: List[int]
    countries: List[Union[str, int]]
    raw_materials: Optional[List[str]] = None
    region: Dict[str, List[str]] = {}

app = FastAPI()

def serialize_df(df: pd.DataFrame):
    schema = pd.io.json.build_table_schema(df)
    return {
        "columns": schema["fields"],
        "rows": df.values.tolist() 
    }

@app.get("/status")
def status():
    return {"status": "ok"}


@app.get("/raw_materials")
def raw_materials():
    return {"raw_materials": utils.default_rmlist()}


@app.post("/gprs_calc")
def gprs_calc(request: GprsCalcRequest):
    raw_materials = utils.default_rmlist() if request.raw_materials is None else request.raw_materials
        
    df: pd.DataFrame = main.gprs_calc(
        period=request.years,
        country=request.countries,
        rawmaterial=raw_materials,
        region_dict=request.region,
        export_to_xlsx=False,
        write_to_db=False
    )
    return {
        "results": serialize_df(df)
    }
