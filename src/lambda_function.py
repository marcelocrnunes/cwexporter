"""
AWS Lambda function. 

Need to review this code. It's ugly.... :(
"""


from cwexporter import generate_metrics_data, generate_metrics_querys, listmetrics, formater
import json, base64

def lambda_handler(event, context):
    if 'path' in event:
        if 'proxy' in event['resource']:
            p=event['path'].split('/')
            
            if len(p)>4 or len(p)==3: 
              error = { 
                  "statusCode": "422", 
                  "headers": { "Content-type": "text/plain" }, 
                  "body":"""Missing parameters. Call the API with url/<region>/<namespace>. 
                            Example: url/us-east-1/AWS/EC2 or url/us-east-1 (url/ will return all metrics for us-east-1)"""}
              return error
           
            if (len(p))==4:  
                namespace=p[2]+'/'+p[3]
                region=p[1]
                metricsquery, resultsquery = generate_metrics_querys(listmetrics(namespace=namespace, Region_name=region))
                resultsquery = generate_metrics_data(metricsquery, resultsquery, Region_name=region)
            else:
                region=p[1]
                metricsquery, resultsquery = generate_metrics_querys(listmetrics(Region_name=region))
                resultsquery = generate_metrics_data(metricsquery, resultsquery, Region_name=region)
        else:
            metricsquery, resultsquery = generate_metrics_querys(listmetrics())
            resultsquery = generate_metrics_data(metricsquery, resultsquery)
    body=''
    for i in formater(resultsquery):
        body+=i
        body+='\n'
        
    response = {
      "statusCode": "200",
      "isBase64Encoded": False,
      "headers": { "Content-type": "text/plain" },
      "body": body 
    }
    return response 