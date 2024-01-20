from flask import current_app

import time

#=======================================================================
# Fetch_From_Cache
#=======================================================================
def Fetch_From_Cache( Target_Address, Target_Port ):
    Cache_Target = Target_Address + "_" + str(Target_Port)

    Scrape_Data = None
    Scrape_Return = False

    if Cache_Target in current_app.config["SCRAPE_CACHE"]:
        Age = (time.time() - current_app.config["SCRAPE_CACHE"][Cache_Target]["time"])
        if Age < current_app.config["CACHE_PERIOD"]:
            current_app.logger.debug("In cache and valid")
            Scrape_Data   = current_app.config["SCRAPE_CACHE"][Cache_Target]["data"]
            Scrape_Return = True
        else:
            current_app.logger.debug("In cache but expired")
            current_app.config["SCRAPE_CACHE"].pop(Cache_Target)

    return Scrape_Return, Scrape_Data

#=======================================================================
# Add_To_Cache
#=======================================================================
def Add_To_Cache( Target_Address, Target_Port, Scrape_Data ):
    # If config CACHE_PERIOD is 0 then don't cache
    if current_app.config["CACHE_PERIOD"] == 0:
        return
    
    Cache_Target = Target_Address + "_" + str(Target_Port)
    current_app.logger.debugv("Add to cache {}".format( Cache_Target ))

    current_app.config["SCRAPE_CACHE"][Cache_Target]         = {}
    current_app.config["SCRAPE_CACHE"][Cache_Target]["time"] = time.time()
    current_app.config["SCRAPE_CACHE"][Cache_Target]["data"] = Scrape_Data
    return

#=======================================================================
# Tidy_Cache
#=======================================================================
def Tidy_Cache():
    Remove_List = []

    for c in current_app.config["SCRAPE_CACHE"]: 
        Age = (time.time() - current_app.config["SCRAPE_CACHE"][c]["time"])
        if Age > current_app.config["CACHE_PERIOD"]:
            current_app.logger.debugv("Remove from cache {}".format( c ))
            Remove_List.append(c)

    for r in Remove_List:
        current_app.config["SCRAPE_CACHE"].pop(r)
    return
