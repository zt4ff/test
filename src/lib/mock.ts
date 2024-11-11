export interface Asset {
  id: number;
  type: "kpi" | "storyboard" | "layout";
  title: string;
  description: string;
  isFavorite: boolean;
  shareableLink: string;
  date: string;
}

export enum AssetType {
  "kpi" = "KPI",
  "layout" = "Layouts",
  "storyboard" = "Storyboards",
}

export interface KPIAsset extends Asset {
  businessQuestions: string[];
  metricIds: string[];
  calculation: number;
  visualsAvailable: Array<"bar" | "circular" | "linear">;
  affiliateApplicability: string[];
}

export interface StoryboardAsset extends Asset {
  assetContext: string;
  accessable: boolean;
  applicabeAffiliates: string[];
  coupledKpi: string[];
}

export interface LayoutAsset extends Asset {
  pageCount: number;
  activeKPIs: string[];
  previewImage: string;
  storyboardElements: {
    kpis: string[];
    filters: string[];
    affiliates: string[];
  };
}

export interface FetchResponse {
  data: Asset[];
  hasMore: boolean;
  total: number;
}

export const mockRecentSearches: string[] = [
  "Sales KPIs",
  "Customer Dashboard",
  "Marketing Metrics",
];

const generateMockAsset = (id: number): Asset => {
  const baseAsset: Asset = {
    id,
    title: `Asset ${id}`,
    type: ["kpi", "layout", "storyboard"][
      Math.floor(Math.random() * 3)
    ] as Asset["type"],
    description: `Description for asset ${id}`,
    isFavorite: Math.random() < 0.5,
    shareableLink: "",
    date: new Date(2024, 0, id).toLocaleDateString(),
  };

  if (baseAsset.type === "kpi") {
    return {
      ...baseAsset,
      businessQuestions: [
        "What are the key sales drivers and how is it gotten or derived?",
        "How is customer retention and how is it also gotten or derived?",
        "What are the key sales drivers and how is it created?",
        "How is customer retention and how is it also created?",
      ],
      metricIds: ["#comm", "#stakeholder"],
      calculation: 30,
      visualsAvailable: ["bar", "circular"],
      affiliateApplicability: ["global", "local"],
    } as KPIAsset;
  } else if (baseAsset.type === "layout") {
    return {
      ...baseAsset,
      pageCount: 5,
      activeKPIs: ["kpi-1", "kpi-2"],
      previewImage: "/placeholder.png",
      storyboardElements: {
        kpis: ["kpi-1", "kpi-2"],
        filters: ["filter-1", "filter-2"],
        affiliates: ["affiliate-1", "affiliate-2"],
      },
    } as LayoutAsset;
  } else if (baseAsset.type === "storyboard") {
    return {
      ...baseAsset,
      coupledKpi: ["kpi-1", "kpi-3"],
      assetContext: "content",
      applicabeAffiliates: ["affiliate11", "affiliate2"],
      accessable: Math.random() < 0.5, // randomly generates true or false
    } as StoryboardAsset;
  }
  return baseAsset;
};

export const mockData: Asset[] = Array.from({ length: 50 }, (_, index) =>
  generateMockAsset(index + 1)
);

export const fetchMockData = async (
  page: number,
  pageSize: number,
  searchQuery: string = "",
  typeFilter?: Asset["type"]
): Promise<FetchResponse> => {
  await new Promise((resolve) => setTimeout(resolve, 500));

  let filteredData = [...mockData];

  if (searchQuery) {
    filteredData = filteredData.filter(
      (item) =>
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }

  if (typeFilter) {
    filteredData = filteredData.filter((item) => item.type === typeFilter);
  }

  const start = (page - 1) * pageSize;
  const end = start + pageSize;

  return {
    data: filteredData.slice(start, end),
    hasMore: end < filteredData.length,
    total: filteredData.length,
  };
};
