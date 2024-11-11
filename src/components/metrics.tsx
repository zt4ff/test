import { cn } from "@/lib/utils";
import { FC } from "react";

interface MetricsProps extends React.ButtonHTMLAttributes<HTMLDivElement> {
  data: string | number;
  label: string;
}

const Metrics: FC<MetricsProps> = ({ className, data, label, ...props }) => (
  <div className={cn("text-center", className)} {...props}>
    <p>{data}</p>
    <p>{label}</p>
  </div>
);

export default Metrics;
