import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Chat from "./components/Chat";
import DarkModeToggle from "./components/DarkModeToggle";

const queryClient = new QueryClient();

function App() {
  return (
    <>
      <QueryClientProvider client={queryClient}>
        <div className="fixed top-6 right-6">
          <DarkModeToggle />
        </div>
        <Chat />
      </QueryClientProvider>
    </>
  );
}

export default App;
