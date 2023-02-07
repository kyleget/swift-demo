import { useQuery } from "react-query";

import { getTransactionDetails } from "../api";

export type UseTransactionDetailsProps = {
  uetr: string | null;
};

export const useTransactionDetails = ({ uetr }: UseTransactionDetailsProps) => {
  return useQuery(
    "transaction-details",
    getTransactionDetails({ uetr: uetr ?? "" }),
    {
      enabled: !!uetr,
      retry: 0,
      cacheTime: undefined,
    }
  );
};
