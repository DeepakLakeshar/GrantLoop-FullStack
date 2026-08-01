import { forwardRef } from "react";

type FormFieldProps = React.InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: string;
};

/** Matches the label/input styling already used identically across the
 * Case Submission and Donation Flow mockups — reused here, not reinvented. */
export const FormField = forwardRef<HTMLInputElement, FormFieldProps>(
  ({ label, error, className, id, ...props }, ref) => {
    const fieldId = id ?? props.name;
    return (
      <div className="space-y-2">
        <label htmlFor={fieldId} className="font-label-caps text-label-caps text-on-surface-variant uppercase block">
          {label}
        </label>
        <input
          {...props}
          id={fieldId}
          ref={ref}
          className={`w-full bg-white border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary rounded px-4 py-3 text-body-md transition-all ${
            error ? "border-error" : ""
          } ${className ?? ""}`}
        />
        {error && <p className="text-error text-data-table font-data-table">{error}</p>}
      </div>
    );
  }
);
FormField.displayName = "FormField";
