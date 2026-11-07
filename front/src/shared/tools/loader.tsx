
export const Loader = () => (
  <div className="spinner-grow spinner-grow-sm text-light me-2" role="status">
    <span className="visually-hidden">Loading...</span>
  </div>
);

export const Loader__2 = () => (
  <div className="d-flex justify-content-center align-items-center h__400">
    <div className="spinner-border text-success" role="status">
      <span className="visually-hidden">در حال بارگذاری...</span>
    </div>
  </div>
);


export default function Preloader() {
  return (
    <div className="preloader" id="preloader">
      <div className="spinner-grow text-secondary" role="status">
        <div className="sr-only"></div>
      </div>
    </div>
  );
}