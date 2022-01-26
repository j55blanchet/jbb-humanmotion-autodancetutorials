
import json
from typing import Named

from ..datatypes.VideoDatabase import VideoDatabaseEntry

def read_db(db_filepath: str):
    db = []
    with open(db_filepath, 'r', encoding='utf-8') as db_file:
        db = json.load(db_file)

    # TODO: Extract VideoDatabaseEntry lines

    # out = [

    # ]
    # return [{
    #     'title': 
    # }]