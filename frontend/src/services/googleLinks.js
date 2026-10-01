/**
 * Google links for a lead: search (knowledge panel with photos, menu, reviews)
 * and Maps (the exact place page when the scraper captured it).
 */
export function getGoogleLinks(lead) {
  const query = encodeURIComponent(`${lead.business_name} ${lead.location}`);
  const placeUrl = lead.source_urls?.find((url) => url.includes("/maps/place/"));
  return {
    search: `https://www.google.com/search?q=${query}`,
    maps: placeUrl || `https://www.google.com/maps/search/?api=1&query=${query}`,
  };
}
