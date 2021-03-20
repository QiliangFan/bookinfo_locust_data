#!/bin/bash

# in some cases, serveral data may not be available, please choose to gather previous data
cur_dir=`cd $(dirname $0);pwd`

if [ `ls $cur_dir/data|wc -w` -gt 0 ] ;
then
rm $cur_dir/data/* -rf
fi

if [ `ls $cur_dir/img|wc -w` -gt 0  ] ;
then
rm $cur_dir/img/* -rf
fi

SPAN=4h
interval=1
# ts=$(date +%s)
ts=1616169600

for code in `cat status_code.txt`
do
    python3 main.py --metric=istio_requests_total --span=$SPAN --code=$code --ts=$ts --interval $interval
done

for metric in `cat metrics.txt`
do
    python3 main.py --metric=$metric --span=$SPAN --ts=$ts --interval $interval
done

python3 main.py --node_exporter true --span=$SPAN --ts=$ts --interval $interval


python3 compute_gold_metric.py --interval $interval