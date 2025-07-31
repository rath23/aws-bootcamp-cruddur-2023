import { getCurrentUser, fetchUserAttributes } from '@aws-amplify/auth';

export async function checkAuth(setUser) {
  try {
    // const cognitoUserOutput = await getCurrentUser();
    // const cognitoUser = cognitoUserOutput?.user ?? cognitoUserOutput;
    // if (!cognitoUser) {
    //   setUser(null);
    //   return;
    // }

    const attributes = await fetchUserAttributes();
    const preferred_username = attributes.preferred_username ?? attributes["custom:preferred_username"] ?? "";
    const name = attributes.name ?? attributes["custom:name"] ?? "";

    localStorage.setItem("handle", preferred_username);
    localStorage.setItem("display_name", name);

    setUser({
      display_name: name,
      handle: preferred_username,
    });
  } catch (error) {
    console.log("Not signed in or auth failed:", error);
    setUser(null);
  }
}
