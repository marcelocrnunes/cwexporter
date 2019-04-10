from cwexporter import listmetrics, generate_metrics_data, generate_metrics_querys, formater 
from argparse import ArgumentParser

"""
python3 src/console.py -h
usage: console.py [-h] [--region REGION] [--namespace NAMESPACE]

Region and Namespace

optional arguments:
  -h, --help            show this help message and exit
  --region REGION       Region to use
  --namespace NAMESPACE
                        Namespace to query
                        
"""


if __name__ == "__main__" :
    
    parser = ArgumentParser(description="Region and Namespace")    
    parser.add_argument('--region', default='us-east-1', type=str, help='Region to use')
    parser.add_argument('--namespace', default='AWS/EC2', type=str, help='Namespace to query')
    args = parser.parse_args()
    metricsquery, resultsquery = generate_metrics_querys(listmetrics(Region_name=args.region, namespace=args.namespace))
    resultsquery = generate_metrics_data(metricsquery, resultsquery)
    for i in formater(resultsquery) :
        print(i)
        