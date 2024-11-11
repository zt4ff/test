"use client";

import React, { useState, useEffect, useCallback } from "react";
import { debounce } from "lodash";
import Button from "@/components/button";
import Search from "@/components/search";
import { mockRecentSearches, fetchMockData, Asset } from "@/lib/mock";
import { FaTimes } from "react-icons/fa";
import AssetCard from "@/components/asset-card";
import Navbar from "@/components/navbar";

const SEARCH_DELAY = 300;

export default function Home(): JSX.Element {
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [type, setType] = useState<Asset["type"] | undefined>();
  const [items, setItems] = useState<Asset[]>([]);
  const [page, setPage] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(false);
  const [hasMore, setHasMore] = useState<boolean>(false);
  const pageSize = 10;

  const loadData = async (
    currentPage: number,
    search: string,
    assetType: Asset["type"] | undefined
  ): Promise<void> => {
    setLoading(true);
    try {
      const response = await fetchMockData(
        currentPage,
        pageSize,
        search,
        assetType
      );
      if (currentPage === 1) {
        setItems(response.data);
      } else {
        setItems((prev) => [...prev, ...response.data]);
      }
      setHasMore(response.hasMore);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
    setLoading(false);
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const debouncedSearch = useCallback(
    debounce((search: string, assetType: Asset["type"] | undefined) => {
      setPage(1);
      loadData(1, search, assetType);
    }, SEARCH_DELAY),
    []
  );

  useEffect(() => {
    setItems([]);
    setHasMore(false);

    debouncedSearch(searchTerm, type);
    return () => debouncedSearch.cancel();
  }, [searchTerm, type, debouncedSearch]);

  const handleLoadMore = (): void => {
    if (!loading && hasMore) {
      const nextPage = page + 1;
      setPage(nextPage);
      loadData(nextPage, searchTerm, type);
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchTerm(e.target.value);
  };

  const handleRecentSearchClick = (search: string): void => {
    setSearchTerm(search);
  };

  return (
    <div className="container">
      <Button className="absolute right-[10px] top-[10px]">Request</Button>
      <p className="text-center pt-10 text-5xl font-bold">Library</p>
      <p className="text-center py-6">
        Browse for assets needed to report and present analysis
      </p>

      <Search
        onChange={handleSearchChange}
        placeholder="Type to search..."
        className="mb-2"
        value={searchTerm}
        endAdornments={() => {
          if (searchTerm === "") return null;

          return (
            <button onClick={() => setSearchTerm("")}>
              <FaTimes />
            </button>
          );
        }}
      />

      {searchTerm === "" && (
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">
            Recent Searches
          </h3>
          <div className="flex flex-wrap gap-2">
            {mockRecentSearches.map((search, index) => (
              <button
                key={index}
                className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200"
                onClick={() => handleRecentSearchClick(search)}
              >
                {search}
              </button>
            ))}
          </div>
        </div>
      )}

      <Navbar
        onTabChange={(tab) => {
          setType(tab as Asset["type"]);
        }}
      />

      <div className="grid grid-cols-2 gap-4 mt-2">
        {items.map((item) => (
          <AssetCard asset={item} key={item.id} />
        ))}
      </div>

      <div className="mt-6 text-center">
        {loading ? (
          <p className="text-gray-500">Loading...</p>
        ) : hasMore ? (
          <Button onClick={handleLoadMore} className="mx-auto">
            Load More
          </Button>
        ) : (
          items.length > 0 && (
            <p className="text-gray-500">No more data to load</p>
          )
        )}
      </div>
    </div>
  );
}
