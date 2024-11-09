export interface Asset {
  id: number;
  title: string;
  type: "Report" | "Dashboard" | "Presentation";
  description: string;
  date: string;
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

export const mockData: Asset[] = Array.from({ length: 50 }, (_, index) => ({
  id: index + 1,
  title: `Asset ${index + 1}`,
  type: ["Report", "Dashboard", "Presentation"][
    Math.floor(Math.random() * 3)
  ] as Asset["type"],
  description: `Description for asset ${index + 1}`,
  date: new Date(2024, 0, index + 1).toLocaleDateString(),
}));

export const fetchMockData = async (
  page: number,
  pageSize: number,
  searchQuery: string = ""
): Promise<FetchResponse> => {
  await new Promise((resolve) => setTimeout(resolve, 800));

  let filteredData = [...mockData];

  if (searchQuery) {
    filteredData = mockData.filter(
      (item) =>
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.type.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }

  const start = (page - 1) * pageSize;
  const end = start + pageSize;

  return {
    data: filteredData.slice(start, end),
    hasMore: end < filteredData.length,
    total: filteredData.length,
  };
};
