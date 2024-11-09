import { cn } from "@/lib/utils";
import React, { FC } from "react";

interface QuestionCardProps extends React.ButtonHTMLAttributes<HTMLDivElement> {
  highlighted?: boolean;
}

const Button: FC<QuestionCardProps> = ({
  className,
  highlighted = false,
  ...props
}) => (
  <div
    className={cn(highlighted ? "bg-primary" : "", className)}
    {...props}
  ></div>
);

export default Button;
