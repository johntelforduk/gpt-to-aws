# GPT to AWS
This project creates AWS infrastructure using natural language interpreted using the [OpenAI](https://openai.com/) [GPT](https://en.wikipedia.org/wiki/Generative_pre-trained_transformer) language model. Rather than [Infrastructure as Code (IaC)](https://en.wikipedia.org/wiki/Infrastructure_as_code), I refer to this as *Infrastructure as Natural Language (IaNL)*.

Current scope is limited to,
* Amazon Elastic Compute Cloud (EC2) only
* A limited range of [T3](https://aws.amazon.com/ec2/instance-types/t3/) instance types.

It uses the recently released [function calling](https://openai.com/blog/function-calling-and-other-api-updates) capability in the Chat Completions API. For a great description of how this capability works, I recommend this [video](https://youtu.be/0lOSvOoF2to).

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

One of the interesting things is that if the prompt is changed to say thet there will only be 5 players, then it usually chooses a t3.micro instance type (which has less capacity).

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
SKIP_AWS=True
AWS_ACCESS_KEY_ID=<your access key>
AWS_SECRET_ACCESS_KEY=<your secret access key>
AWS_REGION_NAME=<your preferred region>
```
Set `SKIP_AWS` to `False` if you want the program to actually create EC2 instances for you. Leave it as `True` if you just want to test the program (see what kind of EC2 it would have launched).

Then to run the program do,
```commandline
python nl_to_aws.py
```
## Costs
The program is currently configured to use the **gpt-3.5-turbo** model, which (at time of writing) has a [cost](https://openai.com/pricing) of about $0.002 per 1,000 tokens. In testing, typical conversations use about 250 tokens, which is a negligible cost. Note, new OpenAI accounts usually come with some token credits.

If you set `SKIP_AWS=False` in the `.env` file it also starts AWS EC2 instances. These will incur ongoing costs. You should ensure that you use the AWS console to terminate any un-needed instances.