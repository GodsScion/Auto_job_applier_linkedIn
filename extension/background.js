// Reason: Service worker — required by Manifest V3.
// Relays messages between popup and content script (passthrough).

chrome.runtime.onInstalled.addListener(() => {
  console.log("AutoApply extension installed.");
});
