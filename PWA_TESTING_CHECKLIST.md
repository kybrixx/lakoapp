# PWA Testing Checklist

Use this checklist to verify your PWA is working correctly.

## Prerequisites
- [ ] PNG logos created (192x192, 512x512, etc. in `assets/images/`)
- [ ] Backend API server running (if testing offline)
- [ ] Frontend served over HTTP (localhost) or HTTPS

## Installation Test

### Desktop (Chrome/Edge)
- [ ] Visit `http://localhost:8080` or your domain
- [ ] Click install icon in address bar (or menu → Install app)
- [ ] App opens in standalone window
- [ ] App has correct title and icon
- [ ] Can access app from applications menu

### Mobile (Android Chrome)
- [ ] Visit URL on phone
- [ ] Tap menu → Install app
- [ ] App appears on home screen
- [ ] App icon is correct (your skewer logo)
- [ ] Can launch as standalone app

### Mobile (iOS Safari 11.3+)
- [ ] Visit URL in Safari
- [ ] Tap Share → Add to Home Screen
- [ ] App appears on home screen
- [ ] Can launch from home screen

## Service Worker Test

### Check Service Worker Registration
- [ ] Open DevTools (F12)
- [ ] Go to Application tab
- [ ] Click Service Workers
- [ ] Verify status: `Active and running`
- [ ] Scope shows: `/`

### Check Caching
- [ ] Go to Application → Cache Storage
- [ ] Verify these caches exist:
  - [ ] `lako-v1` (main app shell)
  - [ ] `lako-runtime-v1` (runtime assets)
  - [ ] `lako-images-v1` (images)
  - [ ] `lako-api-v1` (API responses)

### View Cached Files
- [ ] Expand `lako-v1` cache
- [ ] Verify these are cached:
  - [ ] `index.html`
  - [ ] CSS files
  - [ ] JS files
  - [ ] Images

## Offline Functionality Test

### Go Offline
1. [ ] DevTools → Network tab
2. [ ] Check "Offline" checkbox
3. [ ] Close DevTools
4. [ ] Reload page (Ctrl+R)

### Verify Offline Experience
- [ ] Page loads completely
- [ ] Layout looks normal
- [ ] Images display
- [ ] Previous cached data shows (vendors, products, etc.)
- [ ] Can navigate between cached pages
- [ ] No 404 or connection errors in console

### Perform Offline Actions
- [ ] Try browsing vendors (should show cached list)
- [ ] Try viewing cached products
- [ ] Try accessing settings (cached data)
- [ ] Try navigating to different tabs

### Go Back Online
1. [ ] Uncheck "Offline" in DevTools
2. [ ] Refresh page or try to load new data
3. [ ] Data updates from server
4. [ ] New data gets cached

## Cache Management Test

### Check Cache Size (DevTools)
- [ ] Application → Storage
- [ ] Check "Persistent Storage"
- [ ] View estimated vs quota

### Clear Cache from Settings
- [ ] Navigate to Settings → Cache & Storage
- [ ] Click "Clear Cache"
- [ ] Verify cache is cleared (DevTools → Cache Storage should be empty)
- [ ] Can reload and cache rebuilds

## Manifest Test

### Check Manifest Loading
- [ ] DevTools → Network tab
- [ ] Load page
- [ ] Search for `manifest.json` in requests
- [ ] Should be cached with 200 status

### Verify Manifest Contents
- [ ] DevTools → Application → Manifest
- [ ] Check these fields exist:
  - [ ] App name: "Lako - Local Street Food Market"
  - [ ] Short name: "Lako"
  - [ ] Icons: Show correct paths and sizes
  - [ ] Start URL: "/"
  - [ ] Display: "standalone"
  - [ ] Theme color: "#0f5c2f"

## Update Test

### Verify Update Detection
- [ ] Open app twice (in separate windows)
- [ ] Manually update `CACHE_NAME` in `sw.js` (e.g., `lako-v2`)
- [ ] In second window, trigger update check:
  ```javascript
  pwa.registration.update()
  ```
- [ ] Should see update notification (if permissions granted)

### Manual Cache Clear
- [ ] Open DevTools Console
- [ ] Run: `pwa.clearCache()`
- [ ] All caches should be deleted
- [ ] Refresh page to rebuild cache

## Performance Test

### Check Loading Speed
- [ ] DevTools → Network tab
- [ ] Throttle to "Slow 3G"
- [ ] Refresh page
- [ ] Page should load faster than without cache
- [ ] Should not timeout

### Monitor Cache Hit Rate
- [ ] Open Network tab
- [ ] Look at "Size" column
- [ ] Cached items show `(from cache)` or `(from service worker)`
- [ ] Most static assets should be cached

## Browser Compatibility Test

### Browsers to Test (if available)
- [ ] Chrome 40+
- [ ] Firefox 44+
- [ ] Safari 11.3+ (limited PWA support)
- [ ] Edge 79+
- [ ] Opera 27+
- [ ] Mobile Chrome
- [ ] Mobile Firefox

## Security Test

### Verify HTTPS (Production Only)
- [ ] Check browser shows lock icon
- [ ] No mixed content warnings
- [ ] ServiceWorkers section shows green status

### Check Origin Restrictions
- [ ] Service worker only affects same origin
- [ ] Cross-origin assets not cached inappropriately
- [ ] No sensitive data in cache storage

## Notifications Test (Optional)

### Request Permission
1. [ ] DevTools Console: `pwa.requestNotificationPermission()`
2. [ ] Click Allow
3. [ ] DevTools Console: `pwa.showNotification('Test', 'This is a test')`
4. [ ] Notification should appear

## Troubleshooting Issues

### Service Worker Not Registering
- [ ] ✓ Served over HTTPS or localhost only
- [ ] ✓ Clear all caches and browser data
- [ ] ✓ Check console for errors
- [ ] ✓ Verify `sw.js` exists at root

### Offline Not Working
- [ ] ✓ Service worker is active (DevTools)
- [ ] ✓ Caches are populated
- [ ] ✓ Check cache content isn't corrupted
- [ ] ✓ Try hard refresh (Ctrl+Shift+R)

### Icons Not Showing
- [ ] ✓ PNG files exist in `assets/images/`
- [ ] ✓ File names match manifest.json exactly
- [ ] ✓ Images are valid PNG files (not corrupted)
- [ ] ✓ Correct file permissions (readable)

### Cache Getting Too Large
- [ ] Limit API cache TTL in `sync.js`
- [ ] Implement cache size limits
- [ ] Clear old versions from manifest

## Final Verification

- [ ] ✅ Service worker active
- [ ] ✅ App installs successfully
- [ ] ✅ Works offline completely
- [ ] ✅ Cache management working
- [ ] ✅ Manifest loading
- [ ] ✅ Icons displaying correctly
- [ ] ✅ Performance is acceptable
- [ ] ✅ No console errors
- [ ] ✅ Update detection working
- [ ] ✅ Multiple browsers tested

## Sign-Off

When all tests pass, PWA is ready for production! 🚀

Date Tested: ________________
Tester Name: ________________
Browser/Device: ________________
Notes: ________________________________________________
