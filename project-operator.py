import os
import requests
import json
import time

from os.path import dirname, join
from dotenv import load_dotenv

# Define global variables
TOKEN = os.getenv("PROJECT_TOKEN")
PROJECT_ID = os.getenv("PROJECT_ID")
OPERATION = os.getenv("OPERATION")

def run_graph_query(query, variables=None):
    GITHUB_API_URL = "https://api.github.com/graphql"
    HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github.v4+json"}
    response = requests.post(GITHUB_API_URL, json={'query': query, 'variables': variables}, headers=HEADERS)
    response.raise_for_status()
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    return response.json()

def get_field_id(field_name):
    query = """
    query($projectId: ID!) {
        node(id: $projectId) {
            ... on ProjectV2 {
                fields(first: 100) {
                    nodes {
                        ... on ProjectV2FieldCommon {
                            id
                            name
                        }
                    }
                }
            }
        }
    }
    """
    variables = {"projectId": PROJECT_ID}
    response = run_graph_query(query, variables)

    try:
        fields = response['data']['node']['fields']['nodes']
        for field in fields:
            if field['name'] == field_name:
                return field['id']
    except:
        print(f"Failure with field: {field_name}")
    return None

def remove_item(item_id):
    mutation = """
    mutation($input: DeleteProjectV2ItemInput!) {
        deleteProjectV2Item(input: $input) {
            deletedItemId
        }
    }
    """
    variables = {"input": {"itemId": item_id, "projectId": PROJECT_ID}}
    response = run_graph_query(mutation, variables)
    
    if response is None:
        print("Failed to remove item.")
        return None
    else:
        print("Item removed successfully.")
        print(response)
        return response

def update_custom_field(item_id, field_name, value):
    print("Updating custom field...")
    print(f"FIELD NAME:: {field_name}")
    print(f"VALUE NAME:: {value}")

    field_id = get_field_id(field_name)
    if not field_id:
        print(f"Field ID not found for field name: {field_name}")
        return

    elif isinstance(value, int):
        value = {"number": value} 
    elif not isinstance(value, dict):
        value = {"text": value}  # Wrap the value in a key-value object

    mutation = """
    mutation($input: UpdateProjectV2ItemFieldValueInput!) {
        updateProjectV2ItemFieldValue(input: $input) {
            projectV2Item {
                id
            }
        }
    }
    """
    variables = {
        "input": {
            "projectId": PROJECT_ID,
            "itemId": item_id,
            "fieldId": field_id,
            "value": value
        }
    }
    response = run_graph_query(mutation, variables)

    if response is None:
        print("Failed to update custom field.")
        return
    else:
        print("Custom field updated successfully.")
        return response
    
def create_draft_issue(draft_issue):
    mutation = """
    mutation CreateDraftIssue($input: AddProjectV2DraftIssueInput!) {
        addProjectV2DraftIssue(input: $input) {
            projectItem {
                id
            }
        }
    }
    """
    
    variables = {
        "input": {
            "projectId": PROJECT_ID,
            "title": draft_issue.get('title', 'Untitled Issue'),
            "body": draft_issue.get('body', '')
        }
    }
    
    response = run_graph_query(mutation, variables)
    if response is None:
        print("Failed to create draft issue.")
        return None
    else:
        print("Draft issue created successfully.")
    
    # Loop all field names in the draft issue
    for field_name, value in draft_issue.items():
        if field_name == 'title' or field_name == 'body':
            continue
        print(f"Updating field: {field_name} with value: {value}")
        update_custom_field(response['data']['addProjectV2DraftIssue']['projectItem']['id'], field_name, value)

def add_issue_to_project(issue):
    mutation = """
    mutation($input: AddProjectV2ItemByIdInput!) {
        addProjectV2ItemById(input: $input) {
            projectV2Item {
                id
            }
        }
    }
    """
    
    variables = {
        "input": {
            "projectId": PROJECT_ID,
            "contentId": issue['id']
        }
    }
    
    response = run_graph_query(mutation, variables)
    if response is None:
        print("Failed to add issue to project.")
        return None
    else:
        print("Issue added to project successfully.")

def run_query_paginated(after=None):
    query = """
    query ($projectId: ID!, $after: String) {
        node(id: $projectId) {
            ... on ProjectV2 {
                items(first: 100, after: $after) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    nodes {
                        id
                        draftissue: content {
                            ... on DraftIssue {
                                id
                                title
                                body
                            }
                        }
                        issue: content {
                            ... on Issue {
                              id
                              title
                            }
                        }
                        customField : fieldValueByName(name: """ + "\"" + PKEY + "\"" + """) {
                            ... on ProjectV2ItemFieldTextValue {
                                text
                            }
                        }
    
                    }
                }
            }
        }
    }
    """
    
    variables = {
        "projectId": PROJECT_ID,
        "after": after
    }
    response = run_graph_query(query, variables)
    return response

def get_all_items():
    all_items = []
    has_next_page = True
    after = None
    page = 1
    
    while has_next_page:
        try:
            print(f"Fetching page {page}...")
            result = run_query_paginated(after)
            
            # Check for errors in the response
            if "errors" in result:
                print(f"Errors in response: {result['errors']}")
                break
                
            items_data = result["data"]["node"]["items"]
            all_items.extend(items_data["nodes"])
            
            # Update pagination info
            has_next_page = items_data["pageInfo"]["hasNextPage"]
            after = items_data["pageInfo"]["endCursor"]
            
            print(f"Retrieved {len(items_data['nodes'])} items")
            
            # Add a small delay to avoid rate limiting
            time.sleep(1)
            page += 1
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            break
    
    return all_items

def item_exists(primary_key_value):
    all_items = get_all_items()
    for item in all_items:
        if (item.get('customField') and item['customField'].get('text') == primary_key_value):
            print(f"Item with {primary_key_value} exists.")
            return item
    print(f"Item with {primary_key_value} does not exist.")
    return None


if __name__ == "__main__":
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)

    PKEY_VALUE = os.getenv("PKEY_VALUE")
    PKEY = os.getenv("PKEY")

    if OPERATION == "getItem":
        print("Initiating getItem...")
        
        if not PKEY_VALUE:
            raise ValueError("PKEY_VALUE is required when operation is 'getItem'.")
        
        item = item_exists(PKEY_VALUE)
        if item:
            print(f"Item already exists: {item}")
        else:
            print("Item does not exist.")
            
    elif OPERATION == "createOrUpdate":
        print("Initiating createOrUpdate...")
        record = os.getenv("RECORD")
        
        if not record:
            raise ValueError("Record is required when operation is 'createOrUpdate'.")
    
        try:
            project_issue = json.loads(record)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string for RECORD.")
        
        item = item_exists(PKEY_VALUE)
        if item:
            print(f"Item already exists. Proceeding to update...")
            for key, value in project_issue.items():
                if key == PKEY:
                    continue
                update_custom_field(item.get('id'), key, value)
        else:
            print("Item does not exist.")
            create_draft_issue(project_issue)
    
    elif OPERATION == "removeItem":
        print("Initiating removeItem...")
        if not PKEY_VALUE:
            raise ValueError("PKEY_VALUE is required when operation is 'removeItem'.")
        
        item = item_exists(PKEY_VALUE)
        if item:
            item_id = item['id']
            print(item_id)
            remove_item(item_id)
            print(f"Item `{PKEY_VALUE}` removed successfully.")
        else:        
            print("Item does not exist.")
