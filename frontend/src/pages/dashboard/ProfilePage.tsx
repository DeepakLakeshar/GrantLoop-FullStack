import { useAuth } from "@/context/AuthContext";
import { TopNavBar } from "@/components/layout/TopNavBar";
import { User, Mail, Shield } from "lucide-react";
import { Link } from "react-router-dom";

export function ProfilePage() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="min-h-screen bg-surface-container-lowest">
      <TopNavBar />
      <main className="max-w-container-sm mx-auto px-margin-desktop py-12">
        <h1 className="font-headline-lg text-headline-lg text-primary mb-8">My Profile</h1>
        
        <div className="bg-surface border border-outline-variant rounded-lg overflow-hidden">
          <div className="p-8 border-b border-outline-variant flex items-center gap-6 bg-primary-container/30">
            <div className="w-24 h-24 rounded-full bg-primary flex items-center justify-center text-white font-headline-lg text-headline-lg font-bold">
              {user.username.slice(0, 1).toUpperCase()}
            </div>
            <div>
              <h2 className="font-headline-md text-headline-md text-primary">{user.username}</h2>
              <p className="text-body-lg text-on-surface-variant flex items-center gap-2 mt-1">
                <Shield className="w-4 h-4" /> {user.role.toUpperCase()} ACCOUNT
              </p>
            </div>
          </div>
          
          <div className="p-8 space-y-6">
            <div>
              <label className="text-label-caps font-label-caps text-on-surface-variant block mb-1">Email Address</label>
              <div className="flex items-center gap-3 text-body-lg text-primary">
                <Mail className="w-5 h-5 text-secondary" />
                {user.email}
              </div>
            </div>
            
            <div>
              <label className="text-label-caps font-label-caps text-on-surface-variant block mb-1">Full Name</label>
              <div className="flex items-center gap-3 text-body-lg text-primary">
                <User className="w-5 h-5 text-secondary" />
                {user.username || "Not provided"}
              </div>
            </div>
          </div>
          
          <div className="px-8 py-4 bg-surface-container border-t border-outline-variant text-sm text-on-surface-variant">
            <p>
              Editing your profile is currently disabled. To change your password, visit the{" "}
              <Link to="/settings" className="text-primary font-bold hover:underline">
                Settings
              </Link>{" "}
              page.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
