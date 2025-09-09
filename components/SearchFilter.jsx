import React, { useState } from 'react';
import Input from './Input';
import Button from './Button';

const SearchFilter = ({ 
  searchParams, 
  setSearchParams, 
  onSearch, 
  onAdvancedSearch, 
  onReset, 
  loading 
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleInputChange = (field, value) => {
    setSearchParams(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleBasicSearch = (e) => {
    e.preventDefault();
    onSearch();
  };

  const handleAdvancedSearchSubmit = (e) => {
    e.preventDefault();
    onAdvancedSearch();
  };

  const handleReset = () => {
    setSearchParams({
      search: '',
      eventType: '',
      minPrice: '',
      maxPrice: '',
      location: '',
      ticketType: '',
      isNegotiable: ''
    });
    setShowAdvanced(false);
    onReset();
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Basic Search */}
      <form onSubmit={handleBasicSearch} className="mb-4">
        <div className="flex space-x-4">
          <div className="flex-1">
            <Input
              type="text"
              placeholder="Tìm kiếm vé theo tên sự kiện..."
              value={searchParams.search}
              onChange={(e) => handleInputChange('search', e.target.value)}
            />
          </div>
          <Button
            type="submit"
            disabled={loading}
            className="px-6"
          >
            {loading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Đang tìm...
              </div>
            ) : (
              'Tìm kiếm'
            )}
          </Button>
        </div>
      </form>

      {/* Toggle Advanced Search */}
      <div className="flex justify-between items-center mb-4">
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          {showAdvanced ? '▲ Ẩn tìm kiếm nâng cao' : '▼ Tìm kiếm nâng cao'}
        </button>
        
        <button
          type="button"
          onClick={handleReset}
          className="text-gray-600 hover:text-gray-800 text-sm font-medium"
        >
          Xóa bộ lọc
        </button>
      </div>

      {/* Advanced Search */}
      {showAdvanced && (
        <form onSubmit={handleAdvancedSearchSubmit} className="border-t pt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            {/* Price Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Giá từ (VNĐ)
              </label>
              <Input
                type="number"
                placeholder="0"
                min="0"
                value={searchParams.minPrice}
                onChange={(e) => handleInputChange('minPrice', e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Giá đến (VNĐ)
              </label>
              <Input
                type="number"
                placeholder="1000000"
                min="0"
                value={searchParams.maxPrice}
                onChange={(e) => handleInputChange('maxPrice', e.target.value)}
              />
            </div>

            {/* Event Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Loại sự kiện
              </label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchParams.eventType}
                onChange={(e) => handleInputChange('eventType', e.target.value)}
              >
                <option value="">Tất cả</option>
                <option value="Concert">Concert</option>
                <option value="Sports">Thể thao</option>
                <option value="Theater">Sân khấu</option>
                <option value="Conference">Hội nghị</option>
                <option value="Other">Khác</option>
              </select>
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Địa điểm
              </label>
              <Input
                type="text"
                placeholder="Nhập địa điểm..."
                value={searchParams.location}
                onChange={(e) => handleInputChange('location', e.target.value)}
              />
            </div>

            {/* Ticket Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Loại vé
              </label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchParams.ticketType}
                onChange={(e) => handleInputChange('ticketType', e.target.value)}
              >
                <option value="">Tất cả</option>
                <option value="VIP">VIP</option>
                <option value="Premium">Premium</option>
                <option value="Standard">Standard</option>
                <option value="Economy">Economy</option>
              </select>
            </div>

            {/* Is Negotiable */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Có thể thương lượng
              </label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchParams.isNegotiable}
                onChange={(e) => handleInputChange('isNegotiable', e.target.value)}
              >
                <option value="">Tất cả</option>
                <option value="true">Có thể thương lượng</option>
                <option value="false">Giá cố định</option>
              </select>
            </div>
          </div>

          <div className="flex space-x-4">
            <Button
              type="submit"
              disabled={loading}
            >
              {loading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Đang tìm...
                </div>
              ) : (
                'Áp dụng bộ lọc'
              )}
            </Button>
          </div>
        </form>
      )}
    </div>
  );
};

export default SearchFilter;
