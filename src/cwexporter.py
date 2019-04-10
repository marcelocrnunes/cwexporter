#!/usr/bin/python3

"""
===============
cwexport module
===============

Module for exporting cloudwatch metrics to a pure text Prometheus exposition format
To DocTest: python3 cwexporter.py -v 

Example usage: 

>>> region='us-east-1'
>>> namespace='AWS/EC2'
>>> type(listmetrics(Region_name=region, namespace=namespace))
<class 'list'>
>>> type(generate_metrics_querys(listmetrics(Region_name=region, namespace=namespace)))
<class 'tuple'>
>>> a, b = generate_metrics_querys(listmetrics(Region_name=region, namespace=namespace))
>>> type(a)
<class 'list'>
>>> type(b)
<class 'dict'>
>>> r=(generate_metrics_data(a,b, Region_name=region))
>>> type(r)
<class 'dict'>
>>> 'ApiCalls' in r.keys()
True
>>> type(r['ApiCalls'])
<class 'int'>
>>> r['ApiCalls']>=1
True
"""
import os
import sys
 
if 'LAMBDA_TASK_ROOT' in os.environ: 
    "Checking if we are running in a Lambda environment. This is needed in order to import the local boto3 version (1.9.129)."
    envLambdaTaskRoot = os.environ["LAMBDA_TASK_ROOT"]
    print("LAMBDA_TASK_ROOT env var:"+os.environ["LAMBDA_TASK_ROOT"])
    print("sys.path:"+str(sys.path))
 
    sys.path.insert(0,envLambdaTaskRoot+"/cw2prometheus")


import string 
from boto3 import client #type: ignore
from datetime import datetime, timedelta
from collections import defaultdict
from itertools import zip_longest
from random import choice
from typing import List, Dict, Tuple, DefaultDict, Iterable, Any

def randomString(stringLength: int = 10) -> str:
    """Generate a random string of fixed length
    
    >>> type(randomString(15))
    <class 'str'>
    >>> len(randomString(15))
    15
    
    """
    letters = string.ascii_lowercase
    return ''.join(choice(letters) for i in range(stringLength))

def listmetrics(namespace: str = None, Region_name: str = None) -> List:
    """List metrics from a provided namespace or all metrics for a particular region, if namespace is None
    
    >>> type(listmetrics(Region_name="us-east-1", namespace="AWS/EC2"))
    <class 'list'>
    
    """
    cloudwatch = client('cloudwatch', region_name=Region_name)
    paginator = cloudwatch.get_paginator('list_metrics')
    metrics=[]  # type: List
    if namespace is not None:
        page = paginator.paginate(Namespace=namespace) 
    else:
        page = paginator.paginate()
    for response in page:
        for metric in response['Metrics']:
            metrics.append(metric)
    return metrics
    
def generate_metrics_querys(metrics: List, period: int = 30, stats: str = 'Sum') -> Tuple[List, Dict]:
    """Generates a list and a dictionary of MetricDataQueries structures from a list of metrics. The dictionary is needed to later co-relate the Query with the Results based on the random generated Id
    
    >>> a=(generate_metrics_querys(listmetrics(Region_name="us-east-1", namespace="AWS/EC2")))
    >>> type(a)
    <class 'tuple'>
    >>> len(a)==2
    True
    
    """
    metricsquery = [] #type: List 
    resultsquery = defaultdict(list) #type: DefaultDict
    for metric in metrics:
        identity = randomString() 
        metricsquery.append({'Id': identity, 'MetricStat': {'Metric': metric, 'Period': period, 'Stat': stats} })
        resultsquery[identity].append({'query': {'MetricStat': {'Metric': metric, 'Period': period, 'Stat': stats}}})
    return metricsquery, dict(resultsquery)
    
def generate_metrics_data(metricsquery: List, resultsquery: Dict, deltaminutes: int = 5, Region_name: str = None) -> Dict:
    """Get the metrics data from the Cloudwatch GetMetricData API calls and append it to the resultsquery dictionary by their ID. Store the number of API Calls in the key ApiCalls for statistics
    
    >>> a=generate_metrics_querys(listmetrics(Region_name="us-east-1", namespace="AWS/EC2"))
    >>> d=generate_metrics_data(a[0],a[1],Region_name="us-east-1")
    >>> type(d)
    <class 'dict'>
    >>> len(d)>=1
    True

    """
    cloudwatch=client('cloudwatch', region_name=Region_name) 
    paginator = cloudwatch.get_paginator('get_metric_data')
    metricsgroup=grouper(metricsquery)
    resultsquery['ApiCalls']=0 
    for mqs in metricsgroup:
        for response in paginator.paginate(MetricDataQueries=mqs, StartTime=datetime.now()-timedelta(minutes=deltaminutes),EndTime=datetime.now()):
            for results in response['MetricDataResults']:
                resultsquery[results['Id']].append({'results':results})
        resultsquery['ApiCalls']+=1
    return resultsquery

