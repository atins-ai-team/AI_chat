import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { formSchema } from "@/utils/schema";
import { z } from "zod";
import { Textarea } from "./ui/textarea";
import { useMutation } from "@tanstack/react-query";
import { fetchAIResponse } from "@/lib/utils";
import { Loader } from "lucide-react";
import TextSkeleton from "./TextSkeleton";
import ReactMarkdown from "react-markdown";

type Message = {
  user: string;
  text: string;
};

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const scrollRef = React.useRef<HTMLDivElement>(null);

  const mutation = useMutation({
    mutationFn: fetchAIResponse,
    onMutate: async (newMessage: string) => {
      setMessages((prev) => [
        ...prev,
        { user: "User", text: newMessage },
        { user: "AI", text: "" },
      ]);
    },
    onSuccess: (data) => {
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
          user: "AI",
          text: data,
        };
        return newMessages;
      });
    },

    onError: (error) => {
      console.error("Błąd podczas zapytania:", error);
    },
  });

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      id: "1",
      user: "1",
      query: "",
    },
  });

  function onSubmit(values: z.infer<typeof formSchema>) {
    if (values.query.trim() === "") return;
    mutation.mutate(values.query);
    form.resetField("query");
  }

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  return (
    <div className="flex flex-col items-center justify-center md:gap-6 h-screen mx-auto max-w-[800px] px-[1em] py-[4em]">
      <div
        className={`w-full flex flex-col gap-12 mb-12 overflow-y-auto pr-6 custom-scroll mt-[2em] lg:mt-0 ${
          messages.length > 0 && "h-full"
        }`}
      >
        {messages.map((message, i) => (
          <div
            key={i}
            className={`${
              message.user === "User"
                ? "bg-slate-100 dark:bg-custom-light-gray rounded-md p-3 md:p-4 w-[70%] self-end"
                : "w-full self-start leading-7"
            }`}
          >
            <div className="prose dark:prose-invert max-w-none">
              <ReactMarkdown>{message.text}</ReactMarkdown>
            </div>
          </div>
        ))}
        {mutation.isPending && <TextSkeleton />}
        <div ref={scrollRef} />
      </div>

      {messages.length === 0 && (
        <p className="text-center text-lg md:text-2xl">How can I help you?</p>
      )}
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex items-center justify-between gap-6 p-3 md:p-4 rounded-lg md:rounded-2xl bg-white shadow-md border-[1px] border-slate-200 dark:border-none dark:bg-custom-light-gray w-full"
        >
          <FormField
            control={form.control}
            name="query"
            render={({ field }) => (
              <FormItem className="w-full">
                <FormControl>
                  <Textarea
                    placeholder="Ask your assistant..."
                    autoComplete="off"
                    {...field}
                    className="border-none dark:bg-custom-light-gray resize-none min-h-6 max-h-24 overflow-y-auto custom-scroll text-sm md:text-base shadow-none"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button
            disabled={mutation.isPending || !form.watch("query")}
            type="submit"
            className="cursor-pointer"
          >
            {mutation.isPending ? <Loader className="animate-spin" /> : "Send"}
          </Button>
        </form>
      </Form>
    </div>
  );
};

export default Chat;
