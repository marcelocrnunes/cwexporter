from cwexporter import listmetrics, generate_metrics_data, generate_metrics_querys, formater 
from argparse import ArgumentParser
from pprint import pprint

"""
python3 src/console.py -h
usage: console.py [-h] [--region REGION] [--namespace NAMESPACE]

Region and Namespace

optional arguments:
  -h, --help            show this help message and exit
  --region REGION       Region to use
  --namespace NAMESPACE
                        Namespace to query
  --raw RAW             Raw results
                      
"""


if __name__ == "__main__" :
    
    parser = ArgumentParser(description="Region and Namespace")    
    parser.add_argument('--region', default='us-east-1', type=str, help='Region to use')
    parser.add_argument('--namespace', default='AWS/EC2', type=str, help='Namespace to query')
    parser.add_argument('--raw', action="store_true", help='Raw results')
    args = parser.parse_args()
    metricsquery, resultsquery = generate_metrics_querys(listmetrics(Region_name=args.region, namespace=args.namespace))
    resultsquery = generate_metrics_data(metricsquery, resultsquery)
    if args.raw:
        pprint(resultsquery)
    else:
        for i in formater(resultsquery) :
            print(i)
        