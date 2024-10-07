import os
import json
import requests
import xml.etree.ElementTree as ET

class AppDConfigurationBackup:

    def __init__(self, base_url, headers):
        self.base_url = base_url
        self.headers = headers

    def fetch_applications(self):
        """Fetch all applications and return their IDs and names."""
        url = f"{self.base_url}/applications"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()  # Raise an error for bad status codes
        root = ET.fromstring(response.content)
        applications = []
        for application in root.findall('application'):
            app_id = application.find('id').text
            app_name = application.find('name').text
            applications.append({'id': app_id, 'name': app_name})
    
        return applications

    def fetch_health_rules(self, app_id):
        """Fetch health rules for the given application."""
        url = f"{self.base_url}/alerting/rest/v1/applications/{app_id}/health-rules"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def fetch_actions(self, app_id):
        """Fetch actions for the given application."""
        url = f"{self.base_url}/alerting/rest/v1/applications/{app_id}/actions"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def fetch_policies(self, app_id):
        """Fetch policies for the given application."""
        url = f"{self.base_url}/alerting/rest/v1/applications/{app_id}/policies"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def save_to_file(self, app_name, data_type, data):
        """Save the provided data to a JSON file."""
        dir_path = f"./{app_name}/{data_type}/"
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, f"{data_type}.json")
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Saved {data_type} for {app_name} to {file_path}")

    def backup_configuration(self):
        """Main method to backup configuration for all applications."""
        applications = self.fetch_applications()

        for app in applications:
            app_id = app['id']
            app_name = app['name']

            print(f"Backing up configuration for {app_name}...")

            # Fetch and save health rules
            health_rules = self.fetch_health_rules(app_id)
            self.save_to_file(app_name, "health_rules", health_rules)

            # Fetch and save actions
            actions = self.fetch_actions(app_id)
            self.save_to_file(app_name, "actions", actions)

            # Fetch and save policies
            policies = self.fetch_policies(app_id)
            self.save_to_file(app_name, "policies", policies)

            # Optionally send a POST request with the collected details
            self.send_backup_data(app_name, health_rules, actions, policies)

    def send_backup_data(self, app_name, health_rules, actions, policies):
        """Send a POST request with backup data."""
        backup_data = {
            "app_name": app_name,
            "health_rules": health_rules,
            "actions": actions,
            "policies": policies,
        }
        # Define your endpoint here
        endpoint_url = "https://example.com/api/backup"  # Change to your endpoint
        response = requests.post(endpoint_url, json=backup_data)
        if response.status_code == 200:
            print(f"Successfully sent backup data for {app_name}.")
        else:
            print(f"Failed to send backup data for {app_name}: {response.text}")

def main():
    # Set up base URL and headers
    base_url = "https://abcd-ent-{appd_env}-01.saas.appdynamics.com/controller"
    headers = {
        'Authorization': 'Bearer {token}',  # Replace with actual token
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    backup_tool = AppDConfigurationBackup(base_url, headers)
    backup_tool.backup_configuration()

if __name__ == '__main__':
    main()
