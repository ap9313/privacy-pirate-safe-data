"use client";

import { useState } from "react";
import type { LucideIcon } from "lucide-react";
import { FileText, ImageIcon, Info, Menu, Type, Wifi, X } from "lucide-react";

import { AboutPage } from "@/app/ui/about/about-page";
import { FormPage } from "@/app/ui/form/form-page";
import { PdfPage } from "@/app/ui/pdf/pdf-page";
import { PicturePage } from "@/app/ui/picture/picture-page";
import { TestPage } from "@/app/ui/test/test-page";
import { TextPage } from "@/app/ui/text/text-page";

type Page = "about" | "form" | "pdf" | "text" | "picture" | "test";

interface MenuItem {
  id: Page;
  label: string;
  icon: LucideIcon;
}

const menuItems: MenuItem[] = [
  { id: "about", label: "About", icon: Info },
  { id: "form", label: "Form", icon: FileText },
  { id: "pdf", label: "PDF", icon: FileText },
  { id: "text", label: "Text", icon: Type },
  { id: "picture", label: "Picture", icon: ImageIcon },
  { id: "test", label: "Test", icon: Wifi },
];

export default function SafeDataApp() {
  const [currentPage, setCurrentPage] = useState<Page>("about");
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const renderPage = () => {
    switch (currentPage) {
      case "about":
        return <AboutPage />;
      case "form":
        return <FormPage />;
      case "pdf":
        return <PdfPage />;
      case "text":
        return <TextPage />;
      case "picture":
        return <PicturePage />;
      case "test":
        return <TestPage />;
      default:
        return <AboutPage />;
    }
  };

  return (
    <div className="min-h-screen flex bg-background">
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-0"
        } transition-all duration-300 bg-sidebar text-sidebar-foreground flex flex-col overflow-hidden`}
      >
        <div className="p-4 border-b border-sidebar-border flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-sidebar-primary">Safe-Data</h1>
            <p className="text-sm text-sidebar-foreground/70">Privacy Microservice</p>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-2 rounded-lg hover:bg-sidebar-accent transition-colors text-sidebar-foreground"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <nav className="flex-1 p-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentPage(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-1 transition-colors text-left ${
                  currentPage === item.id
                    ? "bg-sidebar-primary text-sidebar-primary-foreground"
                    : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="flex-1 flex flex-col overflow-hidden">
        {!sidebarOpen && (
          <header className="h-14 border-b border-border flex items-center px-4 bg-card">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-lg hover:bg-muted transition-colors text-foreground"
            >
              <Menu className="w-5 h-5" />
            </button>
          </header>
        )}
        <div className="flex-1 overflow-auto">{renderPage()}</div>
      </main>
    </div>
  );
}
