import {
  Asset,
  AssetType,
  KPIAsset,
  LayoutAsset,
  StoryboardAsset,
} from "@/lib/mock";
import Modal from "@/components/modal";
import { useState } from "react";
import Storyboard from "@/components/storyboard";
import KPI from "@/components/kpi";
import Layout from "@/components/layout";
import { TbStar, TbStarOff } from "react-icons/tb";

interface AssetCardProps {
  asset: Asset;
}

const AssetCard = ({ asset }: AssetCardProps) => {
  const [currentAsset, setCurrentAsset] = useState<Asset | null>(null);

  const renderModal = (param: Asset["type"]) => {
    switch (param) {
      case "storyboard":
        return <Storyboard asset={currentAsset as StoryboardAsset} />;
      case "kpi":
        return <KPI asset={currentAsset as KPIAsset} />;
      case "layout":
        return <Layout asset={currentAsset as LayoutAsset} />;
      default:
        return null;
    }
  };

  return (
    <>
      <div
        className="p-4 border rounded-lg hover:border-blue-500 transition-colors cursor-pointer"
        onClick={() => {
          setCurrentAsset(asset);
        }}
      >
        <div className="flex justify-between items-start">
          <div>
            <h3 className="font-medium">{asset.title}</h3>
            <p className="text-sm text-gray-600">{asset.description}</p>
          </div>
          <span className="text-sm text-blue-600 bg-blue-50 px-2 py-1 rounded">
            {AssetType[asset.type]}
          </span>
        </div>
        <div className="flex justify-between items-center mt-3">
          <div className="text-sm text-gray-500">{asset.date}</div>
          {asset?.isFavorite && <TbStar color="black" />}
        </div>
      </div>
      <Modal
        isOpen={!!currentAsset}
        onClose={() => {
          setCurrentAsset(null);
        }}
      >
        {!!currentAsset && renderModal(currentAsset.type)}
      </Modal>
    </>
  );
};

export default AssetCard;
