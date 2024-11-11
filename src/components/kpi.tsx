import { KPIAsset } from "@/lib/mock";
import React from "react";
import { CiBookmark } from "react-icons/ci";
import { FiGrid } from "react-icons/fi";
import { BarProgress, CircularProgress, LinearProgress } from "./charts";


const renderCharts = (param: "bar" | "circular" | "linear", total: number) => {
  switch (param) {
    case "bar":
      return <BarProgress total={total} />;
    case "circular":
      return <CircularProgress total={total} />;
    case "linear":
      return <LinearProgress total={total} />;
    default:
      return null;
  }
};

interface KPIProps {
  asset: KPIAsset;
}

const KPI = ({ asset }: KPIProps) => (
  <div>
    <div className="bg-lightblue w-max mx-auto p-2 rounded text-center">
      <FiGrid className="w-[40px] h-[40px]" />
    </div>
    <p className="text-2xl items-center	flex justify-center">
      <span className="font-bold">{asset.title}</span>
      <span className="text-sm mx-1 bg-lightblue px-[5px] rounded">kpi</span>
    </p>
    <p className="text-center mt-4">{asset.description}</p>

    <div className="flex items-center justify-center mt-2">
      {asset.metricIds.map((metricid) => (
        <div
          key={metricid}
          className="text-sm mx-1 bg-lightblue px-[5px] rounded"
        >
          {metricid}
        </div>
      ))}
    </div>

    <div className="grid grid-cols-3 gap-y-2 mt-4 text-center">
      <div>
        <p>Calculation:</p>
        <p>{asset.calculation}</p>
      </div>
      <div>
        <p>Visuals Available:</p>
        <ul>
          {asset.visualsAvailable.map((item) => (
            <li key={item}>- {item}</li>
          ))}
        </ul>
      </div>
      <div>
        <p>Affiliate Applicability</p>
        <ul>
          {asset.affiliateApplicability.map((item) => (
            <li key={item}>- {item}</li>
          ))}
        </ul>
      </div>
    </div>

    <div className="bg-lightblue my-4 rounded p-2 grid grid-cols-2 gap-2">
      {asset.visualsAvailable.map(item => (<div key={item}>
        {renderCharts(item, asset.calculation)}
      </div>))}
    </div>

    <div className="mt-6">
      <p className="font-bold text-xl mb-2">Business Questions</p>
      <div className="grid grid-cols-2 gap-3">
        {asset.businessQuestions.map((question, index) => (
          <div
            key={question}
            className={`p-2 ${index === 0 ? "bg-lightblue" : ""}`}
          >
            <p className="font-bold">Question {index + 1}</p>
            <p className="font-gray400">{question}</p>
          </div>
        ))}
      </div>
    </div>

    <button className="bg-black text-white font-bold py-2 w-[100%] rounded mt-4 flex items-center justify-center gap-2">
      <CiBookmark />
      Favourite
    </button>
  </div>
);

export default KPI;
