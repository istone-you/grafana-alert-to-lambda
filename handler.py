import json
import os
import base64
import boto3

client = boto3.client('ecs')

def lambda_handler(event, context):
    try:
        headers = event.get("headers", {})
        grafana_authorization = headers.get("authorization")

        username = os.environ['USERNAME']
        password = os.environ['PASSWORD']

        credentials = f"{username}:{password}".encode("utf-8")
        encoded_credentials = base64.b64encode(credentials).decode("utf-8")
        lambda_authorization = f"Basic {encoded_credentials}"

        # ユーザー名とパスワードが一致している場合正常に動作
        if grafana_authorization == lambda_authorization:

            print("認証に成功しました。")

            # GrafanaからのデータからECSクラスター名を取得
            grafana = json.loads(event["body"])
            ecs_cluster = grafana["alerts"][0]["labels"]["ecs_cluster"]

            # クラスター名からECSインスタンスを取得
            list_instance = client.list_container_instances(
                cluster = ecs_cluster,
            )

            instance_arn = list_instance['containerInstanceArns'][0]

            # ECSインスタンスIDを取得
            describe_instance = client.describe_container_instances(
                cluster=ecs_cluster,
                containerInstances=[
                    instance_arn
                ]
            )

            instance_id = describe_instance['containerInstances'][0]['ec2InstanceId']

            print(instance_id)

            # ECSインスタンスを再起動
            # response = ec2.reboot_instances(
            #     InstanceIds=[
            #         instance_id['containerInstances'][0]['ec2InstanceId']
            #     ]
            # )

        else:
            print("認証に失敗しました。")

    except Exception as e:
        print("エラーが発生しました。", e)

    # エラーの場合Grafanaはアラートを送り続けるので認証に失敗しても200を返す
    return {
        'statusCode': 200
    }
