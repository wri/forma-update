#! sh
date=$1
fname="forma250_all"
rm -rf /tmp/gfw-250-site
mkdir /tmp/gfw-250-site
s3cmd get s3://forma250/gfw-site-1/* /tmp/gfw-250-site/ --force
echo "x,y,z,sd,se" > /tmp/$fname.csv
cat /tmp/gfw-250-site/part* | tr "\t" "," >> /tmp/$fname.csv
rm /tmp/$fname.zip
zip /tmp/$fname.zip /tmp/$fname.csv
s3cmd -P put /tmp/$fname.zip s3://forma250/forvizz/