const TextSkeleton = () => {
  return (
    <div className="w-full animate-pulse">
      <div className="h-2.5 bg-slate-300 rounded-full dark:bg-slate-500 w-[20%] mb-4"></div>
      <div className="h-2 bg-slate-300 rounded-full dark:bg-slate-500 max-w-[60%] mb-2.5"></div>
      <div className="h-2 bg-slate-300 rounded-full dark:bg-slate-500 mb-2.5"></div>
      <div className="h-2 bg-slate-300 rounded-full dark:bg-slate-500 max-w-[80%] mb-2.5"></div>
      <div className="h-2 bg-slate-300 rounded-full dark:bg-slate-500 max-w-[50%] mb-2.5"></div>
      <div className="h-2 bg-slate-300 rounded-full dark:bg-slate-500 max-w-[40%]"></div>
    </div>
  );
};

export default TextSkeleton;
