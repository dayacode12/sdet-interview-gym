import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/sidebar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "SDET Interview Gym — Schwab Cyber Security QA Prep",
  description:
    "Personal practice platform: Java coding, automation, API and SQL testing, IAM security scenarios, timed mock interviews with transparent scoring.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body className="min-h-screen bg-background text-foreground antialiased">
        <div className="flex min-h-screen flex-col md:flex-row">
          <Sidebar />
          <main className="min-w-0 flex-1 overflow-x-hidden">
            <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">{children}</div>
          </main>
        </div>
      </body>
    </html>
  );
}
