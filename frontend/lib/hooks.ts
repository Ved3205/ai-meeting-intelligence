import { useQuery } from "@tanstack/react-query";
import { api } from "./api";

export function useMeetings() {
  return useQuery({ queryKey: ["meetings"], queryFn: api.listMeetings });
}
