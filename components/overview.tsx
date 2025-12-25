import { motion } from "framer-motion";

import { MessageIcon } from "./icons";

export const Overview = () => {
  return (
    <motion.div
      key="overview"
      className="max-w-3xl mx-auto md:mt-20"
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ delay: 0.5 }}
    >
      <div className="rounded-xl p-6 flex flex-col gap-8 leading-relaxed text-center max-w-2xl">
        <p className="flex flex-row justify-center gap-4 items-center">
          <MessageIcon size={32} />
        </p>
        <div>
          <p>
            <b>Mockly</b> is an AI coach that assists with technical interview preparation.
          </p>
          <p>
            Mockly walks through problems step-by-step, simulating a real interview.
          </p>
          <p>
            At the end of the session, Mockly provides helpful feedback and suggestions.
          </p>
          <p className="mt-4">
            Start a mock interview session by selecting a question.
          </p>
        </div>
      </div>
    </motion.div>
  );
};
