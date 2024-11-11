import React from "react";

export const CircularProgress = ({ total = 0 }) => {
  const radius = 50;
  const circumference = 2 * Math.PI * radius;
  const progress = ((100 - total) / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <h3 className="text-lg font-medium mb-4">Circular Progress</h3>
      <div className="relative">
        <svg width="120" height="120" className="transform -rotate-90">
          <circle
            className="text-gray-200"
            strokeWidth="10"
            stroke="currentColor"
            fill="transparent"
            r={radius}
            cx="60"
            cy="60"
          />
          <circle
            className="text-blue-600"
            strokeWidth="10"
            strokeDasharray={circumference}
            strokeDashoffset={progress}
            strokeLinecap="round"
            stroke="currentColor"
            fill="transparent"
            r={radius}
            cx="60"
            cy="60"
          />
        </svg>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <span className="text-2xl font-bold">{total}%</span>
        </div>
      </div>
    </div>
  );
};

export const BarProgress = ({ total = 0 }) => {
  return (
    <div className="flex flex-col items-center">
      <h3 className="text-lg font-medium mb-4">Bar Progress</h3>
      <div className="w-48">
        <div className="relative pt-1">
          <div className="overflow-hidden h-4 text-xs flex rounded bg-gray-200">
            <div
              style={{ width: `${total}%` }}
              className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-600 transition-all duration-500"
            />
          </div>
          <div className="text-center mt-2">
            <span className="text-lg font-semibold">{total}%</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export const LinearProgress = ({ total = 0 }) => {
  return (
    <div className="flex flex-col items-center">
      <h3 className="text-lg font-medium mb-4">Linear Progress</h3>
      <div className="w-48">
        <svg width="100%" height="8" className="mb-2">
          <defs>
            <pattern
              id="progress-pattern"
              x="0"
              y="0"
              width="8"
              height="8"
              patternUnits="userSpaceOnUse"
            >
              <circle
                cx="4"
                cy="4"
                r="2"
                fill="currentColor"
                className="text-blue-600"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="#f3f4f6" rx="4" />
          <rect
            width={`${total}%`}
            height="100%"
            fill="url(#progress-pattern)"
            rx="4"
          />
        </svg>
        <div className="text-center">
          <span className="text-lg font-semibold">{total}%</span>
        </div>
      </div>
    </div>
  );
};
