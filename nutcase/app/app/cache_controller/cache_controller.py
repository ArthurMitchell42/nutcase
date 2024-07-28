import threading
from queue import Empty
import time
import copy

from app.utils import nut_server_handler
from app.utils import apc_server_handler

Scrape_Cache = {}

# =================================================================================================
# Scrape_Bucket class
# =================================================================================================
class Scrape_Bucket():
    def __init__(self, address, port, mode):
        self._address = address
        self._port = port
        self._mode = mode
        self._result = None
        self._scrape_data = {}
        self._ready_flag = threading.Condition()

    @property
    def scrape_data(self):
        return self._scrape_data

    @scrape_data.setter
    def scrape_data(self, new_scrape_data):
        self._scrape_data = new_scrape_data

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, Result):
        self._result = Result

    def get_flag(self):
        return self._ready_flag

    def get_target(self):
        return {"address": self._address, "port": self._port, "mode": self._mode}

    @property
    def target(self):
        return {"address": self._address, "port": self._port, "mode": self._mode}

# =======================================================================
# Add_To_Cache
# =======================================================================
def Add_To_Cache(Target_Address, Target_Port, Scrape_Data):
    Cache_Target = Target_Address + "_" + str(Target_Port)

    Scrape_Cache[Cache_Target]         = {}
    Scrape_Cache[Cache_Target]["time"] = time.time()
    Scrape_Cache[Cache_Target]["data"] = Scrape_Data
    return

# =======================================================================
# Tidy_Cache
# =======================================================================
def Tidy_Cache(Cache_Period):
    Remove_List = []

    for c in Scrape_Cache:
        Age = (time.time() - Scrape_Cache[c]["time"])
        if Age > Cache_Period:
            Remove_List.append(c)

    for r in Remove_List:
        Scrape_Cache.pop(r)
    return

# =======================================================================
# Fetch_From_Cache
# =======================================================================
def Fetch_From_Cache(Target_Address, Target_Port, Cache_Period):
    Cache_Target = Target_Address + "_" + str(Target_Port)

    Scrape_Data = None
    Scrape_Return = False

    if Cache_Target in Scrape_Cache:
        Age = (time.time() - Scrape_Cache[Cache_Target]["time"])
        if Age < Cache_Period:
            # print("In cache and valid")
            Scrape_Data   = Scrape_Cache[Cache_Target]["data"]
            Scrape_Return = True
        else:
            # print("In cache but expired")
            Scrape_Cache.pop(Cache_Target)

    return Scrape_Return, Scrape_Data

# =================================================================================================
# Cache_Handler
# =================================================================================================
def Cache_Handler(app):
    while not app.config['STOP_CACHE'].is_set():
        try:
            Bucket = app.config['CACHE_QUEUE'].get(timeout=5.0)
            app.logger.debug("Data_Handler request for {}".format(Bucket.get_target()))
            Flag = Bucket.get_flag()
            Flag.acquire()
            Target = Bucket.get_target()

            # ===================================================================================
            # Check the cache to see if we need to re-scrape
            # ===================================================================================
            Scrape_Return, Scrape_Data = Fetch_From_Cache(Target['address'], Target['port'],
                                                          app.config["CACHE_PERIOD"])

            if Scrape_Return:
                app.logger.debug("Fetched from cache")
            else:
                app.logger.debug("Not in cache, scraping server")

            if not Scrape_Return:
                # ===================================================================================
                # Get the server data based on type (NUT/APC) as it can't be sourced from the cache
                # ===================================================================================
                with app.app_context():
                    if Target['mode'] == "nut":    # Server_Protocol.NUT:
                        Scrape_Return, Scrape_Data = nut_server_handler.Scrape_NUT_Server(
                                                            Target['address'], Target['port'])
                    elif Target['mode'] == "apc":  # Server_Protocol.APC:
                        Scrape_Return, Scrape_Data = apc_server_handler.Scrape_APC_Server(
                                                            Target['address'], Target['port'])
                    else:
                        Scrape_Return = False
                        Scrape_Data = {}

                # If config CACHE_PERIOD is 0 then don't cache
                if Scrape_Return and app.config["CACHE_PERIOD"] != 0:
                    Add_To_Cache(Target['address'], Target['port'], Scrape_Data)

            Bucket.scrape_data = copy.deepcopy(Scrape_Data)
            Bucket.result = Scrape_Return

            app.logger.debug("Data_Handler result {}".format(Bucket.result))
            Flag.notify()
            Flag.release()
        except Empty:
            Tidy_Cache(app.config["CACHE_PERIOD"])
            continue

    app.logger.debug("Data_Handler stopping")
    return
