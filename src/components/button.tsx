import { cn } from "@/lib/utils";
import React, { FC } from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

const variantClasses = {
  primary: "bg-primary text-white",
  secondary: "bg-gray-500 text-black",
};

const Button: FC<ButtonProps> = ({
  variant = "primary",
  className,
  ...props
}) => (
  <button
    className={cn(variantClasses[variant], "px-4 py-2 rounded", className)}
    {...props}
  ></button>
);

export default Button;
