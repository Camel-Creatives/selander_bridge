import os
import sys

from selander_bridge import GoogleAuthManager, ContactsClient, SCOPE_CONTACTS_READONLY

def main():
    secret_file = "client_secret_257045456484-qa159gispleepeepgnseujhtrfa59hpq.apps.googleusercontent.com.json"
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    secret_path = os.path.join(project_root, secret_file)
    
    if not os.path.exists(secret_path):
        print(f"Error: {secret_path} not found!")
        print("Please place the client secret JSON file in the project root.")
        sys.exit(1)

    print("Initializing Google Auth Manager...")
    # Initialize the auth manager. We only need read-only access for this test.
    auth = GoogleAuthManager(
        client_secrets_file=secret_path,
        scopes=[SCOPE_CONTACTS_READONLY],
    )

    # Use a dummy email or your actual email as the account key for token caching
    account_key = "itslugenge96@gmail.com" 
    
    print("Initializing Contacts Client...")
    print("If this is your first time, a browser window will open for you to log in.")
    contacts = ContactsClient(auth, account=account_key)

    print("\nFetching contacts...")
    try:
        # We will fetch up to 10 contacts to verify it works
        count = 0
        for person in contacts.list_contacts(page_size=10):
            names = person.get("names", [])
            email_addresses = person.get("emailAddresses", [])
            
            # Extract display name
            display_name = names[0].get("displayName") if names else "Unknown Name"
            
            # Extract primary email
            primary_email = "No Email"
            if email_addresses:
                primary_email = email_addresses[0].get("value")
                
            print(f"- {display_name} ({primary_email})")
            
            count += 1
            if count >= 10:
                print("... (showing max 10 contacts for this test) ...")
                break
                
        if count == 0:
            print("Successfully connected, but no contacts were found in your account.")
        else:
            print(f"\nSuccess! Successfully retrieved {count} contacts.")
            
    except Exception as e:
        print(f"\nAn error occurred while fetching contacts: {e}")

if __name__ == "__main__":
    main()
