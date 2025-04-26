import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const fetchAIResponse = async (input: string) => {
  const queryPayload = {
    id: "1",
    user: "2",
    query: input,
  };

  const response = await fetch("http://localhost:8001/query_AI", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(queryPayload),
  });

  const contentType = response.headers.get("content-type");

  if (contentType && contentType.includes("application/json")) {
    const data = await response.json();
    return typeof data === "string"
      ? data
      : data.response || JSON.stringify(data);
  } else {
    return await response.text();
  }
};
