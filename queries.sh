# runquery "https://wri-01.cartodb.com/api/v1/sql/?api_key=0e5365cb1a299778e9df9c7bf6db489af8aa08e1&q=SET%20statement_timeout%20TO%200"

# runquery "https://wri-01.cartodb.com/api/v1/sql/?api_key=0e5365cb1a299778e9df9c7bf6db489af8aa08e1&q=SET%20statement_timeout%20TO%2010000000000"



# restrict by cartodb
table="yo"; z=17; echo "UPDATE $table SET sd = ARRAY(SELECT DISTINCT UNNEST(date_array) ORDER BY 1) WHERE sd IS null" # WHERE z = $z AND 

# restrict by cartodb_id
table="yo"; z=17; echo "UPDATE $table SET se = ARRAY(SELECT count(*) FROM UNNEST(date_array) d GROUP BY d ORDER BY d) WHERE se IS null" # z = $z AND

# cross fingers - could possibly insert a where clause into subquery
table="yo"; z=16; echo "INSERT INTO $table (x,y,date_array,z) (SELECT x, y, array_agg(undate) AS date_array, $z AS z FROM (SELECT floor(x/2) AS x, floor(y/2) AS y, unnest(date_array) AS undate FROM $table WHERE z $(expr $z + 1)) foo GROUP BY x,y)"

# restrict by cartodbid
table="yo"; z=16; echo "UPDATE $table SET sd = ARRAY(SELECT DISTINCT UNNEST(date_array) ORDER BY 1)" # WHERE z = $z
table="yo"; z=16; echo "UPDATE $table SET se = ARRAY(SELECT count(*) FROM UNNEST(date_array) d GROUP BY d ORDER BY d)" # WHERE z = $z

# cross fingers - could possibly insert a where clause into subquery
table="yo"; z=15; echo "INSERT INTO $table (x,y,date_array,z) (SELECT x, y, array_agg(undate) as date_array, $z as z FROM (SELECT floor(x/2) as x, floor(y/2) as y, unnest(date_array) AS undate FROM gfw2_forma_ew WHERE z = $(expr $z + 1)) foo GROUP BY x,y)"

# restrict by zoom for zoom 16->6 and by cartodb_id
table="yo"; z=16; echo "UPDATE $table SET sd = ARRAY(SELECT DISTINCT UNNEST(date_array) ORDER BY 1)" # WHERE z < $z
table="yo"; z=16; echo "UPDATE $table SET se = ARRAY(SELECT count(*) FROM UNNEST(date_array) d GROUP BY d ORDER BY d)" # WHERE z < $z

