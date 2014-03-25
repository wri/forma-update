import os
import itertools
import sys
import time

import requests

from utils import *

# table containing data in common data model
INITTABLE = "cdm_2014_03_16"

# temporary table during update process
TABLE = "gfw2_forma_ew1"

# table for checking whether specific pixels were correctly processed
CONTROLTABLE = 'gfw2_forma_control_pixels'

APIKEY = os.environ["CARTODB_API_KEY"]

# head of API URL used for all queries
BASEURL = "https://wri-01.cartodb.com/api/v2/sql?api_key=%s&q=" % APIKEY

RANGEFIELD = 'cartodb_id'
RANGEFIELD2 = 'cartodb_id'
MAXZOOM = 15
MINZOOM = 6
STEPCOUNT = 20

ZOOMQUERY17 = "INSERT INTO %s (x,y,date_array,z) (SELECT x, y, array_agg(undate) as date_array, %d as z FROM (%s) foo GROUP BY x,y)"

ZOOMSUBQUERY17 = "SELECT x::int, y::int, p::int AS undate FROM %s"

ZOOMQUERY = "INSERT INTO %s (x,y,date_array,z) (SELECT x, y, array_agg(undate) AS date_array, %d AS z FROM (%s) foo GROUP BY x,y)"

ZOOMSUBQUERY = "SELECT floor(x/2) AS x, floor(y/2) AS y, unnest(date_array) AS undate FROM %s WHERE z = %d"

UPDATENULLSD = "UPDATE %s SET sd = ARRAY(SELECT DISTINCT UNNEST(date_array) ORDER BY 1)"

UPDATENULLSE = "UPDATE %s SET se = ARRAY(SELECT count(*) FROM UNNEST(date_array) d GROUP BY d ORDER BY d)"

UPDATENULLSD17 = range_query(MAXZOOM, MAXZOOM + 1, UPDATENULLSD + " WHERE sd is null", "z")

UPDATENULLSE17 = range_query(MAXZOOM, MAXZOOM + 1, UPDATENULLSE + " WHERE se is null", "z")

DROPINDEX = "DROP INDEX IF EXISTS %s_%s_idx"
CREATEINDEX = "CREATE INDEX %s_%s_idx ON %s (%s)"


def create_indexes(drop_query, create_query, table, base_url):

    queries = gen_drop_index_queries(drop_query, table)
    queries += gen_create_index_queries(create_query, table)

    return run_queries(table, base_url, queries)

def run_z17(base_url, step_count, init_table, table, z, zoom_sub,
            zoom, sd_query, se_query, range_field, ctrl_table):

    # get range for init table
    minid, maxid, stepsize = calc_range_params(base_url, step_count,
                                               init_table, range_field)
    # gen queries to load data into new table for z17
    queries = gen_load_17_query(zoom_sub, zoom, init_table, table,
                                minid, maxid, stepsize, z, range_field)

    results = []

    # run queries
    results = run_queries(table, base_url, queries)

    # get range for new table
    minid, maxid, stepsize = calc_range_params(base_url, step_count,
                                               table, range_field)

    # gen queries to update null values in new table for z17
    queries = gen_update_null_queries(table, UPDATENULLSD17, minid,
                                      maxid, stepsize, z,
                                      range_field=range_field)

    queries += gen_update_null_queries(table, UPDATENULLSE17, minid,
                                       maxid, stepsize, z,
                                       range_field=range_field)

    results += run_queries(table, base_url, queries)

    # check that a given zoom level has some rows, no nulls in sd/se fields
    # if any checks fail, an exception will be raised.
    if zoom_ok(z, table, ctrl_table, base_url):
        return results

    return results

def process_zoom(table, z, base_url, step_count, zoom_sub, zoom,
                 update_sd, update_se, range_field, ctrl_table):
    results = []
    print "\nRunning zoom %d\n" % z

    # incrementally add data for zoom level
    # get range for table
    minid, maxid, stepsize = calc_range_params(base_url, step_count,
                                               table, range_field,
                                               zoom=z+1)

    # gen queries to load data for zoom level
    queries = gen_load_Z_query(zoom_sub, zoom, table, minid, maxid,
                               stepsize, z, range_field)
    
    results += run_queries(table, base_url, queries)

    # bulk load add data - works better ...
    query = zoom % (table, z, zoom_sub % (table, z + 1))
    results += run_query(base_url, query)

    minid, maxid, stepsize = calc_range_params(base_url, step_count,
                                               table, range_field,
                                               zoom=z)

    # gen queries to update null values in table for zoom level
    queries = gen_update_null_queries(table, UPDATENULLSE,
                                      minid, maxid, stepsize, z,
                                      range_field)

    queries += gen_update_null_queries(table, UPDATENULLSD,
                                      minid, maxid, stepsize, z,
                                      range_field)

    results += run_queries(table, base_url, queries)

    # check that a given zoom level has some rows, no nulls in sd/se fields
    # if any checks fail, an exception will be raised.
    if zoom_ok(z, table, ctrl_table, base_url):
        return results

def main(input_table=INITTABLE, output_table=TABLE, z_min=MINZOOM, z_max=MAXZOOM):
    t = time.time()
    responses = []
    
    # load and update data for z17
    responses += run_z17(BASEURL, STEPCOUNT, INITTABLE, TABLE, z_max,
                         ZOOMSUBQUERY17, ZOOMQUERY17, UPDATENULLSD17,
                         UPDATENULLSE17, RANGEFIELD, CONTROLTABLE)
    
    # create indexes for table
    responses += create_indexes(DROPINDEX, CREATEINDEX, TABLE, BASEURL)

    # # process data for zooms below 17
    # for z in range(z_max - 1, z_min - 1, -1): # z17 already done
    #     process_zoom(TABLE, z, BASEURL, STEPCOUNT, ZOOMSUBQUERY,
    #                  ZOOMQUERY, UPDATENULLSD, UPDATENULLSE,
    #                  RANGEFIELD2, CONTROLTABLE)

    print "\nElapsed time: %0.1f minutes" % ((time.time() - t) / 60)
    return responses
