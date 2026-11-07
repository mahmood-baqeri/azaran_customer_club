// حذف declare const bootstrap: any;

import { Offcanvas } from "bootstrap";

export const closeOffcanvas = (id: string) => {
    const offcanvasElement = document.getElementById(id);
    if (offcanvasElement) {
        const bsOffcanvas = Offcanvas.getInstance(offcanvasElement)
            || new Offcanvas(offcanvasElement);
        bsOffcanvas.hide();
    }
};

export function switchCanvas(modelID: string, mode: "show" | "close") {
    const theModalEl = document.getElementById(modelID);
    if (!theModalEl) return;

    let bsOffcanvas = Offcanvas.getInstance(theModalEl);
    if (!bsOffcanvas) {
        bsOffcanvas = new Offcanvas(theModalEl);
    }

    if (mode === "show") {
        bsOffcanvas.show();
    } else {
        bsOffcanvas.hide();
    }
}

