import boto3, json, decimal
import os


def lambda_handler(event: any, context: any):
    visit_count: int = 0

    dynamodb = boto3.resource("dynamodb")
    table_name = os.environ["TABLE_NAME"]
    table = dynamodb.Table(table_name)
    
    headers = {
   
        "Access-Control-Allow-Headers": "Accept,Accept-Language,Content-Language,Content-Type,Authorization,x-correlation-id",
        "Access-Control-Expose-Headers": "x-my-header-out",
        "Access-Control-Allow-Methods": "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
        "Access-Control-Allow-Origin": "*" }

    getrequest = table.get_item(Key={"visits": "total"})
    if "Item" in getrequest:
        visit_count = getrequest["Item"]["count"]
    
    visit_count += 1

    table.put_item(Item={"visits": "total", "count": visit_count})
    
    
    response = {
            "statusCode": 200,
            "headers": {"content-type": "application/json",
                        "Access-Control-Allow-Headers": "Accept,Accept-Language,Content-Language,Content-Type,Authorization,x-correlation-id",
                        "Access-Control-Expose-Headers": "x-my-header-out",
                        "Access-Control-Allow-Methods": "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
                        "Access-Control-Allow-Origin": "*" },
            "body":  json.dumps({"visit_count": visit_count}, default = str)
                       
    }
    
    return response 


    #class DecimalEncoder(json.JSONEncoder):    
    #    def default(self, obj):
    #        if isinstance(obj, decimal.Decimal):
    #            return int(obj)
    #        return super(DecimalEncoder, self).default(obj)