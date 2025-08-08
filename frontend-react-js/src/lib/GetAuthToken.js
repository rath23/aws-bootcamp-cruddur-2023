import { fetchAuthSession } from '@aws-amplify/auth';

export async function getAuthToken() {
  try {
    const session = await fetchAuthSession();
    return session.tokens?.accessToken?.toString() || null;
  } catch (err) {
    console.error("Failed to get auth token:", err);
    return null;
  }
}
