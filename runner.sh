#! /bin/sh
. ./update.sh

output_file="/tmp/queries.txt"
rm $output_file
table="gfw2_forma_ew"
base_url="https://wri-01.cartodb.com/api/v2/sql?api_key=$api_key&q="
base_zoom=17
step_count=10

# get min and max cartodb_ids and calculate stepsize

query="SELECT min(cartodb_id) FROM gfw2_forma_ew"
url=$(buildurl "$base_url" "$query")
#min_id=$(curl "$url" | grep -o "[0-9]*" | tail -n 1)

query="SELECT max(cartodb_id) FROM gfw2_forma_ew"
url=$(buildurl "$base_url" "$query")
#max_id=$(curl "$url" | grep -o "[0-9]*" | tail -n 1)

#temp=$(expr $max_id - $min_id)
#step_size=$(expr $temp / $step_count)

min_id=14265057
max_id=20125540
step_size=586048
# misc. preliminary queries

#
echo "ADD QUERY FOR ADDING NEW DATA TO TABLE, PLUS INDEXING"

##################################
# update null columns for z = 17 #
##################################
query="UPDATE $table SET sd = ARRAY(SELECT DISTINCT UNNEST(date_array) ORDER BY 1) WHERE sd IS null"
queries=$(restrictzoom $base_zoom "$query")
queries=$(rangedquery $min_id $max_id $step_size "$queries")
exportqueries "$output_file" "$base_url" "$queries"

query="UPDATE $table SET se = ARRAY(SELECT count(*) FROM UNNEST(date_array) d GROUP BY d ORDER BY d) WHERE se IS null"
queries=$(restrictzoom $base_zoom "$query")
queries=$(rangedquery $min_id $max_id $step_size "$queries")
exportqueries "$output_file" "$base_url" "$queries"

###############
# run zoom 16 #
###############

subquery="SELECT floor(x/2) AS x, floor(y/2) AS y, unnest(date_array) AS undate FROM $table WHERE z = $(expr $z + 1)"
queries=$(rangedquery $min_id $max_id $step_size "$subquery")
echo "$queries" | while read q;
do
    mainquery="INSERT INTO $table (x,y,date_array,z) (SELECT x, y, array_agg(undate) AS date_array, $z AS z FROM ($q) foo GROUP BY x,y)"
    exportqueries "$output_file" "$base_url" "$mainquery"
done

##################################
# update min and max cartodb_ids #
##################################

query="SELECT min(cartodb_id) FROM gfw2_forma_ew"
url=$(buildurl "$base_url" "$query")
#min_id=$(curl "$url" | grep -o "[0-9]*" | tail -n 1)

query="SELECT max(cartodb_id) FROM gfw2_forma_ew"
url=$(buildurl "$base_url" "$query")
#max_id=$(curl "$url" | grep -o "[0-9]*" | tail -n 1)

#temp=$(expr $max_id - $min_id)
#step_size=$(expr $temp / $step_count)

###########################
# update z16 null columns #
###########################
z=16
query="UPDATE $table SET sd = ARRAY(SELECT DISTINCT UNNEST(date_array) ORDER BY cartodb_id)"
queries=$(restrictzoom $z "$query")
queries=$(rangedquery $min_id $max_id $step_size "$queries")
exportqueries "$output_file" "$base_url" "$queries"

z=16
query="UPDATE $table SET se = ARRAY(SELECT count(*) FROM UNNEST(date_array) d GROUP BY d ORDER BY d)"
queries=$(restrictzoom $z "$query")
queries=$(rangedquery $min_id $max_id $step_size "$queries")
exportqueries "$output_file" "$base_url" "$queries"

######################
# Run for zooms 15-7 #
######################


echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
echo "When done testing, make sure queries for min and max ids are uncommented"
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