def zip_discard_compr(*iterables: Iterable, sentinel: Any = object()) -> Any:
    """Will discard itens from a Grouper result as in to have the exact number of itens for each metricsquery list
    
    >>> args=[iter('ABCDEFGHIJLMNOPQ')] * 5
    >>> zip_discard_compr(*args)
    [['A', 'B', 'C', 'D', 'E'], ['F', 'G', 'H', 'I', 'J'], ['L', 'M', 'N', 'O', 'P'], ['Q']]
    
    """
    return [[entry for entry in iterable if entry is not sentinel]
            for iterable in zip_longest(*iterables, fillvalue=sentinel)]
            
def grouper(iterable: Iterable, n: int = 100, fillvalue: Any = None) -> Any:
    """Collect data into fixed-length chunks or blocks. In this case, we want 100 metrics queries at a time, since this is the limit for a single GetMetricData Call
    
    >>> grouper('ABCDEFG', 3)
    [['A', 'B', 'C'], ['D', 'E', 'F'], ['G']]
    """
    args = [iter(iterable)] * n
    return zip_discard_compr(*args) 
    
def formater(resultsquery: Dict) -> List:
    """The formater function will return a Prometheus exposition formatted list of strings computed from a dictionary of responses from the GetMetricData api. 
    TODO: Lots of stuff. I am not happy with accessing list by index [0] for this. Not sure if GetMetricData will return more than one list item and this will broke this function. Thinking about 
    using enumerate for the values (As I did for the datapoints/timestamps lists)
    
    >>> test=dict()
    >>> test['lvrqciqeoe']=[{'query': {'MetricStat': {'Metric': {'Namespace': 'AWS/EC2', 'MetricName': 'StatusCheckFailed_System', 'Dimensions': [{'Name': 'InstanceId', 'Value': 'i-0747590f4f554184a'}]}, 'Period': 30, 'Stat': 'Sum'}}}, {'results': {'Id': 'lvrqciqeoe', 'Label': 'StatusCheckFailed_System', 'Timestamps': [datetime(2019, 4, 5, 16, 25), datetime(2019, 4, 5, 16, 24), datetime(2019, 4, 5, 16, 23), datetime(2019, 4, 5, 16, 22)], 'Values': [0.0, 0.0, 0.0, 0.0], 'StatusCode': 'Complete'}}]
    >>> formater(test)
    ['StatusCheckFailed_System{Namespace="AWS/EC2", InstanceId="i-0747590f4f554184a"} 0.0 1554481500.0', 'StatusCheckFailed_System{Namespace="AWS/EC2", InstanceId="i-0747590f4f554184a"} 0.0 1554481440.0', 'StatusCheckFailed_System{Namespace="AWS/EC2", InstanceId="i-0747590f4f554184a"} 0.0 1554481380.0', 'StatusCheckFailed_System{Namespace="AWS/EC2", InstanceId="i-0747590f4f554184a"} 0.0 1554481320.0']
    >>> for i in formater(test): print(i)  
    ... 
    StatusCheckFailed_System{Namespace="AWS/EC2", InstanceId="i-0747590f4f554184a"} 0.0 1554481500.0
    StatusCheckFailed_System{Namespace="AWS/EC2", InstanceId="i-0747590f4f554184a"} 0.0 1554481440.0
    StatusCheckFailed_System{Namespace="AWS/EC2", InstanceId="i-0747590f4f554184a"} 0.0 1554481380.0
    StatusCheckFailed_System{Namespace="AWS/EC2", InstanceId="i-0747590f4f554184a"} 0.0 1554481320.0
    >>> 
    
    """
    formattedresults=[] #type: List
    for identiy, values in resultsquery.items():
        body=''
        if isinstance(values,list):
            metricname=values[0]['query']['MetricStat']['Metric']['MetricName']
            namespace=values[0]['query']['MetricStat']['Metric']['Namespace']
            dimensions=values[0]['query']['MetricStat']['Metric']['Dimensions']
            if isinstance(dimensions,list) and len(dimensions)>=1:
                for k in dimensions:
                    body+=f', {k["Name"]}="{k["Value"]}"'
            datapoints=values[1]['results']['Values']
            timestamps=values[1]['results']['Timestamps']
            headstring = f'{metricname}{{Namespace="{namespace}"' 
            if isinstance(datapoints,list) and len(datapoints)>=1:
                # data=str(datapoints[0])
                for index, (data, time)  in enumerate(zip(datapoints, timestamps)):
                    endingstring=f'}} {data} {time.timestamp()}'
                    formattedresults.append(headstring+body+endingstring) 
            else: 
                endingstring = f'}} ' 
                formattedresults.append(headstring+body+endingstring)
    return formattedresults
            
if __name__ == "__main__":
    
    import doctest
    doctest.testmod()