#!/bin/bash

cur_dir=`cd $(dirname $0);pwd`

if [ `ls $cur_dir/data|wc -w` -gt 0 ] ;
then
rm $cur_dir/data/* -rf
fi

python3 get_data.py --metric=istio_requests_total --span=10m --code=200




