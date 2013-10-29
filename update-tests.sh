#! /bin/sh
. ./yo.sh

tester() 
{
    result=$1
    expected=$2
    if [ "$result" = "$expected" ]
    then
        echo "Pass"
    else
        echo "Fail"
        echo "$result != \n$expected"
    fi
}

result=$(urlencode "SELECT * FROM yo")
expected="SELECT%20%2A%20FROM%20yo"
tester "$result" "$expected"

result=$(buildurl "https://wri-01.cartodb.com/api/v1/sql/?q=" "SELECT * FROM yo")
expected="https://wri-01.cartodb.com/api/v1/sql/?q=SELECT%20%2A%20FROM%20yo"
tester "$result" "$expected"

result=$(containswhere "asfd")
expected=0
tester "$result" "$expected"

result=$(containswhere "asfdwhereasdf")
expected=1
tester "$result" "$expected"

result=$(containswhere "asfdwhereasdfwHERE")
expected=1
tester "$result" "$expected"

result=$(containswhere "asfdWHERE")
expected=1
tester "$result" "$expected"

result=$(parsewhere "SELECT * FROM yo")
expected="SELECT * FROM yo WHERE"
tester "$result" "$expected"

result=$(parsewhere "SELECT * FROM yo WHERE id=1")
expected="SELECT * FROM yo WHERE id=1 AND"
tester "$result" "$expected"

result=$(restrictrange 1 10 "SELECT * FROM yo")
expected="SELECT * FROM yo WHERE cartodb_id>=1 AND cartodb_id<10"
tester "$result" "$expected"

result=$(restrictrange 1 10 "SELECT * FROM yo WHERE id=1")
expected="SELECT * FROM yo WHERE id=1 AND cartodb_id>=1 AND cartodb_id<10"
tester "$result" "$expected"

result=$(restrictzoom 17 "SELECT * FROM yo")
expected="SELECT * FROM yo WHERE z=17"
tester "$result" "$expected"

result=$(restrictzoom 17 "SELECT * FROM yo WHERE id=1")
expected="SELECT * FROM yo WHERE id=1 AND z=17"
tester "$result" "$expected"

result=$(rangedquery 0 1000001 250000 "SELECT * FROM yo")
expected="SELECT * FROM yo WHERE cartodb_id>=0 AND cartodb_id<250000
SELECT * FROM yo WHERE cartodb_id>=250000 AND cartodb_id<500000
SELECT * FROM yo WHERE cartodb_id>=500000 AND cartodb_id<750000
SELECT * FROM yo WHERE cartodb_id>=750000 AND cartodb_id<1000000
SELECT * FROM yo WHERE cartodb_id>=1000000 AND cartodb_id<1250000"
tester "$result" "$expected"

# range query
query="SELECT * FROM yo WHERE id=1"
api_key="myapikey"
base_url="https://wri-01.cartodb.com/api/v1/sql/?api_key=$api_key&q="
queries=$(rangedquery 0 1000001 250000 "$query")

result=$(echo "$queries" | while read q; do echo $(buildurl "$base_url" "$q"); done)
expected="https://wri-01.cartodb.com/api/v1/sql/?api_key=myapikey&q=SELECT%20%2A%20FROM%20yo%20WHERE%20id%3D1%20AND%20cartodb_id%3E%3D0%20AND%20cartodb_id%3C250000
https://wri-01.cartodb.com/api/v1/sql/?api_key=myapikey&q=SELECT%20%2A%20FROM%20yo%20WHERE%20id%3D1%20AND%20cartodb_id%3E%3D250000%20AND%20cartodb_id%3C500000
https://wri-01.cartodb.com/api/v1/sql/?api_key=myapikey&q=SELECT%20%2A%20FROM%20yo%20WHERE%20id%3D1%20AND%20cartodb_id%3E%3D500000%20AND%20cartodb_id%3C750000
https://wri-01.cartodb.com/api/v1/sql/?api_key=myapikey&q=SELECT%20%2A%20FROM%20yo%20WHERE%20id%3D1%20AND%20cartodb_id%3E%3D750000%20AND%20cartodb_id%3C1000000
https://wri-01.cartodb.com/api/v1/sql/?api_key=myapikey&q=SELECT%20%2A%20FROM%20yo%20WHERE%20id%3D1%20AND%20cartodb_id%3E%3D1000000%20AND%20cartodb_id%3C1250000"
tester "$result" "$expected"
