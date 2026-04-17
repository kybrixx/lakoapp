# Lako PWA - Progressive Web App Setup Guide

## Overview
Lako is now a fully functional Progressive Web App (PWA) with offline capabilities, installable app experience, and intelligent caching strategies.

## What's Included

### 1. **Service Worker (`sw.js`)**
- Handles offline functionality
- Implements intelligent caching strategies:
  - **API calls**: Network-first with cache fallback
  - **Images**: Cache-first for faster loading
  - **HTML/CSS/JS**: Stale-while-revalidate (fresh from network, serve cached version immediately)
  - **Other assets**: Cache-first, network fallback
- Background sync support
- Cache management messaging

### 2. **Manifest (`manifest.json`)**
- App metadata and branding
- Install prompts configuration
- App shortcuts
- Share target configuration
- Icon definitions (support for maskable icons)

### 3. **PWA Manager (`js/pwa.js`)**
- Service worker registration
- Install prompt handling
- Update notifications
- Offline/online status detection
- Notification permission management
- Cache management utilities

### 4. **Logo (`assets/images/logo.svg`)**
- Skewer + map pointer design
- Black and white color scheme
- Available as SVG (scalable to any size)

## Setup Instructions

### Step 1: Generate PNG Icons from SVG
The app references several PNG logo sizes. Convert the SVG logo to PNG using one of these methods:

**Option A: Online Tool (Recommended - No Dependencies)**
1. Go to [Convertio](https://convertio.co/svg-png/) or [CloudConvert](https://cloudconvert.com/)
2. Upload `/assets/images/logo.svg`
3. Convert to PNG
4. Download and save as:
   - `logo-192.png` (192x192px)
   - `logo-512.png` (512x512px)
   - `logo-maskable-192.png` (192x192px)
   - `logo-maskable-512.png` (512x512px)
   - `logo-96.png` (96x96px) - for shortcuts

Save these to `/frontend/assets/images/`

**Option B: Using ImageMagick (if available)**
```bash
convert logo.svg -resize 192x192 logo-192.png
convert logo.svg -resize 512x512 logo-512.png
convert logo.svg -resize 96x96 logo-96.png
```

**Option C: Using Node.js + svg-to-png (minimal setup)**
```bash
npm install svg-to-png
# Then use it to convert the SVG files
```

### Step 2: Optional - Create Screenshots
Add app screenshots for the PWA (referenced in manifest):
- Create `assets/images/screenshot-1.png` (540x720 - mobile view)
- Create `assets/images/screenshot-2.png` (1280x720 - desktop view)

These are nice-to-have but not required for offline functionality.

### Step 3: Serve Over HTTPS (Production)
PWA features require HTTPS in production:
- Service workers only work over HTTPS (or localhost for development)
- Update manifest.json if you change your domain
- Ensure `start_url` matches your deployment URL

### Step 4: Test Locally
```bash
# Serve the frontend locally
cd frontend
python -m http.server 8080

# Visit http://localhost:8080
# Open DevTools → Application → Service Workers to verify registration
```

## Features

### Offline Support
- ✅ Browse cached vendors even without internet
- ✅ View cached products and posts
- ✅ Access offline when service worker is active
- ✅ Automatic sync when back online

### Installability
- ✅ Add to home screen on mobile
- ✅ Install as standalone app on desktop
- ✅ Appears in app drawer
- ✅ Full-screen immersive experience

### Caching Strategies
```
API Calls         → Network → Cache → Offline JSON
Images            → Cache → Network (faster loading)
HTML/CSS/JS       → Cache → Network (stale-while-revalidate)
Other Assets      → Cache → Network
```

### App Shortcuts (Mobile/Desktop)
Users can access common features directly:
- Browse Vendors
- View Map
- Get Suggestions

## Cache Management

### Clear Cache
Users can manage cache from settings:
```javascript
// Clear all cached data
pwa.clearCache();
```

### Cache Size
Check storage usage:
```javascript
// Get cache size info
pwa.getCacheSize().then(estimate => {
  console.log('Usage:', estimate.usage);
  console.log('Quota:', estimate.quota);
});
```

### Notification Permissions
The app requests notification permission for update alerts:
```javascript
// Request permission
pwa.requestNotificationPermission();
```

## Browser Support

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Service Workers | ✅ | ✅ | ⚠️ (11.1+) | ✅ |
| Web App Manifest | ✅ | ✅ | ⚠️ (partial) | ✅ |
| Add to Home Screen | ✅ | ✅ | ✅ | ✅ |
| Offline Support | ✅ | ✅ | ⚠️ (limited) | ✅ |

## File Structure

```
/frontend
├── manifest.json                 # PWA metadata
├── sw.js                         # Service worker
├── index.html                    # Updated with PWA meta tags
├── js/
│   ├── pwa.js                   # PWA manager
│   └── sync.js                  # Cache service (updated)
├── pages/
│   ├── register.html            # Updated with manifest
│   ├── guest/browse.html        # Updated with manifest
│   └── ...
└── assets/images/
    ├── logo.svg                 # Skewer logo (scalable)
    ├── logo-192.png             # (generate from SVG)
    ├── logo-512.png             # (generate from SVG)
    └── ...
```

## Updating the App

### Version Updates
1. Modify any cached assets
2. Update `CACHE_NAME` in `sw.js`:
   ```javascript
   const CACHE_NAME = 'lako-v2';  // Increment version
   ```
3. Service worker automatically invalidates old caches
4. Users see update notification

### Manual Update Check
```javascript
// Force check for updates
if (pwa.registration) {
  pwa.registration.update();
}
```

## Troubleshooting

### Service Worker Not Registering
- Check browser console for errors
- Verify HTTPS or localhost
- Clear browser cache and restart
- Check if service worker file is accessible

### Offline Features Not Working
- Verify service worker is active (DevTools → Application)
- Check network tab for cached responses
- Ensure `localDB` is initialized
- Clear cache and re-register

### Icons Not Showing
- Verify PNG files exist in `assets/images/`
- Check file permissions
- Ensure correct naming convention
- Verify manifest.json paths

### App Not Installable
- HTTPS required (production)
- Valid manifest.json required
- Icon sizes must match manifest
- Start URL must be valid

## Performance Tips

1. **Cache Sizings**: Adjust TTL values in `sync.js`
2. **Image Optimization**: Use WebP format for better compression
3. **Code Splitting**: Load vendor/customer code separately
4. **Pre-caching**: Add critical routes to `ASSETS_TO_CACHE`

## Security

- Service worker only runs over HTTPS (production)
- Manifest content is cryptographically verified
- Cache only stores from same origin
- Sensitive data not cached (handled by server)

## References

- [MDN - Progressive Web Apps](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Web App Manifest Spec](https://www.w3.org/TR/appmanifest/)
- [Service Workers API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Microsoft Edge PWA Documentation](https://learn.microsoft.com/en-us/microsoft-edge/progressive-web-apps-chromium/)

## License

Same as Lako application
