# GitHub Project CRUD Operator

A GitHub Action for managing items in GitHub Projects (v2) through CRUD operations - Create, Read, Update, and Delete items with custom fields.

## Features

- **Find items** in a GitHub Project by primary key
- **Create new draft issues** in a GitHub Project with custom fields
- **Update existing items** with new field values
- **Remove items** from a GitHub Project
- **Add issues** to a GitHub Project

## Setup

To use this action, you'll need:

1. A GitHub Personal Access Token with Projects permissions
2. The GraphQL node ID of your GitHub Project (v2)
3. A custom field in your Project to use as a primary key

You can find your GitHub Project's GraphQL node ID using the [GitHub GraphQL Explorer](https://docs.github.com/en/graphql/overview/explorer). After logging in, run a query like the one below, replacing `user` with your username or organization name and `number` with your project number (visible in the project URL):

```graphql
query {
  user(login: "your-username") {  # Or organization(login: "your-org")
    projectV2(number: 1) {  # Replace with your project number
      id  # This is the GraphQL node ID you need
      title
    }
  }
}
```

The `id` field in the response contains the GraphQL node ID you'll need for the project_id input.

## Inputs

| Input | Description | Required |
|-------|-------------|----------|
| `token` | GitHub personal access token with project permissions | Yes |
| `project_id` | GitHub Project v2 ID (GraphQL node ID) | Yes |
| `operation` | Operation to perform (`getItem`, `createOrUpdate`, `removeItem`) | Yes |
| `primary_key_field` | Primary key field name in the GitHub Project | Yes |
| `primary_key_value` | Value of primary key to lookup | Yes |
| `record` | JSON string representing the record (for createOrUpdate) | Only for createOrUpdate |
| `issue_id` | Issue ID to be added to the GitHub Project | Only for addItem |

## Outputs

| Output | Description |
|--------|-------------|
| `result` | Result of the operation (JSON string) |
| `success` | Boolean indicating if the operation was successful |
| `message` | Message describing the result of the operation |
| `item_id` | ID of the affected item (if applicable) |

## Usage Examples

### Finding an Item

```yaml
- name: Find item in GitHub Project
  uses: mageroni/project-crud-operator@v1
  with:
    token: ${{ secrets.PROJECT_TOKEN }}
    project_id: ${{ vars.PROJECT_ID }}
    operation: getItem
    primary_key_field: "Ticket ID"
    primary_key_value: "PROJ-123"
```   

### Creating or Updating an Item

```yaml
- name: Create or update item
  uses: mageroni/project-crud-operator@v1
  with:
    token: ${{ secrets.PROJECT_TOKEN }}
    project_id: ${{ vars.PROJECT_ID }}
    operation: createOrUpdate
    primary_key_field: "Ticket ID"
    primary_key_value: "PROJ-123"
    record: '{"title":"New Feature Request","body":"This is the description","Ticket ID":"PROJ-123","Status":"Backlog","Priority":"High"}'
```

### Removing an Item

```yaml
- name: Remove item from project
  uses: mageroni/project-crud-operator@v1
  with:
    token: ${{ secrets.PROJECT_TOKEN }}
    project_id: ${{ vars.PROJECT_ID }}
    operation: removeItem
    primary_key_field: "Ticket ID"
    primary_key_value: "PROJ-123"
```

### Adding an Item

```yaml
- name: Add item to project
  uses: mageroni/project-crud-operator@v1
  with:
    token: ${{ secrets.PROJECT_TOKEN }}
    project_id: ${{ vars.PROJECT_ID }}
    operation: addItem
    primary_key_field: "Ticket ID"
    primary_key_value: "PROJ-123"
    issue_id: 1
```

## Important Notes

### Note 1. Record Format for createOrUpdate

When using the createOrUpdate operation, the record parameter should be a JSON string with:

- `title`: Title for the draft issue (required for new items)
- `body`: Description for the draft issue (optional)
- Your custom fields as key-value pairs

Example record:

```json
{
  "title": "New Feature Request",
  "body": "Detailed description of the feature",
  "Ticket ID": "PROJ-123",
  "Status": "Backlog",
  "Priority": "High",
  "Points": 5
}
```

### Note 2. Draft Issues

When creating new items with createOrUpdate, this action creates draft issues in your GitHub Project, not regular GitHub issues.

### Note 3. Primary Key Requirements

The primary_key_field and primary_key_value must be provided in all operations:

For getItem: Used to search for the item
For createOrUpdate: Used as an identifier for the new or existing item
For removeItem: Used to find the item to delete

## License

This project is licensed under the MIT License - see the LICENSE file for details.