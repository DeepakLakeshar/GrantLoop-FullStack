import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { HeartHandshake } from "lucide-react";
import type { Campaign } from "@/types/entities";
import { formatCurrency } from "@/lib/format";

interface DonationWidgetProps {
  campaign: Campaign;
}

const PRESET_MULTIPLIERS = [0.01, 0.02, 0.05]; // relative to goal, rounded below

export function DonationWidget({ campaign }: DonationWidgetProps) {
  const navigate = useNavigate();
  const presets = PRESET_MULTIPLIERS.map((m) => Math.max(10, Math.round((campaign.goal_amount * m) / 10) * 10));
  const [amount, setAmount] = useState<number>(presets[1]);
  const [customAmount, setCustomAmount] = useState("");
  const [isAnonymous, setIsAnonymous] = useState(false);

  const effectiveAmount = customAmount ? Number(customAmount) : amount;

  function handleDonate() {
    // Provider (Razorpay vs Stripe) is resolved entirely server-side by
    // currency/region at checkout time — the widget never names a
    // gateway, per the frozen Donation Flow decision.
    navigate(`/causes/${campaign.id}/donate`, {
      state: { amount: effectiveAmount, currency: campaign.campaign_currency, isAnonymous },
    });
  }

  return (
    <div className="bg-white border border-outline-variant rounded-xl p-8 shadow-sm">
      <div className="grid grid-cols-3 gap-3 mb-4">
        {presets.map((preset) => (
          <button
            key={preset}
            onClick={() => {
              setAmount(preset);
              setCustomAmount("");
            }}
            className={`p-3 border rounded-lg font-headline-sm text-primary text-center transition-all ${
              !customAmount && amount === preset
                ? "border-primary bg-primary-container/5"
                : "border-outline-variant hover:border-primary"
            }`}
          >
            {formatCurrency(preset, campaign.campaign_currency)}
          </button>
        ))}
      </div>
      <input
        type="number"
        min={1}
        placeholder="Custom amount"
        aria-label="Custom donation amount"
        value={customAmount}
        onChange={(e) => setCustomAmount(e.target.value)}
        className="w-full p-3 border border-outline-variant rounded-lg mb-4 focus:ring-1 focus:ring-primary focus:border-primary"
      />
      <label className="flex items-center justify-between p-3 bg-surface-container-low rounded-lg border border-outline-variant mb-6 cursor-pointer">
        <span className="text-body-md text-on-surface-variant">Donate anonymously</span>
        <input
          type="checkbox"
          checked={isAnonymous}
          onChange={(e) => setIsAnonymous(e.target.checked)}
          className="rounded text-primary focus:ring-primary border-outline-variant"
        />
      </label>
      <button
        onClick={handleDonate}
        disabled={!effectiveAmount || effectiveAmount <= 0}
        className="w-full py-4 bg-primary text-white font-bold rounded-lg hover:bg-primary-container transition-all flex items-center justify-center gap-2 disabled:opacity-50"
      >
        <HeartHandshake className="w-5 h-5" />
        Donate {effectiveAmount > 0 ? formatCurrency(effectiveAmount, campaign.campaign_currency) : ""}
      </button>
    </div>
  );
}
