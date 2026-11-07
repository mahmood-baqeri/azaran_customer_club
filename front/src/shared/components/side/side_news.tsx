import React, { useState } from 'react';
import { PersianDatePicker } from '../../shared/utils/persianDatePicker';
import { formatDateToYMD } from '../../utils/functions';


interface TheProps {
    onApply: (filters: { start: string | null; end: string | null; title: string | null }) => void;
}

const FilterNews: React.FC<TheProps> = ({ onApply }) => {
    const [startDate, setStartDate] = useState<string | null>(null);
    const [endDate, setEndDate] = useState<string | null>(null);
    const [title, setTitle] = useState("");

    const handleApply = () => {
        onApply({ start: startDate, end: endDate, title: title });
    };

    const handleStartDate = (miladiDate: Date | null) => {
        if (miladiDate) {
            setStartDate(formatDateToYMD(miladiDate));
        }
    };

    const handleEndDate = (miladiDate: Date | null) => {
        if (miladiDate) {
            setEndDate(formatDateToYMD(miladiDate));
        }
    };

    return (
        <div
            className="offcanvas offcanvas-start suha-filter-offcanvas-wrap p-3"
            id="side_date_filter_element"
            aria-labelledby="side_date_filter_elementLabel"
        >
            <button className="btn-close text-reset" type="button" data-bs-dismiss="offcanvas" aria-label="Close"></button>
            <div className="offcanvas-body p-0 pt-5">
                <div className="container">
                    <div className="row">
                        <div className="col-12">
                            <div className="widget price-range mb-4">
                                <h6 className="widget-title mb-2">جستجو</h6>
                                <br />
                                <div className="widget-desc">
                                    <div className="row g-2">
                                        <div className="col-12">
                                            <p className='m-0'>عنوان</p>
                                            <input className="form-control" type="text" placeholder="عنوان" value={title} onChange={e => setTitle(e.target.value)} />
                                        </div>
                                        <div className="col-12 mt-4">
                                            <p className='m-0'>تاریخ شروع</p>
                                            <PersianDatePicker onChange={handleStartDate} />
                                        </div>
                                        <div className="col-12 mt-4">
                                            <p className='m-0'>تاریخ پایان</p>
                                            <PersianDatePicker onChange={handleEndDate} />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="col-12">
                            <div className="apply-filter-btn">
                                <button onClick={handleApply} className="btn btn-info btn-lg w-100" data-bs-dismiss="offcanvas">
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

export default FilterNews;
