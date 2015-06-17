big_file=$1
length=1500000
prefix=forma250_
tail -n +2 $big_file | split -l $length - $prefix
for file in $prefix*
do
    head -n 1 $big_file > tmp_file
    cat $file >> tmp_file
    mv -f tmp_file $file
done