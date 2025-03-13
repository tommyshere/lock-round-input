import json
import boto3

APIGW_ENDPOINT = "https://6jvamzra4m.execute-api.us-west-1.amazonaws.com/production"
dynamodb = boto3.client('dynamodb')
apigateway = boto3.client('apigatewaymanagementapi', endpoint_url=APIGW_ENDPOINT)


def main(*_, **__):
    try:
        response = dynamodb.scan(TableName="GolfNutsLiveConnections")
        connection_ids = [item['connection_id']['S'] for item in response.get('Items', [])]

        message = {
            "action": "round-start",
            "isRoundOneStart": True,
            "isRoundTwoStart": False,
            "isRoundThreeStart": False,
            "isRoundFourStart": False,
        }

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


if __name__ == "__main__":
    main()
