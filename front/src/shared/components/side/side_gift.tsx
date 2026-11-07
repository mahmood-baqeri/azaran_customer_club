import React, { useState } from 'react';

interface Props {
  onApply: (filters: { min: string, max: string }) => void;
}

const GiftSide: React.FC<Props> = ({ onApply }) => {
  const [max, setMax] = useState('10000');
  const [min, setMin] = useState('1');

  const handleApply = () => {
    onApply({ min , max });
  };

  return (
    <div
      className="offcanvas offcanvas-start suha-filter-offcanvas-wrap p-3"
      id="side_gift_filter_element"
      aria-labelledby="suhaFilterOffcanvasLabel"
    >
      <button className="btn-close text-reset" type="button" data-bs-dismiss="offcanvas" aria-label="Close"></button>
      <div className="offcanvas-body p-0 pt-5">
        <div className="container">
          <div className="row">

            <div className="col-12">
              <div className="widget price-range mb-4">
                <h6 className="widget-title mb-4">محدوده قیمت</h6>
                <div className="widget-desc">
                  <div className="row g-2">
                    <div className="col-12">
                      <div className="form-floating">
                        <input className="form-control" id="floatingInput" type="number" value={min} onChange={e => setMin(e.target.value)} />
                        <label>حداقل</label>
                      </div>
                    </div>
                    <div className="col-12">
                      <div className="form-floating">
                        <input className="form-control" id="floatingInput" type="number" value={max} onChange={e => setMax(e.target.value)} />
                        <label>حداکثر</label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="col-12">
              <div className="apply-filter-btn">
                <button
                  onClick={handleApply}
                  className="btn btn-lg btn-info w-100"
                  data-bs-dismiss="offcanvas"
                >
                  اعمال
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GiftSide;
