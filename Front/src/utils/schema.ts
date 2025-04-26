import { z } from "zod";

export const formSchema = z.object({
  id: z.string(),
  user: z.string(),
  query: z.string(),
});
