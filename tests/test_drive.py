import os
import sys

from selander_bridge import GoogleAuthManager, DriveClient, SCOPE_DRIVE_READONLY

def main():
    secret_file = "client_secret_257045456484-qa159gispleepeepgnseujhtrfa59hpq.apps.googleusercontent.com.json"
    
    # We look for the file in the parent directory (project root)
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
        scopes=[SCOPE_DRIVE_READONLY],
    )

    account_key = "itslugenge96@gmail.com" 
    
    print("Initializing Drive Client...")
    print("If you haven't authorized Drive access yet, a browser window will open.")
    drive = DriveClient(auth, account=account_key)

    print("\nFetching files from Drive...")
    try:
        count = 0
        # List up to 10 files
        for file in drive.list_files(page_size=10):
            print(f"- {file.get('name')} (ID: {file.get('id')})")
            
            count += 1
            if count >= 10:
                print("... (showing max 10 files for this test) ...")
                break
                
        if count == 0:
            print("Successfully connected, but no files were found in your Drive.")
        else:
            print(f"\nSuccess! Successfully retrieved {count} files.")
            
    except Exception as e:
        print(f"\nAn error occurred while fetching Drive files: {e}")

if __name__ == "__main__":
    main()
