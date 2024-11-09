"use client"

import Button from "@/components/button";
import Navbar from "@/components/navbar";
import Search from "@/components/search";

export default function Home() {
  return (
    <div className="container">
      <Button className="absolute right-[10px] top-[10px]">Request</Button>
      <p className="text-center pt-10  text-5xl font-bold">Library</p>
      <p className="text-center py-6">
        Browse for assets needed to report and present analysis
      </p>

      <Search
        onChange={(e) => {
          console.log(e.target.value);
        }}
        placeholder="Type to search..."
        className="mb-6"
      />

      <Navbar />
    </div>
  );
}
