import boto3
import botocore.config
import json
from datetime import datetime
def blog_generate(blog_topic:str)-> str:
    prompt = f"""
        <s>[INST]Human: Write a 200 words blog on the topic {blog_topic}
        Assistant:[/INST]
        """
    
    body = {
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature":0.5,
        "top_p":0.9
    }
    
    try:
        bedrock=boto3.client("bedrock-runtime", region="us-east-1", 
                             config=botocore.config.Config(read_timeout=300, retries={'max_attempts':3}))
        response = bedrock.invoke_model(body=json.dumps(body), modelId="meta.llama2-13b-chat-v1")

        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        print(response_data)
        blog_details = response_data['generation']
        return blog_details
        
    except Exception as e:
        print(e)
        return ""

def save_blog_details(s3_key, s3_bucket, generate_blog):
    s3=boto3.client('s3')

    try:
        s3.put_object(Bucket = s3_bucket, Key = s3_key, Body = generate_blog)
        print("saved_to_s3")
    except Exception as e:
        print("Error while saving")


def lambda_handler(event, context):
    # TODO implement
    event=json.loads(event['body'])
    blog_topic=event['blog_topic']
    generate_blog=blog_generate(blog_topic=blog_topic)
    
    if generate_blog:
        current_time = datetime.now().strftime('%H%M%S')
        s3_key = f"blog-output/{current_time}.txt"
        s3_bucket="aws_bedrock"
        save_blog_details(s3_key=s3_key, s3_bucket=s3_bucket, generate_blog=generate_blog)

    else:
        print("no blog")
    
    return{
        'Status':200,
        'bode':json.dumps('Blog Generated')
    }