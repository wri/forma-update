import os
import itertools
import sys
import time

import requests

from utils import *

# table containing data in common data model
INITTABLE = "cdm_latest"

# temporary table during update process - MUST BE PUBLIC
TABLE = "gfw2_forma_ew"

APIKEY = os.environ["CARTODB_API_KEY"]

# head of API URL used for all queries
BASEURL = "https://wri-01.cartodb.com/api/v2/sql?api_key=%s&q=" % APIKEY

RANGEFIELD = 'x'
MAXZOOM = 16
MINZOOM = 6
STEPCOUNT = 10

ZOOMQUERY17 = "INSERT INTO %s (x,y,date_array,z,iso) (SELECT x, y, array_agg(undate) as date_array, %d as z,array_agg(iso) as iso FROM (%s) foo GROUP BY x,y)"

ZOOMSUBQUERY17 = "SELECT x::int, y::int, p::int AS undate,iso FROM %s"

ZOOMQUERY = "INSERT INTO %s (x,y,date_array,z) (SELECT x, y, array_agg(undate) AS date_array, %d AS z FROM (%s) foo GROUP BY x,y)"

ZOOMSUBQUERY = "SELECT floor(x/2) AS x, floor(y/2) AS y, unnest(date_array) AS undate FROM %s WHERE z = %d"

UPDATENULLSD = "UPDATE %s SET sd = ARRAY(SELECT DISTINCT UNNEST(date_array) ORDER BY 1)"

UPDATENULLSE = "UPDATE %s SET se = ARRAY(SELECT count(*) FROM UNNEST(date_array) d GROUP BY d ORDER BY d)"

UPDATENULLSD17 = range_query(MAXZOOM, MAXZOOM + 1, UPDATENULLSD + " WHERE sd is null", "z")

UPDATENULLSE17 = range_query(MAXZOOM, MAXZOOM + 1, UPDATENULLSE + " WHERE se is null", "z")

DROPINDEX = "DROP INDEX IF EXISTS %s_%s_idx"
CREATEINDEX = "CREATE INDEX %s_%s_idx ON %s (%s)"

def main(z_min=MINZOOM, z_max=MAXZOOM):
    t = time.time()
    responses = []
    
    # process data for z17
    responses += run_z17(BASEURL, STEPCOUNT, INITTABLE, TABLE, z_max,
                         ZOOMSUBQUERY17, ZOOMQUERY17, UPDATENULLSD17,
                         UPDATENULLSE17, RANGEFIELD)
    
    # create indexes for table
    responses += create_indexes(DROPINDEX, CREATEINDEX, TABLE, BASEURL)

    # process data for zooms below 17
    for z in range(z_max - 1, z_min - 1, -1): # z17 already done
        process_zoom(TABLE, z, BASEURL, STEPCOUNT, ZOOMSUBQUERY,
                     ZOOMQUERY, UPDATENULLSD, UPDATENULLSE, RANGEFIELD)

    print "\nElapsed time: %0.1f minutes" % ((time.time() - t) / 60)
    return responses
