export type TransactionStatus =
  | "accepted"
  | "completed"
  | "rejected"
  | "unknown";

export type AmountResponse = {
  amount: string;
  currency: string;
  formatted_amount: string;
};

export type Amount = Omit<AmountResponse, "amount"> & {
  amount: Number;
};

export type PaymentEventResponse = {
  fees: AmountResponse;
  from: string;
  instructed_amount: AmountResponse | null;
  last_update_date: string;
  message_type: string;
  received_date: string;
  settlement_amount: AmountResponse | null;
  to: string;
  transaction_status_reason: string | null;
  transaction_status: TransactionStatus;
};

export type PaymentEvent = Omit<
  PaymentEventResponse,
  | "fees"
  | "instructed_amount"
  | "last_update_date"
  | "received_date"
  | "settlement_amount"
> & {
  fees: Amount;
  instructed_amount: Amount | null;
  last_update_date: Date;
  received_date: Date;
  settlement_amount: Amount | null;
};

export type TransactionDetailsResponse = {
  bank: string;
  completion_date: string;
  initiation_date: string;
  last_update_date: string;
  payment_events: PaymentEventResponse[];
  settlement_amount: AmountResponse | null;
  transaction_status: TransactionStatus;
  uetr: string;
};

export type TransactionDetails = Omit<
  TransactionDetailsResponse,
  | "completion_date"
  | "initiation_date"
  | "last_update_date"
  | "payment_events"
  | "settlement_amount"
> & {
  completion_date: Date;
  initiation_date: Date;
  last_update_date: Date;
  payment_events: PaymentEvent[];
  settlement_amount: Amount | null;
};

export type ResponseError = {
  detail: string;
};
