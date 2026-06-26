# Google Cloud Setup & Requirements

Before your application can authenticate users and access their Google Workspace data using `selander_bridge`, you must configure a project in the Google Cloud Console. 

This guide covers the exact steps required, including common pitfalls like forgetting to enable specific APIs or adding test users.

## 1. Create a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown at the top of the page and select **New Project**.
3. Name your project and click **Create**.

## 2. Enable Required APIs (Crucial Step)
Even if you have credentials, **your code will crash with a 403 Error** if you haven't explicitly enabled the APIs you plan to use.

1. In your project, go to **APIs & Services > Library**.
2. Search for and click on the APIs you need:
   - **[Google People API](https://console.developers.google.com/apis/api/people.googleapis.com/overview)** (Required for `ContactsClient`)
   - **[Google Drive API](https://console.developers.google.com/apis/api/drive.googleapis.com/overview)** (Required for `DriveClient`)
3. Click the blue **Enable** button for each one.

## 3. Configure the OAuth Consent Screen & Test Users
If you don't configure this properly, users will see an **"Access Blocked: ...has not completed the Google verification process"** error when trying to log in.

1. Go to **APIs & Services > OAuth consent screen**.
2. Choose **External** (unless you have a Google Workspace org and only want internal users).
3. Fill in the required fields (App name, support email, developer contact).
4. Under **Test users** (while your app's publishing status is "Testing"), you **must** add the exact email addresses of the users who will be running the code. Click **+ Add Users** and type their email(s).
   - *Note: If you change your Publishing Status to "In production", you won't need to add test users, but users might see a warning screen requiring them to click "Advanced -> Go to app (unsafe)".*

## 4. Create Desktop OAuth Credentials
Because `selander_bridge` runs locally without a permanent server, you need a specific type of credential.

1. Go to **APIs & Services > Credentials**.
2. Click **+ Create Credentials** and choose **OAuth client ID**.
3. Under **Application type**, select **Desktop app**. (Do not select Web application).
4. Give it a name and click **Create**.
5. Click **Download JSON** and save the file into your project. When initializing `GoogleAuthManager`, point it to this file!
