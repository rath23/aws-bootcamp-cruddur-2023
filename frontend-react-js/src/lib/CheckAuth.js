import { getCurrentUser, fetchUserAttributes } from '@aws-amplify/auth';

export async function checkAuth(setUser) {
  try {
    // First verify there's an active session
    await getCurrentUser(); // This throws if not authenticated
    
    // Then get user attributes
    const attributes = await fetchUserAttributes();
    
    const userData = {
      display_name: attributes.name || attributes["custom:name"] || "",
      handle: attributes.preferred_username || attributes["custom:preferred_username"] || "",
      cognito_id: attributes.sub // Add the cognito user ID
    };

    // Store in localStorage
    localStorage.setItem("handle", userData.handle);
    localStorage.setItem("display_name", userData.display_name);
    localStorage.setItem("cognito_id", userData.cognito_id);

    if (setUser) setUser(userData);
    return userData;
    
  } catch (error) {
    console.error("Auth check failed:", error);
    // Clear any existing auth data
    localStorage.removeItem("access_token");
    localStorage.removeItem("handle");
    localStorage.removeItem("display_name");
    localStorage.removeItem("cognito_id");
    
    if (setUser) setUser(null);
    return null;
  }
}