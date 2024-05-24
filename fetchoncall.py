import json
import requests
from http import HTTPStatus

# Replace with your OpsGenie API key
api_key = "YOUR_API_KEY"

def lambda_handler(event, context):
  """Fetches the name of the currently on-call user from OpsGenie API for a given schedule.

  Args:
      event: Lambda function event object containing the query parameters.
      context: Lambda function context object.

  Returns:
      A JSON response containing the on-call user's name, 
      or an error message if unsuccessful.
  """

  # Get schedule ID from query parameter
  schedule_id = event.get("queryStringParameters", {}).get("scheduleid")

  if not schedule_id:
    return {
        "statusCode": HTTPStatus.BAD_REQUEST,
        "body": json.dumps({"error": "Missing schedule ID query parameter (scheduleid)"})
    }

  # Fetch on-call user details
  on_call_user = get_on_call_user(api_key, schedule_id)

  if on_call_user:
    return {
        "statusCode": HTTPStatus.OK,
        "body": json.dumps({"name": on_call_user})
    }
  else:
    return {
        "statusCode": HTTPStatus.NOT_FOUND,
        "body": json.dumps({"error": "No user currently on call for schedule ID: {}".format(schedule_id)})
    }

def get_on_call_user(api_key, schedule_id):
  """Fetches the name of the user currently on call for a specific OpsGenie schedule.

  Args:
      api_key: OpsGenie API key.
      schedule_id: ID of the on-call schedule.

  Returns:
      The name of the on-call user, or None if an error occurs or no user is on call.
  """

  url = f"https://api.opsgenie.com/v2/schedules/{schedule_id}"
  headers = {"Authorization": f"ApiKey {api_key}"}

  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Parse JSON response
    data = json.loads(response.text)
    participants = data.get("data", {}).get("participants", [])

    # Find currently on-call user
    for participant in participants:
      if participant.get("currentlyOnCall", False):
        return participant.get("name")

  except requests.exceptions.RequestException as e:
    print(f"Error fetching on-call schedule details: {e}")
    return None

  # No currently on-call user found
  return None