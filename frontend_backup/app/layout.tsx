import "@/app/globals.css";
import TopNav from "@/components/layout/TopNav";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-200">
        <TopNav />
        <main className="p-6">{children}</main>
      </body>
    </html>
  );
}
