import axios from "axios";

import { TransactionDetails, TransactionDetailsResponse } from "../types";

import { settings } from "../config";

export const instance = axios.create({
  baseURL: settings.apiUrl,
});

type GetTransactionDetailsProps = {
  uetr: string;
};

export const getTransactionDetails = ({
  uetr,
}: GetTransactionDetailsProps): (() => Promise<TransactionDetails>) => {
  return async () => {
    const { data } = await instance.get<TransactionDetailsResponse>(
      `/transactions/${uetr}`
    );

    const details: TransactionDetails = {
      ...data,
      completion_date: new Date(data.completion_date),
      initiation_date: new Date(data.initiation_date),
      last_update_date: new Date(data.last_update_date),
      payment_events: data.payment_events.map((event) => ({
        ...event,
        fees: {
          ...event.fees,
          amount: parseFloat(event.fees.amount),
        },
        instructed_amount: !!event.instructed_amount
          ? {
              ...event.instructed_amount,
              amount: parseFloat(event.instructed_amount.amount),
            }
          : null,
        last_update_date: new Date(event.last_update_date),
        received_date: new Date(event.received_date),
        settlement_amount: !!event.settlement_amount
          ? {
              ...event.settlement_amount,
              amount: parseFloat(event.settlement_amount?.amount),
            }
          : null,
      })),
      settlement_amount: !!data.settlement_amount
        ? {
            ...data.settlement_amount,
            amount: parseFloat(data.settlement_amount?.amount),
          }
        : null,
    };

    return details;
  };
};
