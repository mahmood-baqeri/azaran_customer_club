//  src/shared/utils/currency.ts

export function currency(price: number): string {
  return new Intl.NumberFormat("fa-IR").format(price);
}

export function convertToCurrency(
  values: (string | number | null | undefined)[],
  action: "sum" | "sub" | "mul" | "div"
): string {
  const numbers = values
    .filter((v) => v !== null && v !== undefined && v !== "" && !isNaN(Number(v)))
    .map((v) => Number(v));
  let result = 0;
  switch (action) {
    case "sum":
      result = numbers.reduce((a, b) => a + b, 0);
      break;
    case "sub":
      result = numbers.reduce((a, b) => a - b);
      break;
    case "mul":
      result = numbers.reduce((a, b) => a * b, 1);
      break;
    case "div":
      result = numbers.reduce((a, b) => a / b);
      break;
  }
  return result.toLocaleString();
}

export function robustIntegerDivide(a: unknown, b: unknown): number | null {
  if (a == null || b == null) return null;
  const numA = Number(a);
  const numB = Number(b);
  if (isNaN(numA) || isNaN(numB) || numB === 0) return null;
  return Math.floor(numA / numB);
}