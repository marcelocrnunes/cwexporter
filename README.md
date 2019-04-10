# cwexporter
An API to export Cloudwatch Metrics to Prometheus exposition format


## to deploy: 

Needs SAM https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html

```
aws s3 mb s3://BUCKETNAME
sam package --template-file packaged.yaml --output-template-file template.yaml --s3-bucket BUCKETNAME
sam deploy --template-file template.yaml --stack-name cwexportertest --capabilities CAPABILITY_IAM --region us-east-1
```


## important: 

The API created will be public. Please, verify auth methods for your API, for example: 

https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-control-access-to-api.html

https://github.com/awslabs/serverless-application-model/tree/master/examples/apps/api-gateway-authorizer-python

https://github.com/awslabs/serverless-application-model/tree/master/examples/2016-10-31/api_lambda_request_auth


## Authors

* **Marcelo Nunes** - ** - [marcelocrnunes](https://github.com/marcelocrnunes)

## License

This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details

