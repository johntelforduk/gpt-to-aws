# GPT to AWS
This repo contains some proof of concepts for creating Amazon Web Services (AWS) infrastructure using generative AI.

## Installation
```commandline
pip install -r requirements.txt
```
**PoC 1** requires both of these keys, whereas **PoC 2** only requires the OpenAI API key.
* [OpenAI API key](https://platform.openai.com/account/api-keys)
* [AWS access key](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html)

Before running the program, create a `.env` file containing the following key/values,
```commandline
# OpenAI
OPEN_AI_KEY=<your OpenAI API key>
TEMPERATURE="0.2"

# AWS
SKIP_AWS=True
AWS_ACCESS_KEY_ID=<your access key>
AWS_SECRET_ACCESS_KEY=<your secret access key>
AWS_REGION_NAME=<your preferred region>
```
The low `TEMPERATURE` setting makes the responses from GPT more focused and deterministic. 

Set `SKIP_AWS` to `False` if you want the **PoC 1** program to actually create EC2 instances for you. Leave it as `True` if you just want to test the program (see what kind of EC2 it would have launched).

## PoC 1: Functional Calling creates infrastructure using boto3
This PoC creates AWS infrastructure using natural language interpreted using the [OpenAI](https://openai.com/) [GPT](https://en.wikipedia.org/wiki/Generative_pre-trained_transformer) language model. Rather than [Infrastructure as Code (IaC)](https://en.wikipedia.org/wiki/Infrastructure_as_code), I refer to this as *Infrastructure as Natural Language (IaNL)*.

Current scope is limited to,
* Amazon Elastic Compute Cloud (EC2) only
* A limited range of [T3](https://aws.amazon.com/ec2/instance-types/t3/) instance types.

It uses the [function calling](https://openai.com/blog/function-calling-and-other-api-updates) capability in the Chat Completions API. For a great description of how this capability works, I recommend this [video](https://youtu.be/0lOSvOoF2to).

In this case, the GPT engine is told about a subset of the parameters that are available to the boto3 [run_instances](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/run_instances.html) method.

For demonstration purposes, the program has a hardcoded GPT prompt, as follows,
> Please create a new EC2 instance for me.
I want to use it as a Minecraft Bedrock server for up to 25 concurrent players. Please balance performance and cost.
I'd also like it to have a 1/4 TB of storage.
After its created, I want to be able to easily get rid of this instance using the AWS console.

This automatically creates an EC2 instance with the following configuration,

| Setting | Value                                                      | Comment                                                                                                                                                                      |
|--|------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| InstanceType | [t3.medium](https://aws.amazon.com/ec2/instance-types/t3/) | This instance type has 2 vCPUs and 4 GB of RAM. Advice online is that 4 GB is the minimum for 25 users on a Bedrock server - so this instance type seems like a good choice. |
| VolumeSize | 250                                                        | Good, because we asked for 1/4 TB of storage.                                                                                                                                |
| DisableApiTermination | False                                                      | Good, because we said we wanted it to be easy to get rid of.                                                                                                                 |

If the prompt is changed to say that there will only be 5 players, then it usually chooses a t3.micro instance type (which has less capacity).


Then to run the program do,
```commandline
python nl_to_aws.py
```

### Costs
This PoC is currently configured to use the **gpt-3.5-turbo** model, which (at time of writing) has a [cost](https://openai.com/pricing) of about $0.002 per 1,000 tokens. In testing, typical conversations use about 250 tokens, which is a negligible cost. Note, new OpenAI accounts usually come with some token credits.

If you set `SKIP_AWS=False` in the `.env` file it also starts AWS EC2 instances. These will incur ongoing costs. You should ensure that you use the AWS console to terminate any un-needed instances.

## PoC 2: High Level Architecture diagram to IaC

This PoC use the **gpt-4-vision-preview** model. It is given this prompt,
> Here is a high level architecture diagram for a system.
The system will be deployed to Amazon Web Services (AWS). 
You must generate an AWS CloudFormation template for the system. 
I will then use your CloudFormation code to generate the infrastructure.
Ensure that your CloudFormation template is valid.
If in doubt about correct configurations to use for AWS services, please follow AWS Well Architected guidelines.

It is also given this image in the prompt,
![HLA diagram](./hla.jpg)

Then to run the program do,
```commandline
python hla_to_iac.py
```

And here is the response from GPT,

_Creating an AWS CloudFormation template from a high-level architecture diagram involves detailing AWS resource declarations in YAML or JSON format. The diagram you have provided includes a VPC, a Lambda Function, an API Gateway, and a DynamoDB table._

_Please remember that an actual CloudFormation template would need much more detailed configuration parameters, resource properties, and possible additional resources such as IAM roles for permissions, depending on the specific use case. Since I don't have the option to code directly, I'll provide you with a pseudo CloudFormation YAML template to illustrate what components you would start with._

_Below is a simplified template example in YAML that corresponds to the architecture diagram you've provided:_

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  MyVPC:
    Type: AWS::EC2::VPC
    Properties:
      # Specify VPC configuration such as CIDR Block, enableDnsSupport, etc.

  MyLambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      Handler: index.handler
      Role: !GetAtt LambdaExecutionRole.Arn
      Code:
        # Define the source code location
      Runtime: nodejs12.x
      VpcConfig:
        SecurityGroupIds: [!Ref LambdaSecurityGroup]
        SubnetIds: [!Ref SubnetA, !Ref SubnetB]
        # Configure the Subnet and security groups as needed

  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      # Define the IAM Role and its policies that allows Lambda to manage resources

  LambdaSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      # Define security group rules and VPC association

  MyDynamoDBTable:
    Type: AWS::DynamoDB::Table
    Properties:
      AttributeDefinitions:
        - AttributeName: "id"
          AttributeType: "S"
      KeySchema:
        - AttributeName: "id"
          KeyType: "HASH"
      BillingMode: PAY_PER_REQUEST
      TableName: "Customers"

  MyApiGateway:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: "CustomerDetailsAPI"
      # Additional API Gateway configuration

  MyLambdaApiGatewayIntegration:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref MyApiGateway
      ResourceId: !GetAtt MyApiGateway.RootResourceId
      HttpMethod: ANY
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub
          - "arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${MyLambdaFunction.Arn}/invocations"
          - {}
        IntegrationResponses:
          - StatusCode: 200

Outputs:
  ApiGatewayUrl:
    Description: "URL of the API Gateway"
    Value: !Sub
      - "https://${MyApiGateway}.execute-api.${AWS::Region}.amazonaws.com/Prod/"
      - {}
```
_This is a basic template and doesn't represent a fully-fledged AWS infrastructure deployment. Here's a checklist you'll need to consider for a complete setup_:

- _Define the VPC CIDR block and other VPC properties._
- _Define Lambda Function details such as execution role, source code (S3 bucket or inline), environment variables, etc._
- _Specify the IAM role and policy for Lambda execution._
- _Specify Lambda security group details, and any specific rules needed._
- _Define DynamoDB table properties such as attribute definitions, key schema, indexes, and any required throughputs or billing mode._
- _Define the API Gateway resources, methods, stages, and integration with Lambda._
- _Insert Lambda permission to allow the API Gateway to invoke the Lambda function._
- _Optionally define outputs for endpoints, ARNs, etc._
- _Consider any necessary security measures such as encryption, logging, and monitoring._

_Keep in mind, creating a stacked architecture in an actual AWS account will require a lot of security and design considerations, which are beyond the scope of this simplified example._
