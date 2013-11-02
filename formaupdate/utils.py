import urllib
import itertools
import requests
import math
from simplejson.decoder import JSONDecodeError

def build_url(base_url, query):
    """Build full query URL, including URL-encoded query."""
    return base_url % urllib.quote(query)

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

def get_id(func, base_url, query, table):
    url = build_url(base_url, query % (func, table))
    r = requests.get(url)

    return r.json()["rows"][0][func]
    
def calc_range_params(base_url, step_count, table):
    
    print "Calculating range parameters from cartodb_ids for table %s" % table
    query = "SELECT %s(cartodb_id) FROM %s"

    min_id = get_id("min", base_url, query, table)
    max_id = get_id("max", base_url, query, table)

    step_size = int(math.floor((max_id - min_id) / step_count))
    print "Min: %d\nMax: %d\nStep size: %d" % (min_id, max_id, step_size)

    return min_id, max_id, step_size

def check_error(response):
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

def run_queries(base_url, queries):
    return [run_query(base_url, q) for q in queries]
