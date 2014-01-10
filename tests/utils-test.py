import unittest
from formaupdate.utils import *
from formaupdate import runner

BASEURL = "https://wri-01.cartodb.com/api/v2/sql?q="
SAMPLEQUERY = "SELECT * FROM table"
SAMPLEWHERE = "SELECT * FROM table WHERE id = 1"

class TestEverything(unittest.TestCase):

    def setUp(self):
        self.table = 'test_forma_update'

    def test_build_url(self):
        query = "SELECT count(*) FROM cdm_2013_10_24"
        result = build_url(BASEURL, query)
        self.assertEqual(result, "%s%s" % (BASEURL,
                        "SELECT%20count%28%2A%29%20FROM%20cdm_2013_10_24"))

    def test_parse_where(self):
        result = parse_where(SAMPLEQUERY)
        self.assertEqual(result, "%s WHERE" % SAMPLEQUERY )

    def test_parse_where1(self):
        result = parse_where(SAMPLEWHERE)
        self.assertEqual(result, "%s AND" % SAMPLEWHERE)

    def test_range_query(self):
        start, end = 10, 20
        query = SAMPLEQUERY
        result = range_query(start, end, query, "cartodb_id")
        expected = "%s WHERE cartodb_id::int >= %d AND cartodb_id::int < %d" % (query, start, end)
        self.assertEqual(result, expected)

    def test_range_query1(self):
        start, end = 10, 20
        query = SAMPLEWHERE
        result = range_query(start, end, query, "cartodb_id")
        expected = "%s AND cartodb_id::int >= %d AND cartodb_id::int < %d" % (query, start, end)
        self.assertEqual(result, expected)

    def test_range_query2(self):
        start, end = 10, 20
        query = SAMPLEWHERE
        result = range_query(start, end, query, "z")
        expected = "%s AND z::int >= %d AND z::int < %d" % (query, start, end)
        self.assertEqual(result, expected)

    def test_gen_range_queries(self):
        start, end, step = 100000, 500000, 150000
        result = gen_range_queries(start, end, step, SAMPLEQUERY, "cartodb_id")
        expected = ["SELECT * FROM table WHERE cartodb_id::int >= 100000 AND cartodb_id::int < 250000",
        "SELECT * FROM table WHERE cartodb_id::int >= 250000 AND cartodb_id::int < 400000",
        "SELECT * FROM table WHERE cartodb_id::int >= 400000 AND cartodb_id::int < 550000"]
        self.assertEqual(result, expected)

    def test_gen_range_queries_myfield(self):
        start, end, step = 100000, 500000, 150000
        result = gen_range_queries(start, end, step, SAMPLEQUERY, "myfield")
        expected = ["SELECT * FROM table WHERE myfield::int >= 100000 AND myfield::int < 250000",
                    "SELECT * FROM table WHERE myfield::int >= 250000 AND myfield::int < 400000",
                    "SELECT * FROM table WHERE myfield::int >= 400000 AND myfield::int < 550000"]
        self.assertEqual(result, expected)

    def test_restrict_all(self):
        minid, maxid, step_size, min_z, max_z = 10, 20, 3, 15, 17
        range_field = "cartodb_id"
        result = restrict_all(minid, maxid, step_size, min_z, max_z, SAMPLEQUERY, range_field)

        where_model = "WHERE cartodb_id::int >= %d AND cartodb_id::int < %d AND z::int >= %d AND z::int < %d"
        expected = ["%s %s" % (SAMPLEQUERY, where_model % (10, 13, 15, 16)),
                    "%s %s" % (SAMPLEQUERY, where_model % (10, 13, 16, 17)),
                    "%s %s" % (SAMPLEQUERY, where_model % (10, 13, 17, 18)),
                    "%s %s" % (SAMPLEQUERY, where_model % (13, 16, 15, 16)),
                    "%s %s" % (SAMPLEQUERY, where_model % (13, 16, 16, 17)),
                    "%s %s" % (SAMPLEQUERY, where_model % (13, 16, 17, 18)),
                    "%s %s" % (SAMPLEQUERY, where_model % (16, 19, 15, 16)),
                    "%s %s" % (SAMPLEQUERY, where_model % (16, 19, 16, 17)),
                    "%s %s" % (SAMPLEQUERY, where_model % (16, 19, 17, 18)),
                    "%s %s" % (SAMPLEQUERY, where_model % (19, 22, 15, 16)),
                    "%s %s" % (SAMPLEQUERY, where_model % (19, 22, 16, 17)),
                    "%s %s" % (SAMPLEQUERY, where_model % (19, 22, 17, 18))]
        # for example:
        # SELECT * FROM table WHERE cartodb_id >= 10 AND cartodb_id < 13 
        # AND z >= 15 AND z < 16
        self.assertEqual(result, expected)

    def test_get_field_val(self):
        result = [get_field_val(f, BASEURL, self.table, "cartodb_id") for f in ["min", "max"]]
        expected = [22328022, 22328026]
        self.assertEqual(result, expected)

    def test_get_field_val1(self):
        result = [get_field_val(f, BASEURL, self.table, "x") for f in ["min", "max"]]
        expected = [2399, 6590]
        self.assertEqual(result, expected)

    def test_gen_step_size(self):
        result = gen_step_size(10, 20, 2)
        expected = 5
        self.assertEqual(result, expected)

    def test_calc_range_params(self):
        step_count = 2

        # check default field - cartodb_id
        result = calc_range_params(BASEURL, step_count, self.table)
        expected = [22328022, 22328026, 2]
        self.assertEqual(result, expected)

    def test_calc_range_params1(self):
        step_count = 2

        # check another field - x
        range_field = 'x'
        result = calc_range_params(BASEURL, step_count, self.table, range_field)
        expected = [2399, 6590, 2095]
        self.assertEqual(result, expected)

    def test_check_error(self):
        query = "SELECT z, count(z) FROM %s WHERE %s = 15 AND se is Null GROUP BY z"

        # field exists - no error
        q = query % (self.table, "z")
        response = run_query(BASEURL, q)

        result = check_error(response)
        expected = False

        self.assertEqual(result, expected)

    def test_check_error2(self):
        query = "SELECT z, count(z) FROM %s WHERE %s = 15 AND se is Null GROUP BY z"

        # field does not exist - should result in an error
        q = query % (self.table, "zzzzzzz")
        response = run_query(BASEURL, q)

        result = check_error(response)
        expected = True

        self.assertEqual(result, expected)

    def test_check_error3(self):
        query = "SELECT z, count(z) FROM %s WHERE %s = 15 AND se is Null GROUP BY z"

        # test varnish error check, and JSONDecodeError
        response = '503 varnish'
        result = check_error(response)
        expected = False # Varnish error is not necessarily an indicator of failure

        self.assertEqual(result, expected)

    def test_run_query(self):
        query = "SELECT x FROM %s LIMIT 1" % self.table
        result = run_query(BASEURL, query)
        result = result.json().keys()
        expected = [u'fields', u'rows', u'total_rows', u'time']

        self.assertEqual(result, expected)

    def test_run_query1(self):
        # force query to fail
        query = "SELECT bad_field FROM %s LIMIT 1" % self.table
        result = run_query(BASEURL, query)
        result = result.json()
        expected = {u'error': [u'column "bad_field" does not exist']}

        self.assertEqual(result, expected)

    def test_run_queries(self):
        query = "SELECT x FROM %s LIMIT 1" % self.table
        result = run_queries(self.table, BASEURL, [query, query])
        result = [r.json().keys() for r in result]
        expected = [[u'fields', u'rows', u'total_rows', u'time'],
                    [u'fields', u'rows', u'total_rows', u'time']]

        self.assertEqual(result, expected)

    def test_gen_load_17_query(self):
        query = runner.ZOOMQUERY17
        sub_query = runner.ZOOMSUBQUERY17
        input_table = 'cdm_latest'
        table = 'gfw2_forma_ew'
        minid = 10
        maxid = 20
        stepsize = 5
        z = 17
        range_field = 'x'

        result = gen_load_17_query(sub_query, query, input_table,
                                   table, minid, maxid, stepsize, z, range_field)
        expected = ['INSERT INTO gfw2_forma_ew (x,y,date_array,z,iso) (SELECT x, y, array_agg(undate) as date_array, 17 as z,array_agg(iso) as iso FROM (SELECT x::int, y::int, p::int AS undate,iso FROM cdm_latest WHERE x::int >= 10 AND x::int < 15) foo GROUP BY x,y)',
                    'INSERT INTO gfw2_forma_ew (x,y,date_array,z,iso) (SELECT x, y, array_agg(undate) as date_array, 17 as z,array_agg(iso) as iso FROM (SELECT x::int, y::int, p::int AS undate,iso FROM cdm_latest WHERE x::int >= 15 AND x::int < 20) foo GROUP BY x,y)']
        self.assertEqual(result, expected)

    def test_gen_update_null_queries_sd(self):
        # test for sd field
        table = 'gfw2_forma_ew'
        minid = 10
        maxid = 20
        stepsize = 5
        z = 13
        range_field = 'x'
        query = runner.UPDATENULLSD

        result = gen_update_null_queries(table, query, minid, maxid,
                                         stepsize, z, range_field)
        expected = ['UPDATE gfw2_forma_ew SET sd = ARRAY(SELECT DISTINCT UNNEST(date_array) ORDER BY 1) WHERE x::int >= 10 AND x::int < 15 AND z::int >= 13 AND z::int < 14',
                    'UPDATE gfw2_forma_ew SET sd = ARRAY(SELECT DISTINCT UNNEST(date_array) ORDER BY 1) WHERE x::int >= 15 AND x::int < 20 AND z::int >= 13 AND z::int < 14'] 

        self.assertEqual(result, expected)

    def test_gen_update_null_queries_se(self):
        # test for se field
        table = 'gfw2_forma_ew'
        minid = 10
        maxid = 20
        stepsize = 5
        z = 13
        range_field = 'x'
        query = runner.UPDATENULLSE

        result = gen_update_null_queries(table, query, minid, maxid,
                                         stepsize, z, range_field)
        expected = ['UPDATE gfw2_forma_ew SET se = ARRAY(SELECT count(*) FROM UNNEST(date_array) d GROUP BY d ORDER BY d) WHERE x::int >= 10 AND x::int < 15 AND z::int >= 13 AND z::int < 14',
                    'UPDATE gfw2_forma_ew SET se = ARRAY(SELECT count(*) FROM UNNEST(date_array) d GROUP BY d ORDER BY d) WHERE x::int >= 15 AND x::int < 20 AND z::int >= 13 AND z::int < 14']

        self.assertEqual(result, expected)

    def test_gen_drop_index_queries(self):
        query = runner.DROPINDEX
        table = 'gfw2_forma_ew'

        result = gen_drop_index_queries(query, table)
        expected = [query % (table, 'x'),
                    query % (table, 'y'),
                    query % (table, 'z')]

        self.assertEqual(result, expected)

    def test_gen_create_index_queries(self):
        query = runner.CREATEINDEX
        table = 'gfw2_forma_ew'

        result = gen_create_index_queries(query, table)
        expected = [query % (table, 'x', table, 'x'),
                    query % (table, 'y', table,  'y'),
                    query % (table, 'z', table, 'z')]

        self.assertEqual(result, expected)

    def test_count_ok(self):
        self.assertFalse(count_ok(16, self.table, BASEURL))

    def test_count_ok1(self):
        self.assertTrue(count_ok(15, self.table, BASEURL))

    def test_count_ok2(self):
        self.assertTrue(count_ok(14, self.table, BASEURL))

    def test_nulls_ok(self):
        result = nulls_ok(15, 'se', self.table, BASEURL)
        self.assertTrue(result)

    def test_nulls_ok1(self):
        result = nulls_ok(15, 'sd', self.table, BASEURL)
        self.assertFalse(result)

    def test_nulls_ok2(self):
        result = nulls_ok(14, 'se', self.table, BASEURL)
        self.assertFalse(result)

    def test_nulls_ok3(self):
        result = nulls_ok(14, 'sd', self.table, BASEURL)
        self.assertTrue(result)

    def test_nulls_ok4(self):
        result = nulls_ok(13, 'se', self.table, BASEURL)
        self.assertTrue(result)

    def test_nulls_ok5(self):
        result = nulls_ok(13, 'sd', self.table, BASEURL)
        self.assertTrue(result)
        
    def test_zoom_ok(self):
        # all good data
        result = zoom_ok(13, self.table, BASEURL)
        self.assertTrue(result)

    def test_zoom_ok1(self):
        # has null se
        with self.assertRaises(Exception):
            zoom_ok(14, self.table, BASEURL)

    def test_zoom_ok2(self):
        # has null sd
        with self.assertRaises(Exception):
            zoom_ok(15, self.table, BASEURL)
