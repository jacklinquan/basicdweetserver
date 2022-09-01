"""Basic dweet server with FastAPI and Deta.

- Author: Quan Lin
- License: MIT
"""

import os
from datetime import datetime
from hashlib import sha256

from fastapi import FastAPI, Request
from deta import Deta


# Time stamp format, later the `us` part needs to be changed to `ms`.
UTC_TIME_STRING_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
# Seconds per day.
SECS_PER_DAY = 86400
# Max number of items of each thing.
MAX_THING_ITEM_NUM = 5

# The flag to tell whether it is running in Deta runtime or a local debugging runtime.
deta_runtime = os.getenv("DETA_RUNTIME")
app = FastAPI()

if deta_runtime:
    deta = Deta()
    # Deta database
    db = deta.Base("basicdweetserver_db")
else:
    # Dummy database in RAM
    db = {}


def get_utc_time_string():
    """Get the current UTC time stamp string."""
    utc_time = datetime.utcnow()
    full_utc_time_string = utc_time.strftime(UTC_TIME_STRING_FORMAT)
    utc_time_string = full_utc_time_string[:23] + "Z"
    return utc_time_string


def db_set(key, data):
    """Database `set` function."""
    if deta_runtime:
        res = db.put(data, key=key, expire_in=SECS_PER_DAY)
    else:
        data["key"] = key
        db[key] = data
        res = data

    return res


def db_get(key):
    """Database `get` function."""
    return db.get(key)


def db_delete(key):
    """Database `delete` function."""
    if deta_runtime:
        db.delete(key)
    else:
        db.pop(key)


def db_fetch_all(query=None):
    """Database `fetch all` function with query."""
    all_res = []
    if deta_runtime:
        res = db.fetch(query=query)
        all_res += res.items
        while res.last:
            res = db.fetch(query=query, last=res.last)
            all_res += res.items
    else:
        all_res = [
            item
            for item in db.values()
            if (not query) or (item["thing"] == query["thing"])
        ]

    return all_res


def get_key_of_base_dict(base_dict):
    """Get the key of a Deta Base dict."""
    return "_".join((base_dict["created"], base_dict["thing"]))


def get_base_dict(thing, para_dict):
    """Get a Deta Base dict from the given `thing` and `para_dict`."""
    base_dict = {}
    base_dict["thing"] = thing
    base_dict["created"] = get_utc_time_string()
    base_dict["content"] = para_dict

    tr_id = sha256(get_key_of_base_dict(base_dict).encode()).hexdigest()[:32]
    tr_id_list = list(tr_id)
    tr_id_list.insert(20, "-")
    tr_id_list.insert(16, "-")
    tr_id_list.insert(12, "-")
    tr_id_list.insert(8, "-")
    tr_id = "".join(tr_id_list)
    base_dict["transaction"] = tr_id

    return base_dict


def get_dict_of_dweet_for(base_dict):
    """Get a returned dict for the `dweet for` API."""
    dweet_dict = {}

    if not base_dict:
        dweet_dict["this"] = "failed"
        dweet_dict["with"] = 404
        dweet_dict["because"] = "we couldn't find this"
        return dweet_dict
    else:
        dweet_dict["this"] = "succeeded"

    dweet_dict["by"] = "dweeting"
    dweet_dict["the"] = "dweet"
    dweet_dict["with"] = {}

    dweet_dict["with"]["thing"] = base_dict.get("thing")
    dweet_dict["with"]["created"] = base_dict.get("created")
    dweet_dict["with"]["content"] = base_dict.get("content")
    dweet_dict["with"]["transaction"] = base_dict.get("transaction")

    return dweet_dict


def get_dict_of_get_dweet(base_dict_list):
    """Get a returned dict for the `get latest dweet` and `get dweets` API."""
    dweet_dict = {}

    if not base_dict_list:
        dweet_dict["this"] = "failed"
        dweet_dict["with"] = 404
        dweet_dict["because"] = "we couldn't find this"
        return dweet_dict
    else:
        dweet_dict["this"] = "succeeded"

    dweet_dict["by"] = "getting"
    dweet_dict["the"] = "dweets"
    dweet_dict["with"] = []

    for item in base_dict_list:
        item_dict = {}
        item_dict["thing"] = item.get("thing")
        item_dict["created"] = item.get("created")
        item_dict["content"] = item.get("content")
        dweet_dict["with"].append(item_dict)

    return dweet_dict


def limit_db_items(thing, num=MAX_THING_ITEM_NUM):
    """Limit the number of items of the given thing."""
    all_res = db_fetch_all(query={"thing": thing})
    all_res.sort(key=lambda x: x["created"], reverse=True)
    for item in all_res[num:]:
        db_delete(item["key"])


@app.get("/")
async def get_root():
    """Get basic api info."""
    return {
        "Description": "Basic dweet server.",
        "/dweet/for/{thing}": "Create a dweet for a thing.",
        "/get/latest/dweet/for/{thing}": "Read the latest dweet for a thing.",
        "/get/dweets/for/{thing}": "Read the last 5 cached dweets for a thing.",
    }


@app.get("/dweet/for/{thing}")
async def dweet_for_by_get(thing: str, request: Request):
    """Create a dweet for a thing."""
    base_dict = get_base_dict(thing, dict(request.query_params))
    res = db_set(get_key_of_base_dict(base_dict), base_dict)
    limit_db_items(thing)
    dweet_dict = get_dict_of_dweet_for(res)
    return dweet_dict


@app.get("/get/latest/dweet/for/{thing}")
async def get_latest_dweet_for(thing: str):
    """Read the latest dweet for a thing."""
    all_res = db_fetch_all(query={"thing": thing})
    all_res.sort(key=lambda x: x["created"], reverse=True)
    dweet_dict = get_dict_of_get_dweet(all_res[:1])
    return dweet_dict


@app.get("/get/dweets/for/{thing}")
async def get_dweets_for(thing: str):
    """Read the last 5 cached dweets for a thing."""
    all_res = db_fetch_all(query={"thing": thing})
    all_res.sort(key=lambda x: x["created"], reverse=True)
    dweet_dict = get_dict_of_get_dweet(all_res)
    return dweet_dict


@app.post("/dweet/for/{thing}")
async def dweet_for(thing: str, data: dict):
    """Create a dweet for a thing."""
    base_dict = get_base_dict(thing, data)
    res = db_set(get_key_of_base_dict(base_dict), base_dict)
    limit_db_items(thing)
    dweet_dict = get_dict_of_dweet_for(res)
    return dweet_dict
