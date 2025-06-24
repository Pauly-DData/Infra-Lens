import os
import json
import time
import random
from typing import Dict, List
from github import Github
import openai

def read_cdk_diff() -> Dict:
    path = 'cdk-diff.json'
    if not os.path.exists(path):
        print("::warning::cdk-diff.json not found. This might indicate that the CDK diff command failed.")
        return {"stacks": {}}

    with open(path, 'r') as f:
        content = f.read().strip()
        if not content:
            print("::warning::cdk-diff.json is empty. This might indicate that the CDK diff command failed.")
            return {"stacks": {}}
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"::warning::Failed to parse cdk-diff.json: {str(e)}")
            return {"stacks": {}}
    
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
    
    if not changes:
        return """No infrastructure changes were detected in the CDK diff. 
This could be because:
1. The CDK diff command failed to execute properly
2. There are no changes to deploy
3. The infrastructure is already up to date

Please check the GitHub Actions logs for more details about the CDK diff execution."""

    prompt = f"""Please provide a clear, concise summary of the following AWS infrastructure changes. 
Focus on the business impact and potential risks. Format the response in markdown:

Changes detected:
{chr(10).join(changes)}

Please summarize these changes in a way that would be helpful for a non-technical stakeholder to understand the impact."""

    return prompt

def get_ai_summary_with_retry(prompt: str, max_retries: int = 3) -> str:
    """Get a summary from OpenAI API with exponential backoff retry logic."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return "OpenAI API key not found in environment variables."
    
    try:
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.openai.com/v1"
        )
    except Exception as e:
        print(f"::error::Failed to initialize OpenAI client: {str(e)}")
        return f"Failed to initialize OpenAI client: {str(e)}"
    
    for attempt in range(max_retries):
        try:
            print(f"::notice::Attempting OpenAI API call (attempt {attempt + 1}/{max_retries})")
            
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
            
        except openai.RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                print(f"::warning::Rate limit hit. Waiting {wait_time:.2f} seconds before retry...")
                time.sleep(wait_time)
            else:
                print(f"::error::Rate limit exceeded after {max_retries} attempts")
                return "Rate limit exceeded. Please try again later."
                
        except openai.APIError as e:
            error_message = str(e)
            if "insufficient_quota" in error_message or "quota" in error_message.lower():
                print(f"::error::OpenAI quota exceeded: {error_message}")
                return "OpenAI API quota exceeded. Please check your billing and usage limits."
            
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"::warning::API error: {error_message}. Waiting {wait_time:.2f} seconds before retry...")
                time.sleep(wait_time)
            else:
                print(f"::error::API error after {max_retries} attempts: {error_message}")
                return f"API error: {error_message}"
                
        except Exception as e:
            print(f"::error::Unexpected error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"::warning::Waiting {wait_time:.2f} seconds before retry...")
                time.sleep(wait_time)
            else:
                return f"Failed to generate AI summary after {max_retries} attempts: {str(e)}"
    
    return "Failed to generate AI summary after all retry attempts."

def post_to_github(summary: str):
    """Post the summary as a comment on the PR."""
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("::warning::GITHUB_TOKEN not found in environment variables")
        return
    
    event_path = os.getenv('GITHUB_EVENT_PATH')
    if not event_path:
        print("::warning::GITHUB_EVENT_PATH not found in environment variables")
        return
    
    try:
        with open(event_path, 'r') as f:
            event_data = json.load(f)
        
        print(f"::notice::Event data keys: {list(event_data.keys())}")
        
        # Try to get PR number from different possible locations
        pr_number = None
        repo_name = None
        
        # Method 1: Direct pull_request event
        if 'pull_request' in event_data:
            pr_number = event_data['pull_request']['number']
            repo_name = event_data['repository']['full_name']
            print(f"::notice::Found PR from pull_request event: #{pr_number}")
        
        # Method 2: Issue event with pull_request
        elif 'issue' in event_data and event_data.get('issue', {}).get('pull_request'):
            pr_number = event_data['issue']['number']
            repo_name = event_data['repository']['full_name']
            print(f"::notice::Found PR from issue event: #{pr_number}")
        
        # Method 3: Try to get from context
        elif 'repository' in event_data:
            repo_name = event_data['repository']['full_name']
            # Try to get PR number from environment variables
            pr_number = os.getenv('GITHUB_PR_NUMBER')
            if pr_number:
                print(f"::notice::Found PR from environment variable: #{pr_number}")
        
        if not pr_number or not repo_name:
            print(f"::warning::Could not determine PR number or repository name")
            print(f"::warning::Available keys: {list(event_data.keys())}")
            print(f"::warning::Repository info: {event_data.get('repository', 'Not found')}")
            return
        
        print(f"::notice::Posting comment to PR #{pr_number} in {repo_name}")
        
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(int(pr_number))
        pr.create_issue_comment(summary)
        
        print("::notice::Successfully posted comment to PR")
        
    except Exception as e:
        print(f"::warning::Failed to post comment to GitHub: {str(e)}")
        print(f"::warning::Event path: {event_path}")
        if os.path.exists(event_path):
            try:
                with open(event_path, 'r') as f:
                    print(f"::warning::Event content: {f.read()}")
            except Exception as read_error:
                print(f"::warning::Could not read event file: {str(read_error)}")

def main():
    try:
        # Read and parse CDK diff
        diff_data = read_cdk_diff()
        
        # Generate prompt and get AI summary
        prompt = generate_prompt(diff_data)
        summary = get_ai_summary_with_retry(prompt)
        
        # Print summary to GitHub Actions log with notice formatting
        print("::notice::✅ AI Summary van CDK wijzigingen:")
        print(f"::notice::{summary}")
        
        # Post summary to PR
        post_to_github(summary)
    except Exception as e:
        print(f"::error::An error occurred: {str(e)}")
        raise

if __name__ == '__main__':
    main() 