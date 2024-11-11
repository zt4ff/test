"use client";

import { useState } from "react";

type TabName = "" | "kpi" | "layouts" | "storyboards";

type NavbarProps = {
  onTabChange: (tab: string) => void;
};

const Navbar: React.FC<NavbarProps> = ({ onTabChange }) => {
  const [activeTab, setActiveTab] = useState<TabName>("");

  const tabs = [
    { item: "", label: "Featured" },
    { item: "kpi", label: "KPI" },
    { item: "layout", label: "Layouts" },
    { item: "storyboard", label: "Storyboards" },
  ];

  return (
    <div className="flex flex-col">
      <nav className="flex justify-around bg-gray-100 text-gray-400 text-gray-400 p-2 rounded ">
        {tabs.map((tab) => (
          <button
            key={tab.item}
            onClick={() => {
              setActiveTab(tab.item as TabName);
              onTabChange(tab.item);
            }}
            className={`flex-1 ${
              activeTab === tab.item ? "bg-white text-black hover:bg-white" : ""
            } text-lg px-4 py-2 rounded`}
          >
            {tab.label}
          </button>
        ))}
      </nav>
    </div>
  );
};

export default Navbar;
