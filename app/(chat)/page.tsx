import { Chat } from "@/components/chat";
import { ChatRedirect } from "./components/ChatRedirect";
import { ChatAuthGuard } from "./components/ChatAuthGuard";

export const dynamic = "force-dynamic";

export default function Page() {
  return (
    <>
      <ChatAuthGuard />
      <ChatRedirect />
      <Chat />
    </>
  );
}
