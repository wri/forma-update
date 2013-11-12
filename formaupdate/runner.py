import os
import itertools
import sys
import time

import requests

from utils import *

# table containing data in common data model
INITTABLE = "cdm_2013_11_08_clean"

# temporary table during update process - MUST BE PUBLIC
TABLE = "gfw2_forma_ew3"

APIKEY = os.environ["CARTODB_API_KEY"]

# head of API URL used for all queries
BASEURL = "https://wri-01.cartodb.com/api/v2/sql?api_key=%s&q=" % APIKEY

MAXZOOM = 17
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
CREATEINDEX = "CREATE INDEX %s_%s_idx ON gfw2_forma_ew (%s)"

def gen_load_17_query(subq, query, input_table, minid, maxid, stepsize, z):
    subq = subq % input_table
    subqueries = gen_range_queries(minid, maxid, stepsize, subq, "cartodb_id")
    return [query % (TABLE, z, q) for q in subqueries]

def gen_update_null_queries(table, sd_query, se_query, minid, maxid, stepsize, z=None):

    sd_query = sd_query % table
    queries = gen_range_queries(minid, maxid, stepsize, sd_query, "cartodb_id")
    
    se_query = se_query % table
    queries += gen_range_queries(minid, maxid, stepsize, se_query, "cartodb_id")
    
    if z:
        queries = [range_query(z, z + 1, q, "z") for q in queries]
    else:
        pass

    return queries

def create_indexes(drop_query, create_query, table, base_url):
    queries = [drop_query % (table, f) for f in ["x", "y", "z"]]
    queries += [create_query % (table, f, f) for f in ["x", "y", "z"]]

    return run_queries(base_url, queries)

def run_z17(init_table, table, z):

    # get range for init table
    minid, maxid, stepsize = calc_range_params(BASEURL, STEPCOUNT, init_table)

    # gen queries to load data into new table for z17
    queries = gen_load_17_query(ZOOMSUBQUERY17, ZOOMQUERY, init_table,
                                minid, maxid, stepsize, z)
    # run queries
    r = run_queries(BASEURL, queries)
    
    # get range for new table
    minid, maxid, stepsize = calc_range_params(BASEURL, STEPCOUNT, table)
    
    # gen queries to update null values in new table for z17
    # no need to specify zoom level, since there's only z17
    queries = gen_update_null_queries(TABLE, UPDATENULLSD17,
                                    UPDATENULLSE17, minid, maxid,
                                    stepsize)

    r += run_queries(BASEURL, queries)
    return r

def process_zoom(z):
    r = []
    print "\nRunning zoom %d\n" % z
    minid, maxid, stepsize = calc_range_params(BASEURL, STEPCOUNT, TABLE)
    
    # subqueries = gen_range_queries(minid, maxid, stepsize, ZOOMSUBQUERY, "cartodb_id")
    
    # add data for zoom level
    query = ZOOMQUERY % (TABLE, z, ZOOMSUBQUERY % (TABLE, z + 1))
    r += run_query(BASEURL, query)

    minid, maxid, stepsize = calc_range_params(BASEURL, STEPCOUNT, TABLE)
    
    # gen queries to update null values in table for zoom level
    queries = gen_update_null_queries(TABLE, UPDATENULLSD,
                                    UPDATENULLSE, minid, maxid,
                                    stepsize, z)
    r += run_queries(BASEURL, queries)

    return r

def main(z_min=MINZOOM, z_max=MAXZOOM):
    t = time.time()
    responses = []
    
    # process data for z17
    responses += run_z17(INITTABLE, TABLE, z_max)
    
    # create indexes for table
    responses += create_indexes(DROPINDEX, CREATEINDEX, TABLE, BASEURL)

    # process data for zooms below 17
    for z in range(z_max - 1, z_min - 1, -1): # z17 already done
        process_zoom(z)

    print "\nElapsed time: %0.1f minutes" % ((time.time() - t) / 60)
    return responses
