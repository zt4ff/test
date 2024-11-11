import { LayoutAsset } from "@/lib/mock";
import Image from "next/image";
import React from "react";
import { FiGrid } from "react-icons/fi";
import Metrics from "./metrics";
import { CiBookmark } from "react-icons/ci";

interface LayoutProps {
  asset: LayoutAsset;
}

const Layout = ({ asset }: LayoutProps) => (
  <div>
    <div className="bg-lightblue w-max mx-auto p-2 rounded text-center">
      <FiGrid className="w-[40px] h-[40px]" />
    </div>
    <p className="text-2xl items-center	flex justify-center">
      <span className="font-bold">{asset.title}</span>
      <span className="text-sm mx-1 bg-lightblue px-[5px] rounded">layout</span>
    </p>
    <p className="text-center mt-4">{asset.description}</p>

    <div className="grid grid-cols-2 my-3">
      <Metrics
        className="border-r-2 border-solid border-lightblue"
        data={asset.activeKPIs.length}
        label="Amount of KPIs"
      />
      <Metrics data={asset.pageCount} label="Page Counts" />
    </div>

    <div className="h-[300px] w-[100%] relative mt-3">
      <Image className="rounded" src={asset.previewImage} fill alt="preview" />
    </div>

    <button className="bg-black text-white font-bold py-2 w-[100%] rounded mt-4 flex items-center justify-center gap-2">
      <CiBookmark />
      Favourite
    </button>
  </div>
);

export default Layout;
