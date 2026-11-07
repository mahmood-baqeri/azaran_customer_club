// src/modules/faq_module/components/CategoryPills.tsx
import type { Category } from "../interface/faq.types";

interface Props {
     categories: Category[];
     selectedId?: number;
     onSelect: (id?: number) => void;
}

export default function CategoryPills({ categories, selectedId, onSelect }: Props) {
     return (
          <div className="faq-categories-wrapper">
               <button
                    className={`faq-pill ${!selectedId ? "active" : ""}`}
                    onClick={() => onSelect(undefined)}
               >
                    همه
               </button>
               {categories.map((c) => (
                    <button
                         key={c.id}
                         className={`faq-pill ${selectedId === c.id ? "active" : ""}`}
                         onClick={() => onSelect(c.id)}
                    >
                         {c.title}
                    </button>
               ))}
          </div>
     );
}