import "@fontsource/roboto/300.css";
import "@fontsource/roboto/400.css";
import "@fontsource/roboto/500.css";
import "@fontsource/roboto/700.css";

import {
  Box,
  Button,
  Container,
  InputAdornment,
  LinearProgress,
  TextField,
} from "@mui/material";
import { AxiosError } from "axios";
import { SearchRounded as SearchRoundedIcon } from "@mui/icons-material";
import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "react-query";
import { ReactQueryDevtools } from "react-query/devtools";

import { NavBar, TransactionView } from "./components";
import { useTransactionDetails } from "./hooks";
import { ResponseError } from "./types";

import "./main.css";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);

const queryClient = new QueryClient();

const App = () => {
  const [uetr, setUETR] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const {
    isFetching,
    isLoading,
    data: transaction,
    error,
  } = useTransactionDetails({ uetr });

  useEffect(() => {
    if (!!error) {
      setUETR(null);
    }
  }, [error]);

  const handleUETRChange = (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setInput(event.target.value);
  };

  const handleSubmit = () => {
    setUETR(input);
  };

  const handleResetUETR = () => {
    setUETR(null);
    setInput("");
  };

  return (
    <>
      <Box>
        {(isLoading || isFetching) && <LinearProgress />}
        <NavBar />
        <Container maxWidth="xl" sx={{ mt: 3, pl: 2, pr: 2, mb: 7 }}>
          {uetr && !error && !isLoading && !isFetching && transaction ? (
            <TransactionView
              onResetButtonClick={handleResetUETR}
              transactionDetails={transaction}
            />
          ) : (
            <>
              <TextField
                error={!!error}
                label="UETR"
                value={uetr}
                onChange={handleUETRChange}
                sx={{ mr: 1, mb: 1, minWidth: 250 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchRoundedIcon />
                    </InputAdornment>
                  ),
                  sx: { backgroundColor: "#fff" },
                }}
                helperText={
                  !!error
                    ? (error as AxiosError<ResponseError>)?.response?.data
                        ?.detail ?? "An unknown error occurred."
                    : null
                }
              />
              <Button
                disabled={!input || isLoading || isFetching}
                size="large"
                sx={{ py: 1.7 }}
                variant="contained"
                onClick={handleSubmit}
              >
                Get Status
              </Button>
            </>
          )}
        </Container>
      </Box>
      <ReactQueryDevtools initialIsOpen={false} />
    </>
  );
};

root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
);
