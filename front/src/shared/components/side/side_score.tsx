import React, { useState } from 'react';

interface Props {
  onApply: (filters: { status: string }) => void;
}

const ScoreSide: React.FC<Props> = ({ onApply }) => {
  const [selectedStatus, setSelectedStatus] = useState('همه');

  const handleApply = () => {
    onApply({ status: selectedStatus });
  };

  const handleChange = (value: string) => {
    setSelectedStatus(value);
  };

  return (
    <div
      className="offcanvas offcanvas-start suha-filter-offcanvas-wrap p-3"
      id="side_score_filter_element"
      aria-labelledby="suhaFilterOffcanvasLabel"
    >
      <button className="btn-close text-reset" type="button" data-bs-dismiss="offcanvas" aria-label="Close"></button>
      <div className="offcanvas-body p-0 pt-5">
        <div className="container">
          <div className="row">
            <div className="col-12">
              <div className="widget catagory mb-4">
                <h6 className="widget-title mb-2">وضعیت</h6>
                <div className="widget-desc">
                  {['همه', 'کسب', 'خرج'].map((label) => (
                    <div className="form-check" key={label}>
                      <input
                        style={{ width: "24px", height: "24px" }}
                        className="form-check-input"
                        type="checkbox"
                        id={`checkbox-${label}`}
                        checked={selectedStatus === label}
                        onChange={() => handleChange(label)}
                      />
                      <label className="form-check-label" htmlFor={`checkbox-${label}`}>
                        {label}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="col-12">
              <div className="apply-filter-btn">
                <button
                  onClick={handleApply}
                  className="btn btn-info btn-lg btn-success w-100"
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

export default ScoreSide;
