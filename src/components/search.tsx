import React, { FC } from "react";
import { FaSearch } from "react-icons/fa";

interface SearchProps extends React.InputHTMLAttributes<HTMLInputElement> {
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const Search: FC<SearchProps> = ({ onChange, className, ...props }) => (
  <div
    className={`flex items-center border-[2px] border-[#eef1f5] rounded px-3 py-3 bg-white ${className}`}
  >
    <FaSearch className="mr-2" />
    <input
      type="text"
      className="flex-1 outline-none text-gray-700"
      onChange={onChange}
      {...props}
    />
  </div>
);

export default Search;