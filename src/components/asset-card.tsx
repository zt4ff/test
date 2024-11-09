import { Asset } from "@/lib/mock";

interface AssetCardProps {
  asset: Asset;
}

const AssetCard = ({ asset }: AssetCardProps) => {
  return (
    <div className="p-4 border rounded-lg hover:border-blue-500 transition-colors">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-medium">{asset.title}</h3>
          <p className="text-sm text-gray-600">{asset.description}</p>
        </div>
        <span className="text-sm text-blue-600 bg-blue-50 px-2 py-1 rounded">
          {asset.type}
        </span>
      </div>
      <div className="text-sm text-gray-500 mt-2">{asset.date}</div>
    </div>
  );
};

export default AssetCard;
