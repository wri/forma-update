import unittest
from funcs import *

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
        expected = "%s WHERE cartodb_id >= %d AND cartodb_id < %d" % (query, start, end)
        self.assertEqual(result, expected)

        query = SAMPLEWHERE
        result = range_query(start, end, query, "cartodb_id")
        expected = "%s AND cartodb_id >= %d AND cartodb_id < %d" % (query, start, end)
        self.assertEqual(result, expected)

        result = range_query(start, end, query, "z")
        expected = "%s AND z >= %d AND z < %d" % (query, start, end)
        self.assertEqual(result, expected)

    def test_gen_range_queries(self):
        start, end, step = 100000, 500000, 150000
        result = gen_range_queries(start, end, step, SAMPLEQUERY, "cartodb_id")
        expected = ["SELECT * FROM table WHERE cartodb_id >= 100000 AND cartodb_id < 250000",
        "SELECT * FROM table WHERE cartodb_id >= 250000 AND cartodb_id < 400000",
        "SELECT * FROM table WHERE cartodb_id >= 400000 AND cartodb_id < 550000"]
        self.assertEqual(result, expected)

    def test_restrict_all(self):
        minid, maxid, step_size, min_z, max_z = 10, 20, 3, 15, 17
        result = restrict_all(minid, maxid, step_size, min_z, max_z, SAMPLEQUERY)

        where_model = "WHERE cartodb_id >= %d AND cartodb_id < %d AND z >= %d AND z < %d"
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

    def test_get_id(self):
        self.assertTrue(False)

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

    def test_process_zoom(self):
        self.assertTrue(False)
