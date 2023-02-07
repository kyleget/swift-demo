import { Box, Button, Card, Typography } from "@mui/material";
import { format as formatDate } from "date-fns";

import { PaymentEvent, TransactionDetails } from "../../types";

export type TransactionViewProps = {
  transactionDetails: TransactionDetails;
  onResetButtonClick: () => void;
};

const getDetailRow = (label: string, value: string) => (
  <Box sx={{ mb: 1 }}>
    <Typography fontWeight="bold" component="span" sx={{ mr: 1 }}>
      {`${label}:`}
    </Typography>
    <Typography component="span">{value}</Typography>
  </Box>
);

export type PaymentEventProps = {
  paymentEvent: PaymentEvent;
};

const PaymentEventView = ({ paymentEvent }: PaymentEventProps) => (
  <Card sx={{ p: 2, mt: 2, mb: 4 }}>
    {getDetailRow("Message Type", paymentEvent.message_type)}
    {getDetailRow("From", paymentEvent.from)}
    {getDetailRow("To", paymentEvent.to)}
    {getDetailRow("Transaction Status", paymentEvent.transaction_status)}
    {getDetailRow(
      "Instructed Amount",
      paymentEvent.instructed_amount?.formatted_amount ?? "-"
    )}
    {getDetailRow(
      "Settlement Amount",
      paymentEvent.settlement_amount?.formatted_amount ?? "-"
    )}
    {getDetailRow("Fees", paymentEvent.fees.formatted_amount)}
  </Card>
);

export const TransactionView = ({
  transactionDetails,
  onResetButtonClick,
}: TransactionViewProps) => (
  <Box sx={{ maxWidth: 700 }}>
    <Box sx={{ display: "flex" }}>
      <Typography variant="h5" component="h2">
        Transaction Details
      </Typography>
      <Box flexGrow={1} />
      <Button onClick={onResetButtonClick}>Reset</Button>
    </Box>
    <Card sx={{ p: 2, mt: 2, mb: 4 }}>
      {getDetailRow("UETR", transactionDetails.uetr)}
      {getDetailRow("Bank", transactionDetails.bank)}
      {getDetailRow(
        "Initiation Date",
        formatDate(transactionDetails.initiation_date, "M/d/Y p")
      )}
      {getDetailRow(
        "Completion Date",
        formatDate(transactionDetails.completion_date, "M/d/Y p")
      )}
      {getDetailRow(
        "Last Update",
        formatDate(transactionDetails.last_update_date, "M/d/Y p")
      )}
      {getDetailRow(
        "Transaction Status",
        transactionDetails.transaction_status
      )}
      {getDetailRow(
        "Settlement Amount",
        transactionDetails.settlement_amount?.formatted_amount ?? "-"
      )}
    </Card>
    <Typography variant="h6" component="h3">
      Payment Events
      {transactionDetails.payment_events.map((event, index) => (
        <PaymentEventView key={index} paymentEvent={event} />
      ))}
    </Typography>
  </Box>
);
