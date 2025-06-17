import os
import json
from typing import Dict, List
from github import Github
import openai

def read_cdk_diff() -> Dict:
    path = ' cdk-diff.json'
    if not os.pat_exists(path):
        raise FileNotFoundError(f"{path} not found")
    
    with open('cdk-diff.json', 'r') as f:
        content = f.read().strip()
        if not content:
            raise ValueError("CDK diff file is empty")
        return json.loads(content)

def generate_prompt(diff_data: Dict) -> str:
    """Generate a prompt for the OpenAI API based on CDK diff data."""
    changes = []
    
    # Process stack changes
    for stack_name, stack_data in diff_data.get('stacks', {}).items():
        if stack_data.get('create'):
            changes.append(f"Stack '{stack_name}' will be created")
        if stack_data.get('update'):
            changes.append(f"Stack '{stack_name}' will be updated")
        if stack_data.get('destroy'):
            changes.append(f"Stack '{stack_name}' will be destroyed")
            
        # Process resource changes
        for resource_id, resource_data in stack_data.get('resources', {}).items():
            if resource_data.get('create'):
                changes.append(f"Resource '{resource_id}' will be created in stack '{stack_name}'")
            if resource_data.get('update'):
                changes.append(f"Resource '{resource_id}' will be updated in stack '{stack_name}'")
            if resource_data.get('destroy'):
                changes.append(f"Resource '{resource_id}' will be destroyed in stack '{stack_name}'")
            if resource_data.get('replace'):
                changes.append(f"Resource '{resource_id}' will be replaced in stack '{stack_name}'")
    
    prompt = f"""Please provide a clear, concise summary of the following AWS infrastructure changes. 
Focus on the business impact and potential risks. Format the response in markdown:

Changes detected:
{chr(10).join(changes)}

Please summarize these changes in a way that would be helpful for a non-technical stakeholder to understand the impact."""

    return prompt

def get_ai_summary(prompt: str) -> str:
    """Get a summary from OpenAI API."""
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert AWS infrastructure architect who can explain complex infrastructure changes in simple terms."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    return response.choices[0].message.content

def post_to_github(summary: str):
    """Post the summary as a comment on the PR."""
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("Error: GITHUB_TOKEN not found in environment variables")
        return
    
    event_path = os.getenv('GITHUB_EVENT_PATH')
    if not event_path:
        print("Error: GITHUB_EVENT_PATH not found in environment variables")
        return
    
    with open(event_path, 'r') as f:
        event_data = json.load(f)
        pr_number = event_data['pull_request']['number']
        repo_name = event_data['repository']['full_name']
    
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(summary)

def main():
    # Read and parse CDK diff
    diff_data = read_cdk_diff()
    
    # Generate prompt and get AI summary
    prompt = generate_prompt(diff_data)
    summary = get_ai_summary(prompt)
    
    # Print summary to GitHub Actions log with notice formatting
    print("::notice::CDK Changes Summary")
    print(f"::notice::{summary}")
    
    # Post summary to PR
    post_to_github(summary)

if __name__ == '__main__':
    main() 