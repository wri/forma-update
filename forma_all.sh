# This script pulls in the latest FORMA data, preprocessed for this
# schema, and generates a master file on S3.

# set version
version="1.0"
threshold=50

# set up dates

rundate="2014-01-08"
start="2005-12-18"
end="2013-12-19"

# header
header="lat,lon,iso,gadm2,date"

# set working directory

basedir="/tmp/forma"
rm -rf $basedir
mkdir -p $basedir

# set readme

readme="$basedir/readme.txt"

# set paths and filenames
fname="forma-${version}-${start}-${end}"
outfile="$basedir/$fname.csv"
outzip="$basedir/forma_all.zip"
s3inputpath="s3://pailbucket/output/run-$rundate/forma-site-50/part-*"

# get the most recent file from S3

s3cmd get $s3inputpath $basedir

# generate a single file containing all alerts

# add header
echo $header > $outfile

# sort order: iso code, date, lat, lon
cat $(ls $basedir/part-*) | sort -k 3,3 -k 5,5 -k 1,1n -k 2,2n | tr "\t" "," >> $outfile

# zip it up along with a readme that includes processing date, code version

rm -rf $readme
touch $readme

echo "FORMA - Forest Monitoring for Action" >> $readme
echo "For more information, please visit http://www.GlobalForestWatch.org or the project code repository:" >> $readme
echo "http://github.com/wri/forma-clj" >> $readme
echo >> $readme; echo >> $readme;
echo "Version $version" >> $readme
echo "Date of processing: $rundate" >> $readme
echo "Dates covered: $start to $end" >> $readme
echo "Spatial resolution: ~500 meters squared, or 0.0043 decimal degrees" >> $readme
echo "Temporal resolution: 16 days" >> $readme
echo "Schema: lat,lon,iso,gadm2,date"
echo "N.B. gadm2 is the objectid for the GADM v2.0 dataset available at gadm.org and can be used to merge in data on administrative units."
echo "Threshold: $threshold percent probability"
echo >> $readme; echo >> $readme;
echo "Data are in the public domain via the CC0 license:" >> $readme
echo "http://creativecommons.org/publicdomain/zero/1.0/" >> $readme

zip --junk-paths $outzip $outfile $readme

# readme:
# mention 2005-12-19 has lots of hits bc catching up
# include processing date and version number

# put on s3 forma bucket
s3cmd put -P $outzip s3://forma/$version/
