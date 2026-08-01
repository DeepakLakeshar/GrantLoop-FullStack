import { forwardRef, useState } from "react";
import { Eye, EyeOff } from "lucide-react";

type PasswordInputProps = React.InputHTMLAttributes<HTMLInputElement> & {
  error?: string;
};

export const PasswordInput = forwardRef<HTMLInputElement, PasswordInputProps>(
  ({ error, className, ...props }, ref) => {
    const [visible, setVisible] = useState(false);

    return (
      <div>
        <div className="relative">
          <input
            {...props}
            ref={ref}
            type={visible ? "text" : "password"}
            className={`w-full bg-white border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary rounded px-4 py-3 pr-12 text-body-md transition-all ${
              error ? "border-error" : ""
            } ${className ?? ""}`}
          />
          <button
            type="button"
            onClick={() => setVisible((v) => !v)}
            aria-label={visible ? "Hide password" : "Show password"}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-primary transition-colors"
          >
            {visible ? <EyeOff className="w-[18px] h-[18px]" /> : <Eye className="w-[18px] h-[18px]" />}
          </button>
        </div>
        {error && <p className="text-error text-data-table font-data-table mt-1">{error}</p>}
      </div>
    );
  }
);
PasswordInput.displayName = "PasswordInput";
