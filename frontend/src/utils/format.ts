export function formatCurrency(
  value: number,
  currency = "USD",
  locale = navigator.language,
): string {
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
  }).format(value);
}

export function formatDate(
  dateString: string,
  locale = navigator.language,
): string {
  return new Date(dateString).toLocaleDateString(locale);
}
