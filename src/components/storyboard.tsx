import { StoryboardAsset } from "@/lib/mock";
import React from "react";
import { FiGrid } from "react-icons/fi";
import Metrics from "./metrics";
import { FaRegEyeSlash } from "react-icons/fa";

interface StoryboardProps {
  asset: StoryboardAsset;
}

const Storyboard = ({ asset }: StoryboardProps) => (
  <div>
    {asset.accessable ? (
      <>
        <div className="bg-lightblue w-max mx-auto p-2 rounded text-center">
          <FiGrid className="w-[40px] h-[40px]" />
        </div>
        <p className="text-2xl items-center	flex justify-center">
          <span className="font-bold">{asset.title}</span>
          <span className="text-sm mx-1 bg-lightblue px-[5px] rounded">
            storyboard
          </span>
        </p>
        <p className="text-center mt-4">{asset.description}</p>

        <div className="grid grid-cols-2 my-3">
          <Metrics
            className="border-r-2 border-solid border-lightblue"
            data={asset.applicabeAffiliates.length}
            label="No of Applicable Affilates"
          />
          <Metrics data={asset.coupledKpi.length} label="No of Coupled KPI" />
        </div>
      </>
    ) : (
      <div className="h-[300px] flex flex-col justify-center items-center">
        <FaRegEyeSlash />
        <p>You have to accees to this resource</p>
        <button className="bg-black text-white font-bold py-2 w-[100%] rounded mt-4 flex items-center justify-center gap-2">
          Request Access
        </button>
      </div>
    )}
  </div>
);

export default Storyboard;
