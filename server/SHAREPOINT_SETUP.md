# SharePoint Integration Setup Guide

This guide explains how to configure the application to store uploaded files in SharePoint instead of the local filesystem.

## Prerequisites

1. **Azure AD App Registration**: You need to create an Azure AD application registration with permissions to access SharePoint.
2. **SharePoint Site**: You need access to a SharePoint site where files will be stored.
3. **Python Library**: The `Office365-REST-Python-Client` library will be installed automatically.

## Step 1: Create Azure AD App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Click **New registration**
4. Fill in:
   - **Name**: Project Status Tracker (or your preferred name)
   - **Supported account types**: Accounts in this organizational directory only
   - **Redirect URI**: Leave blank for now
5. Click **Register**
6. Note down:
   - **Application (client) ID** → `SHAREPOINT_CLIENT_ID`
   - **Directory (tenant) ID** → `SHAREPOINT_TENANT_ID`

## Step 2: Create Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. Add a description and choose expiration
4. Click **Add**
5. **IMPORTANT**: Copy the secret value immediately (you won't see it again)
   - This is your `SHAREPOINT_CLIENT_SECRET`

## Step 3: Configure API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **SharePoint**
4. Choose **Application permissions** (not Delegated)
5. Add the following permissions:
   - `Sites.ReadWrite.All` - Read and write items in all site collections
   - `Files.ReadWrite.All` - Have full access to all files user can access
6. Click **Add permissions**
7. Click **Grant admin consent** (requires admin privileges)

## Step 4: Get SharePoint Site URL

1. Go to your SharePoint site
2. Copy the site URL, for example:
   - `https://yourtenant.sharepoint.com/sites/yoursite`
   - This is your `SHAREPOINT_SITE_URL`

## Step 5: Configure Environment Variables

Add the following to your `.env` file in the `server` directory:

```env
# Storage Configuration
STORAGE_TYPE=sharepoint

# SharePoint Configuration
SHAREPOINT_SITE_URL=https://yourtenant.sharepoint.com/sites/yoursite
SHAREPOINT_DOCUMENT_LIBRARY=Documents
SHAREPOINT_CLIENT_ID=your-client-id-here
SHAREPOINT_CLIENT_SECRET=your-client-secret-here
SHAREPOINT_TENANT_ID=your-tenant-id-here
```

## Step 6: Install Dependencies

The SharePoint library will be installed automatically when you run:

```bash
cd server
poetry install
```

Or manually:

```bash
poetry add "Office365-REST-Python-Client[sharepoint]"
```

## Step 7: Test the Integration

1. Start your server
2. Upload a file through the UI
3. Check the server logs for SharePoint authentication messages
4. Verify the file appears in your SharePoint document library under the project folder

## Folder Structure in SharePoint

Files are organized by project ID in SharePoint:
```
Documents/
  ├── 1/          (Project ID 1)
  │   ├── file1.mp3
  │   └── file2.pdf
  ├── 2/          (Project ID 2)
  │   └── file3.wav
  └── ...
```

## Switching Back to Local Storage

To switch back to local filesystem storage, simply change:

```env
STORAGE_TYPE=local
```

## Troubleshooting

### Authentication Errors

- Verify all SharePoint environment variables are set correctly
- Check that the client secret hasn't expired
- Ensure API permissions are granted and admin consent is provided

### File Upload Errors

- Check SharePoint site URL is correct
- Verify the document library name exists
- Ensure the app has write permissions to the library

### Import Errors

If you see `Office365-REST-Python-Client not installed`:
```bash
cd server
poetry add "Office365-REST-Python-Client[sharepoint]"
```

## Security Notes

- **Never commit** your `.env` file with secrets to version control
- Rotate client secrets regularly
- Use the principle of least privilege for API permissions
- Consider using Azure Key Vault for secret management in production
