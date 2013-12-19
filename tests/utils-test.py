import unittest
from formaupdate.utils import *

BASEURL = "https://wri-01.cartodb.com/api/v2/sql?q="
SAMPLEQUERY = "SELECT * FROM table"
SAMPLEWHERE = "SELECT * FROM table WHERE id = 1"

class TestEverything(unittest.TestCase):

    def test_build_url(self):
        query = "SELECT count(*) FROM cdm_2013_10_24"
        result = build_url(BASEURL, query)
        self.assertEqual(result, "%s%s" % (BASEURL,
                        "SELECT%20count%28%2A%29%20FROM%20cdm_2013_10_24"))

    def test_parse_where(self):
        result = parse_where(SAMPLEQUERY)
        self.assertEqual(result, "%s WHERE" % SAMPLEQUERY )

        result = parse_where(SAMPLEWHERE)
        self.assertEqual(result, "%s AND" % SAMPLEWHERE)

    def test_range_query(self):
        start, end = 10, 20
        query = SAMPLEQUERY
        result = range_query(start, end, query, "cartodb_id")
        expected = "%s WHERE cartodb_id::int >= %d AND cartodb_id::int < %d" % (query, start, end)
        self.assertEqual(result, expected)

        query = SAMPLEWHERE
        result = range_query(start, end, query, "cartodb_id")
        expected = "%s AND cartodb_id::int >= %d AND cartodb_id::int < %d" % (query, start, end)
        self.assertEqual(result, expected)

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
        result = [get_field_val(f, BASEURL, "test_forma_update", "cartodb_id") for f in ["min", "max"]]
        expected = [22328022, 22328026]
        self.assertEqual(result, expected)

        result = [get_field_val(f, BASEURL, "test_forma_update", "x") for f in ["min", "max"]]
        expected = [2399, 6590]
        self.assertEqual(result, expected)

    def test_gen_step_size(self):
        result = gen_step_size(10, 20, 2)
        expected = 5
        self.assertEqual(result, expected)

    def test_calc_range_params(self):
        self.assertTrue(False)

    def test_check_error(self):
        self.assertTrue(False)

    def test_run_query(self):
        self.assertTrue(False)

    def test_run_queries(self):
        self.assertTrue(False)

    def test_gen_load_17_query(self):
        self.assertTrue(False)

    def test_gen_update_null_queries(self):
        self.assertTrue(False)

    def test_create_indexes(self):
        self.assertTrue(False)

    def test_run_z17(self):
        self.assertTrue(False)

    def test_count_ok(self):
        table = 'test_forma_update'

        self.assertFalse(count_ok(16, table, BASEURL))
        self.assertTrue(count_ok(15, table, BASEURL))
        self.assertTrue(count_ok(14, table, BASEURL))

    def test_nulls_ok(self):
        table = 'test_forma_update'

        result = nulls_ok(15, 'se', table, BASEURL)
        self.assertTrue(result)

        result = nulls_ok(15, 'sd', table, BASEURL)
        self.assertFalse(result)

        result = nulls_ok(14, 'se', table, BASEURL)
        self.assertFalse(result)

        result = nulls_ok(14, 'sd', table, BASEURL)
        self.assertTrue(result)

        result = nulls_ok(13, 'se', table, BASEURL)
        self.assertTrue(result)

        result = nulls_ok(13, 'sd', table, BASEURL)
        self.assertTrue(result)
        
    def test_zoom_ok(self):
        table = 'test_forma_update'

        # all good data
        result = zoom_ok(13, table, BASEURL)
        self.assertTrue(result)

        # has null se
        with self.assertRaises(Exception):
            zoom_ok(14, table, BASEURL)

        # has null sd
        with self.assertRaises(Exception):
            zoom_ok(15, table, BASEURL)

    def test_process_zoom(self):
        self.assertTrue(False)
