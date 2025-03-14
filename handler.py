import os
import json
import boto3
import pytz

from datetime import datetime

DYNAMO_CACHE = os.getenv("DYNAMO_CACHE")
APIGW_ENDPOINT = os.getenv("APIGW_ENDPOINT")

dynamodb = boto3.resource("dynamodb")
dynamo_conn = boto3.client("dynamodb")
apigateway = boto3.client("apigatewaymanagementapi", endpoint_url=APIGW_ENDPOINT)


def main(*_, **__):
    try:
        cache = dynamodb.Table(DYNAMO_CACHE)
        tournament = get_tournament(cache)

        tourn_tz = pytz.timezone(tournament["tournament_tz"])
        tourn_dttm = datetime.now(tourn_tz)
        weekday = tourn_dttm.weekday()

        message = {
            "action": "round-start",
            "isRoundOneStart": weekday >= 3,
            "isRoundTwoStart": weekday >= 4,
            "isRoundThreeStart": weekday >= 5,
            "isRoundFourStart": weekday >= 6,
        }

        # Farmer's Insurance
        # message = {
        #     "action": "round-start",
        #     "isRoundOneStart": weekday >= 2,
        #     "isRoundTwoStart": weekday >= 3,
        #     "isRoundThreeStart": weekday >= 4,
        #     "isRoundFourStart": weekday >= 5,
        # }

        response = dynamo_conn.scan(TableName="GolfNutsLiveConnections")
        connection_ids = [item['connection_id']['S'] for item in response.get('Items', [])]

        for connection_id in connection_ids:
            try:
                apigateway.post_to_connection(
                    Data=json.dumps(message).encode('utf-8'), ConnectionId=connection_id
                )
            except Exception as e:
                print(f"Failed to send message to {connection_id}: {e}")

        return {
            "statusCode": 200,
            "body": "Message sent to all connected clients!"
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }


def get_tournament(cache):
    response = cache.get_item(Key={"cache_id": "current"})
    tournament = response.get("Item")
    return tournament


if __name__ == "__main__":
    main()
