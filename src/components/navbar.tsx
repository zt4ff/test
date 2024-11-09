"use client";

import { useState } from "react";
import dynamic from "next/dynamic";

type TabName = "featured" | "kpi" | "layouts" | "storyboards";

const Navbar: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabName>("featured");

  const tabs = [
    { item: "featured", label: "Featured" },
    { item: "kpi", label: "KPI" },
    { item: "layouts", label: "Layouts" },
    { item: "storyboards", label: "Storyboards" },
  ];

  const FeaturedComponent = dynamic(() => import("./featured"), {
    ssr: false,
    loading: () => <div>Loading...</div>,
  });
  const KPIComponent = dynamic(() => import("./kpi"), {
    ssr: false,
    loading: () => <div>Loading...</div>,
  });
  const LayoutsComponent = dynamic(() => import("./layouts"), {
    ssr: false,
    loading: () => <div>Loading...</div>,
  });
  const StoryboardsComponent = dynamic(() => import("./storyboards"), {
    ssr: false,
    loading: () => <div>Loading...</div>,
  });

  const components = {
    featured: FeaturedComponent,
    kpi: KPIComponent,
    layouts: LayoutsComponent,
    storyboards: StoryboardsComponent,
  };

  const Component = components[activeTab];

  return (
    <div className="flex flex-col h-screen">
      <nav className="flex justify-around bg-gray-100 text-gray-400 text-white p-2 rounded ">
        {tabs.map((tab) => (
          <button
            key={tab.item}
            onClick={() => setActiveTab(tab.item as TabName)}
            className={`flex-1 ${
              activeTab === tab.item ? "bg-white text-black hover:bg-white" : ""
            } text-lg px-4 py-2 rounded`}
          >
            {tab.label}
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
