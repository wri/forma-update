#! /bin/sh

urlencode ()
# Handle url encoding for strings (likely SQL queries).
{
    local ENCODED;
	 ENCODED=$(echo -n "$1" | \
	     perl -pe's/([^-_.~A-Za-z0-9])/sprintf("%%%02X", ord($1))/seg');
	 echo $ENCODED
}
 
buildurl ()
# Add base_url to urlencoded query string.
{
    local base_url; local encoded_query;
	 base_url="$1"
	 encoded_query=$(urlencode "$2")
	 echo "$1$encoded_query"
}

containswhere()
# Check for WHERE clause in string and return the number of lines
# WHERE appears in.
{
echo $(echo "$1" | grep --ignore-case "where" | wc -l)
}

parsewhere ()
# Check for WHERE clause in string and add AND or WHERE as appropriate
# to get needed WHERE clause. The WHERE clause is assumed to belong
# at the end of the string. Checking for WHERE only greps for the
# presence of an existing clause, but does not check the location.
#
# Arguments:
# $1: SQL query string
{
local query; local includes_where; local newquery;

query="$1"

includes_where=$(containswhere "$query")

if [ $includes_where -eq 0 ]
then
    # append WHERE to query where none exists
    newquery="$query WHERE"
else
    # append AND to existing WHERE clause
    newquery="$query AND"

fi
# return the updated query
echo "$newquery"
}

restrictrange()
# Appends WHERE SQL clause to the end of a string. It will append to
# an existing WHERE clause, or add a WHERE clause if there isn't one
# already.
#
# Arguments:
# $1: start of range (inclusive)
# $2: end of range (not inclusive)
# $3: SQL query string
{
local start; local end; local query; local newquery;

start="cartodb_id>=$1"
end="cartodb_id<$2"
query=$3
newquery=$(parsewhere "$query")
echo "$newquery $start AND $end"
}

restrictzoom()
# Restrict query to a specific zoom level.
{
z=$1
query=$2
newquery=$(parsewhere "$query")
echo "$newquery z=$z"
}

#restrictzoom 17 "SELECT * from yo"
#restrictzoom 17 "SELECT * from yo WHERE id=1"

rangedquery()
# Generate a query for a given range and step-size using curl.
# POSIX syntax hints taken from
# http://www.unix.com/showthread.php?t=120690
# Arguments:
# $1: start value
# $2: end value
# $3: step size
# $4: query
{
    local start; local end; local step; local query; local newend;
    local tempstart; local newquery; local tempend;
    
    start=$1
    end=$2
    step=$3
    query="$4"
    
    # Make range end one $step after $end in case $end is not a
    # multiple of $step. We want to hit all elements in the range, no
    # matter what.
    newend=$(expr $end + $step)

    # tempend starts at zero
    while [ $(( tempend += $step )) -le $newend ]
    do
        # initialize start variable
        tempstart=$(expr $tempend - $step)
        
        # Quotes around $query are needed to avoid losing "* FROM
        # table" when echoing new query
        newquery=$(restrictrange $tempstart $tempend "$query")

        # need to echo this as a string in case there's an asterix in
        # query a la 'SELECT * ...'. Asterix can be expanded to list
        # files in working directory.
        echo "$newquery"

    done
}

runquery()
# Run a query up to 5 times, retrying as necessary until there are
# no error messages in the response.
{
    local MAXTRIES; local query; local result; local errorcount;
    MAXTRIES=5
    query="$1"
    echo "$query"
    while [ $(( i += 1 )) -le $MAXTRIES ]
    do
        result=$(curl "$query")
        errorcount=$(echo $result | grep --ignore-case "error" | wc -l)
        if [ $errorcount -eq 0 ]
        then
            echo "Success!"
            echo "$query"
            break
        fi
            echo "Error occurred:"
            echo $result
    done
}
