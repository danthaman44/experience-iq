"use client";

import { useUser } from "@stackframe/stack";

export function ChatAuthGuard() {
  useUser({ or: 'redirect' });
  return null;
}
