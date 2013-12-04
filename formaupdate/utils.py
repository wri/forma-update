import urllib
import itertools
import math
from simplejson.decoder import JSONDecodeError

import requests

def build_url(base_url, query):
    """Build full query URL, including URL-encoded query."""
    return "%s%s" % (base_url, urllib.quote(query))

def parse_where(query):
    """If a query contains a WHERE clause, extend it with AND. If not, add
    a WHERE clause."""
    if not "WHERE" in query.upper():
        return "%s WHERE" % (query)
    else:
        return "%s AND" % (query)

def range_query(start, end, query, range_type="cartodb_id"):
    """Make a range query by using/extending a WHERE clause."""
    q = parse_where(query)
    return "%s %s >= %d AND %s < %d" % (q, range_type, start, range_type, end)

def gen_range_queries(start, end, step, query, range_type="cartodb_id"):
    """Generate range queries from range parameters."""
    return [range_query(i, i + step, query, range_type) for i in range(start, end, step)]

def restrict_all(min_id, max_id, step_size, min_z, max_z, query):
    """Restrict a query to cartodb_ids and zoom levels."""

    restricted_ids = gen_range_queries(min_id, max_id + 1, step_size, query, "cartodb_id")
    result = [gen_range_queries(min_z, max_z + 1, 1, query, "z") for query in restricted_ids]
    
    return list(itertools.chain(*result)) # flatten list

def get_id(func, base_url, table):
    """Get cartodb_id from table that corresponds to 'func' variable,
    typically 'min' or 'max'."""

    query = "SELECT %s(cartodb_id) FROM %s" % (func, table)

    url = build_url(base_url, query)

    r = requests.get(url)

    return r.json()["rows"][0][func]
    
def gen_step_size(min_id, max_id, step_count):
    """Generate step size given min/max cartodb_id and desired number of
    steps given in step_count."""
    return int(math.floor((max_id - min_id) / step_count))

def calc_range_params(base_url, step_count, table):
    """Calculate range parameters for query based on min/max cartodb_id
    values."""
    
    print "Calculating range parameters from cartodb_ids for table %s" % table

    min_id = get_id("min", base_url, table)
    max_id = get_id("max", base_url, table)

    step_size = gen_step_size(min_id, max_id, step_count)
    print "Min: %d\nMax: %d\nStep size: %d" % (min_id, max_id, step_size)

    return min_id, max_id, step_size

def check_error(response):
    """Parse error codes in query response and handle appropriately by
    returning true for fatal error, false otherwise."""
    # in case of HTML-page error message
    try:
        s = response.text
    except JSONDecodeError:
        s = response
    if "503" and "varnish" in s.lower():
        print "Varnish error - query may have completed successfully"
        return False
    elif "error" in s.lower():
        print "Query failed: \n%s" % s
        print "Retrying"
        return True
        
def run_query(base_url, query):
    max_tries = 5
    tries = 0
    error = False

    print "\nRunning query: \n%s" % query
    query_url = build_url(base_url, query)

    while tries < max_tries:
        response = requests.get(query_url)
        error = check_error(response)
        if error:
            tries += 1
        else:
            break
    if error:
        print "\nFatal error. Aborting query retries after %s tries." % tries
        print "\nQuery: \n\"%s\"" % query
        print "\nURL: \n%s" % query_url
        print "\nError: \n%s" % resp
        print "\nExiting script"

    else:
        print "Query completed successfully: %s" % response.text

    return response

def run_queries(table, base_url, queries):
    return [run_query(base_url, q) for q in queries]

def gen_load_17_query(subq, query, input_table, table, minid, maxid, stepsize, z):
    subq = subq % input_table
    subqueries = gen_range_queries(minid, maxid, stepsize, subq, "cartodb_id")
    return [query % (table, z, q) for q in subqueries]

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
    queries += [create_query % (table, f, table, f) for f in ["x", "y", "z"]]

    return run_queries(table, base_url, queries)

def run_z17(base_url, step_count, init_table, table, z, zoom_sub, zoom, sd_query, se_query):

    # get range for init table
    minid, maxid, stepsize = calc_range_params(base_url, step_count, init_table)

    # gen queries to load data into new table for z17
    queries = gen_load_17_query(zoom_sub, zoom, init_table, table,
                                minid, maxid, stepsize, z)
    # run queries
    r = run_queries(table, base_url, queries)
    
    # get range for new table
    minid, maxid, stepsize = calc_range_params(base_url, step_count, table)
    
    # gen queries to update null values in new table for z17
    # no need to specify zoom level, since there's only z17
    queries = gen_update_null_queries(table, sd_query, se_query,
                                      minid, maxid, stepsize)

    r += run_queries(table, base_url, queries)
    return r

def process_zoom(table, z, base_url, step_count, zoom_sub, zoom, update_sd, update_se):
    r = []
    print "\nRunning zoom %d\n" % z
    minid, maxid, stepsize = calc_range_params(base_url, step_count, table)
    
    # subqueries = gen_range_queries(minid, maxid, stepsize, ZOOMSUBQUERY, "cartodb_id")
    
    # add data for zoom level
    query = zoom % (table, z, zoom_sub % (table, z + 1))
    r += run_query(base_url, query)

    minid, maxid, stepsize = calc_range_params(base_url, step_count, table)
    
    # gen queries to update null values in table for zoom level
    queries = gen_update_null_queries(table, update_sd, update_se,
                                      minid, maxid, stepsize, z)
    r += run_queries(table, base_url, queries)

    return r
