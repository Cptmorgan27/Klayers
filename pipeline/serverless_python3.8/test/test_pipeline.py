import boto3

import json
import time
from datetime import datetime


def execute_sf(sf_arn, input):
    """

    :param sf_arn: ARN of the step function to invoke and run
    :param input: Input into step function as a dict
    :return: Status of Step function ('SUCCEEDED'|'FAILED'|'TIMED_OUT'|'ABORTED')
    """

    session = boto3.Session(profile_name='KlayersDev')
    sf_client = session.client('stepfunctions', region_name='ap-southeast-1')

    unique_execution_name = f"test-{datetime.now().isoformat()[:-7]}".replace(":", "")
    response = sf_client.start_execution(
        stateMachineArn=sf_arn,
        name=unique_execution_name,
        input=input
    )

    execution_arn = response.get('executionArn')

    while True:

        response = sf_client.describe_execution(
            executionArn=execution_arn
        )

        if response.get('status') == "RUNNING":
            time.sleep(2)
            print("Step Function Still Running")
        else:
            break

    return response.get('status')


def get_pipeline_arn(step_function_name_endswith='pipelineArn'):

    """

    return: the arn of the specified pipeline ending with
    """
    session = boto3.Session(profile_name='KlayersDev')
    client = session.client('cloudformation', region_name='ap-southeast-1')

    response = client.describe_stacks(
        StackName='kl-Klayers-defaultp38'
    )

    sf_arn = [output for output in response['Stacks'][0]['Outputs']
              if output.get('OutputKey').endswith(step_function_name_endswith)][0]['OutputValue']

    return sf_arn


def test_pipeline():
    pipeline_arn=get_pipeline_arn('pipelineArn')

    # Install requests
    input = json.dumps({"package": "requests"})
    assert execute_sf(sf_arn=pipeline_arn, input=input) == "SUCCEEDED"

    # Install idna
    input = json.dumps({"package": "idna"})
    assert execute_sf(sf_arn=pipeline_arn,
                      input=input) == "SUCCEEDED"

    # Install bad package
    input = json.dumps({"package": "bad_package_sdakksdl231"})
    assert execute_sf(sf_arn=pipeline_arn,
                      input=input) == "FAILED"
