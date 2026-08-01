import { Shield, Lock } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-surface-container-highest border-t border-outline-variant w-full py-12 mt-12">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-gutter px-margin-desktop max-w-container-max mx-auto">
        <div className="space-y-4">
          <span className="text-headline-sm font-headline-sm font-bold text-primary">GrantLoop</span>
          <p className="text-on-surface-variant text-body-md">
            Institutional-grade transparency for verified fundraising.
          </p>
        </div>
        <div>
          <h4 className="font-label-caps text-label-caps text-on-surface mb-6 uppercase">Transparency</h4>
          <ul className="space-y-3 text-body-md text-on-surface-variant">
            <li>Audit Logs</li>
            <li>Usage of Funds</li>
            <li>Verification Process</li>
          </ul>
        </div>
        <div>
          <h4 className="font-label-caps text-label-caps text-on-surface mb-6 uppercase">Governance</h4>
          <ul className="space-y-3 text-body-md text-on-surface-variant">
            <li>Privacy Policy</li>
            <li>Terms of Service</li>
          </ul>
        </div>
        <div>
          <h4 className="font-label-caps text-label-caps text-on-surface mb-6 uppercase">Support</h4>
          <ul className="space-y-3 text-body-md text-on-surface-variant">
            <li>Contact Support</li>
            <li>Help Center</li>
          </ul>
        </div>
      </div>
      <div className="px-margin-desktop max-w-container-max mx-auto mt-12 pt-8 border-t border-outline-variant flex justify-between items-center text-label-caps text-on-surface-variant">
        <span>© 2026 GrantLoop. Institutional Trust &amp; Financial Accountability.</span>
        <div className="flex gap-4">
          <Shield className="w-[18px] h-[18px]" />
          <Lock className="w-[18px] h-[18px]" />
        </div>
      </div>
    </footer>
  );
}
