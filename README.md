# GPT to AWS
This project creates AWS infrastructure using natural language interpreted using the [OpenAI](https://openai.com/) [GPT](https://en.wikipedia.org/wiki/Generative_pre-trained_transformer) language model. Rather than [Infrastructure as Code (IaC)](https://en.wikipedia.org/wiki/Infrastructure_as_code), I refer to this as *Infrastructure as Natural Language (IaNL)*.

Current scope is limited to,
* Amazon Elastic Compute Cloud (EC2) only
* A limited range of [T2](https://aws.amazon.com/ec2/instance-types/t2/) instance types.

It uses the recently released [function calling](https://openai.com/blog/function-calling-and-other-api-updates) capability in the Chat Completions API. For a great description of how this capability works, I recommend this [video](https://youtu.be/0lOSvOoF2to).

In this case, the GPT engine is told about a subset of the parameters that are available to the boto3 [run_instances](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/run_instances.html) method.

For demonstration purposes, the program has a hardcoded GPT prompt, as follows,
> Please create a new EC2 instance for me.
I'd like it to have a 1/4 TB of storage, a single CPU and 2 GBs of RAM.
After its created, I want to be able to easily get rid of this instance using the AWS console.

This automatically creates an EC2 instance with the following configuration,

| Setting | Value                                                     | Comment                                                              |
|--|-----------------------------------------------------------|----------------------------------------------------------------------|
| InstanceType | [t2.small](https://aws.amazon.com/ec2/instance-types/t2/) | A great choice, as this instance type has 1 vCPU and 2.0 GiB of RAM. |
| VolumeSize | 250 | Good, because we asked for 1/4 TB of storage. |
| DisableApiTermination | False | Great, because we said we wanted it to be easy to get rid of. |

## Installation
```commandline
pip install python-dotenv
pip install boto3
pip install openai
```
The program requires both of these,
* [OpenAI API key](https://platform.openai.com/account/api-keys)
* [AWS access key](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html)

Before running the program, create a `.env` file containing the following key/values,
```commandline
# OpenAI
OPEN_AI_KEY=<your OpenAI API key>
OPEN_AI_MODEL="gpt-3.5-turbo-0613"

# AWS
AWS_ACCESS_KEY_ID=<your access key>
AWS_SECRET_ACCESS_KEY=<your secret access key>
AWS_REGION_NAME=<your preferred region>
```
Tben to run the program do,
```commandline
python nl_to_aws.py
```
## Costs
The program is currently configured to use the **gpt-3.5-turbo** model, which (at time of writing) has a [cost](https://openai.com/pricing) of about $0.002 per 1,000 tokens. In testing, typical conversations use about 250 tokens, which is a negligible cost. Note, new OpenAI accounts usually come with some token credits.

It also starts AWS EC2 instances which will incur ongoing costs. You should ensure that you use the AWS console to terminate any un-needed instances.