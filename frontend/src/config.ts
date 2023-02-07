export type Settings = {
  apiUrl: string;
};

export const settings: Settings = {
  apiUrl: import.meta.env.VITE_API_URL ?? "http://0.0.0.0:8000/api",
};
