import os
import json

def load_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading file {file_path}: {e}")
        return None

def create_payload_for_subfolder(subfolder_path):
    actions_path = os.path.join(subfolder_path, 'actions', 'action.json')
    health_rules_path = os.path.join(subfolder_path, 'health_rules', 'healthrule.json')
    policies_path = os.path.join(subfolder_path, 'policies', 'policy.json')

    actions = load_json_file(actions_path)
    health_rules = load_json_file(health_rules_path)
    policies = load_json_file(policies_path)

    payload = {
        "actions": [],
        "healthRules": [],
        "policies": []
    }

    if actions:
        for action in actions:
            payload["actions"].append({
                "actionType": action['actionType'],
                "emails": action.get('emails', []),
                "cc": action.get('cc', []),
                "bcc": action.get('bcc', []),
                "emailVersion": action.get('emailVersion', 1),
                "timeZone": action.get('timeZone', "UTC"),
                "name": action['name']
            })

    if health_rules:
        for health_rule in health_rules:
            payload["healthRules"].append({
                "name": health_rule['name'],
                "enabled": health_rule['enabled'],
                "useDataFromLastNMinutes": health_rule['useDataFromLastNMinutes'],
                "waitTimeAfterViolation": health_rule['waitTimeAfterViolation'],
                "scheduleName": health_rule['scheduleName'],
                "affects": health_rule['affects'],
                "evalCriterias": health_rule['evalCriterias']
            })

    if policies:
        for policy in policies:
            policy_entry = {
                "name": policy['name'],
                "enabled": policy['enabled'],
                "executeActionsInBatch": policy['executeActionsInBatch'],
                "actions": [],
                "events": policy['events'],
                "selectedEntities": policy['selectedEntities']
            }

            for action in policy.get('actions', []):
                action_name = action['actionName']
                if any(act['name'] == action_name for act in actions):
                    policy_entry["actions"].append({
                        "actionType": action['actionType'],
                        "emailVersion": action.get('emailVersion', 1),
                    })
                else:
                    print(f"Warning: Action '{action_name}' not found in actions.")

            if 'events' in policy:
                health_rule_events = policy['events'].get('healthRuleEvents', {})
                health_rules_list = health_rule_events.get('healthRules', [])
                policy_entry['healthRules'] = health_rules_list

            payload["policies"].append(policy_entry)

    return payload

def process_root_folder(root_folder):
    for subfolder in os.listdir(root_folder):
        subfolder_path = os.path.join(root_folder, subfolder)
        if os.path.isdir(subfolder_path):
            print(f"Processing folder: {subfolder_path}")
            payload = create_payload_for_subfolder(subfolder_path)
            if payload:
                send_payload_to_endpoints(payload)

def send_payload_to_endpoints(payload):
    import requests

    endpoints = {
        "actions": "",
        "healthRules": "",
        "policies": ""
    }
	headers = {}

    for key in endpoints:
        try:
            response = requests.post(endpoints[key], json=payload[key])
            response.raise_for_status()  # Raise an error for bad responses
            print(f"Successfully posted {key} for payload.")
        except requests.exceptions.RequestException as e:
            print(f"Error posting {key}: {e}")

if __name__ == "__main__":
    root_folder = "root_folder"
    process_root_folder(root_folder)
