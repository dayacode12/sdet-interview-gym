import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/sidebar";
import { AuthGate } from "@/components/auth-gate";
import { PrivateAssistantMount } from "@/components/private-assistant-mount";

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
    <html lang="en" suppressHydrationWarning className={`${geistSans.variable} ${geistMono.variable}`}>
      <head>
        {/* Set the theme before first paint so dark mode never flashes.
            Mirrors ThemeToggle's contract: explicit choice in localStorage,
            otherwise the OS preference. The same applies to the collapsed
            sidebar, so a collapsed session never flashes the sidebar open. */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem("theme");var d=t==="dark"||(!t&&window.matchMedia("(prefers-color-scheme: dark)").matches);if(d){document.documentElement.classList.add("dark")}if(localStorage.getItem("sidebar-collapsed")==="1"){document.documentElement.classList.add("sidebar-collapsed")}}catch(e){}})()`,
          }}
        />
      </head>
      <body className="min-h-screen bg-background text-foreground antialiased transition-colors">
        <AuthGate>
          <div className="flex min-h-screen flex-col md:flex-row">
            <Sidebar />
            <main className="min-w-0 flex-1 overflow-x-hidden">
              <div className="content-shell mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">{children}</div>
            </main>
          </div>
          <PrivateAssistantMount />
        </AuthGate>
      </body>
    </html>
  );
}
