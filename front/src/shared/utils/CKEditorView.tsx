import { memo, useMemo } from "react";
import DOMPurify from "dompurify";

export const CKEditorView = memo(function CKEditorView({
     content,
}: {
     content: string;
}) {
     const clean = useMemo(() => DOMPurify.sanitize(content), [content]);
     return (
          <div
               className="prose max-w-none"
               dangerouslySetInnerHTML={{ __html: clean }}
          />
     );
});


// export function CKEditorView({ content }: { content: string }) {
//     const clean = DOMPurify.sanitize(content);

//     return (
//         <div
//             className="prose max-w-none"
//             dangerouslySetInnerHTML={{ __html: clean }}
//         />
//     );
// }
