"use client";

import { useUser } from "@stackframe/stack";
import { useEffect } from "react";

export function ChatAuthGuard() {
  const user = useUser({ or: 'redirect' });
  // Register the user in our backend after getting the access token from Stack
  useEffect(() => {
    const registerUser = async () => {
      const accessToken = await user.getAccessToken();
      const body = {
        id: user.id,
        displayName: user.displayName,
        primaryEmail: user.primaryEmail,
        primaryEmailVerified: user.primaryEmailVerified,
        profileImageUrl: user.profileImageUrl
      }
      const headers = {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${accessToken}`
      }
      const response = await fetch("/api/users/register", {
        method: "POST",
        headers: headers,
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        console.error("Failed to register user", response.statusText);
        throw new Error("Failed to register user");
      }
    };
    registerUser();
  }, [user]);
  return null;
}
