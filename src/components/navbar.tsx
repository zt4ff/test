"use client";

import { useState } from "react";
import dynamic from "next/dynamic";

type TabName = "Featured" | "KPI" | "Layouts" | "Storyboards";

const Navbar: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabName>("Storyboards");
  const components: Record<TabName, React.ComponentType> = {
    Featured: dynamic(() => import("./featured")),
    KPI: dynamic(() => import("./kpi")),
    Layouts: dynamic(() => import("./layouts")),
    Storyboards: dynamic(() => import("./storyboards")),
  };
  const Component = components[activeTab];

  return (
    <div className="flex flex-col h-screen">
      <nav className="flex justify-around bg-blue-600 text-white py-4">
        {Object.keys(components).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as TabName)}
            className={`${
              activeTab === tab ? "underline" : ""
            } text-lg px-4 py-2 hover:bg-blue-700`}
          >
            {tab}
          </button>
        ))}
      </nav>
      <div className="flex-grow p-4">
        <Component />
      </div>
    </div>
  );
};

export default Navbar;
