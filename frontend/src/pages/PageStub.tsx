import { TopNavBar } from "@/components/layout/TopNavBar";
import { Footer } from "@/components/layout/Footer";

interface PageStubProps {
  title: string;
  note?: string;
}

/** Temporary placeholder — Phase 1 wires up routing and layout shells;
 * each page's real content gets built out in its own pass, reusing the
 * shared components already in this codebase. */
export function PageStub({ title, note }: PageStubProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <TopNavBar />
      <main className="flex-1 max-w-container-max mx-auto px-margin-desktop py-24 text-center">
        <h1 className="font-headline-lg text-headline-lg text-primary mb-4">{title}</h1>
        <p className="text-on-surface-variant font-body-md">
          {note ?? "Page content pending implementation."}
        </p>
      </main>
      <Footer />
    </div>
  );
}
