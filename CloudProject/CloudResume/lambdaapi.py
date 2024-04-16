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

    getrequest = table.get_item(Key={"viewcounts": "0"})
    if "Item" in getrequest:
        visit_count = getrequest["Item"]["count"]
    
    visit_count += 1

    table.put_item(Item={"viewcounts": "0", "count": visit_count})
    
    class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, decimal.Decimal):
                return int(obj)
            return super(DecimalEncoder, self).default(obj)
    
    response = {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Headers": "Accept,Accept-Language,Content-Language,Content-Type,Authorization,x-correlation-id",
                        "Access-Control-Expose-Headers": "x-my-header-out",
                        "Access-Control-Allow-Methods": "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
                        "Access-Control-Allow-Origin": "*" },
            "body":  visit_count,
                       
    }
    
    return json.loads(json.dumps(response, default=str)), 