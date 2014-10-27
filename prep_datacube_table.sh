#! sh
date=$1
fname="gfw2_forma_latest"
rm -rf /tmp/gfw-site
mkdir /tmp/gfw-site
s3cmd get s3://pailbucket/output/run-$date/gfw-site/* /tmp/gfw-site/ --force
echo "x,y,z,sd,se" > /tmp/$fname.csv
cat /tmp/gfw-site/part* | tr "\t" "," >> /tmp/$fname.csv
rm /tmp/$fname.zip
zip /tmp/$fname.zip /tmp/$fname.csv
s3cmd -P put /tmp/$fname.zip s3://forvizz/