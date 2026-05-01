import os
import streamlit as st


def show_oauth_status():
    client_secret_exists = os.path.exists("credentials.json")

    if client_secret_exists:
        st.success("credentials.json found. OAuth setup can be implemented next.")
    else:
        st.warning("credentials.json not found. Add Google OAuth credentials later for direct Calendar API access.")

    st.code(
        """Production OAuth steps:
1. Create Google Cloud project
2. Enable Google Calendar API
3. Configure OAuth consent screen
4. Download credentials.json
5. Use google-auth-oauthlib flow
6. Store token.json locally or securely in deployment
""",
        language="text",
    )
